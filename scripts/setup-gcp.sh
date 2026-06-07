#!/usr/bin/env bash
#
# One-time GCP setup for the GitHub Actions -> Cloud Build -> Cloud Run pipeline.
#
# Provisions, idempotently:
#   * Required APIs
#   * Artifact Registry (Docker) repository
#   * Three least-privilege service accounts (runtime / build-runner / deployer)
#   * All IAM bindings between them
#   * Secret Manager secret for the NVIDIA API key
#   * Workload Identity Federation pool + provider, scoped to THIS GitHub repo
#
# Run with Owner (or sufficient IAM) on the project:
#   ./scripts/setup-gcp.sh
#
# Override any default via environment variable, e.g.:
#   PROJECT_ID=my-proj REGION=europe-west1 ./scripts/setup-gcp.sh

set -euo pipefail

# ----------------------------- Configuration --------------------------------
PROJECT_ID="${PROJECT_ID:-genaiguruyoutube}"
REGION="${REGION:-us-central1}"
GITHUB_REPO="${GITHUB_REPO:-Yash-Kavaiya/NV-DataGenerator}" # owner/repo

AR_REPO="${AR_REPO:-nv-data-generator}"
BACKEND_SERVICE="${BACKEND_SERVICE:-nv-data-generator-backend}"
FRONTEND_SERVICE="${FRONTEND_SERVICE:-nv-data-generator-frontend}"
NVIDIA_SECRET="${NVIDIA_SECRET:-nvidia-api-key}"

RUNTIME_SA_NAME="${RUNTIME_SA_NAME:-nv-data-generator-run}"
BUILD_RUNNER_SA_NAME="${BUILD_RUNNER_SA_NAME:-cloud-build-runner}"
DEPLOYER_SA_NAME="${DEPLOYER_SA_NAME:-github-deployer}"

WIF_POOL_ID="${WIF_POOL_ID:-github-pool}"
WIF_PROVIDER_ID="${WIF_PROVIDER_ID:-github-provider}"

# ----------------------------- Derived values -------------------------------
RUNTIME_SA="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_RUNNER_SA="${BUILD_RUNNER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
DEPLOYER_SA="${DEPLOYER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==> Project: ${PROJECT_ID} | Region: ${REGION} | Repo: ${GITHUB_REPO}"
gcloud config set project "${PROJECT_ID}" >/dev/null

PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
echo "==> Project number: ${PROJECT_NUMBER}"

# ----------------------------- Enable APIs ----------------------------------
echo "==> Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com

# --------------------------- Artifact Registry ------------------------------
echo "==> Ensuring Artifact Registry repo '${AR_REPO}'..."
if ! gcloud artifacts repositories describe "${AR_REPO}" --location="${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${AR_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Images for NV-DataGenerator (Cloud Run)"
else
  echo "    already exists."
fi

# --------------------------- Service accounts -------------------------------
create_sa() {
  local name="$1" display="$2" email="$3"
  if ! gcloud iam service-accounts describe "${email}" >/dev/null 2>&1; then
    gcloud iam service-accounts create "${name}" --display-name="${display}"
  else
    echo "    SA ${email} already exists."
  fi
}
echo "==> Ensuring service accounts..."
create_sa "${RUNTIME_SA_NAME}"      "Cloud Run runtime (NV-DataGenerator)" "${RUNTIME_SA}"
create_sa "${BUILD_RUNNER_SA_NAME}" "Cloud Build runner"                   "${BUILD_RUNNER_SA}"
create_sa "${DEPLOYER_SA_NAME}"     "GitHub Actions deployer (WIF)"        "${DEPLOYER_SA}"

# ------------------------------ Project IAM ---------------------------------
grant_project() {
  local member="$1" role="$2"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="${member}" --role="${role}" --condition=None >/dev/null
}
echo "==> Granting project-level roles..."
# Deployer (impersonated by GitHub): submit builds, stage source, read logs.
grant_project "serviceAccount:${DEPLOYER_SA}" "roles/cloudbuild.builds.editor"
grant_project "serviceAccount:${DEPLOYER_SA}" "roles/storage.admin"
grant_project "serviceAccount:${DEPLOYER_SA}" "roles/logging.viewer"
# Build runner (executes the build): push images, deploy Run, read source, log.
grant_project "serviceAccount:${BUILD_RUNNER_SA}" "roles/artifactregistry.writer"
grant_project "serviceAccount:${BUILD_RUNNER_SA}" "roles/run.admin"
grant_project "serviceAccount:${BUILD_RUNNER_SA}" "roles/storage.objectViewer"
grant_project "serviceAccount:${BUILD_RUNNER_SA}" "roles/logging.logWriter"

# --------------------------- Service-account IAM ----------------------------
echo "==> Granting service-account impersonation (actAs) chains..."
# Deployer may run builds AS the build runner.
gcloud iam service-accounts add-iam-policy-binding "${BUILD_RUNNER_SA}" \
  --member="serviceAccount:${DEPLOYER_SA}" \
  --role="roles/iam.serviceAccountUser" >/dev/null
# Build runner may deploy Cloud Run services AS the runtime SA.
gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA}" \
  --member="serviceAccount:${BUILD_RUNNER_SA}" \
  --role="roles/iam.serviceAccountUser" >/dev/null

# ----------------------------- Secret Manager -------------------------------
echo "==> Ensuring secret '${NVIDIA_SECRET}'..."
if ! gcloud secrets describe "${NVIDIA_SECRET}" >/dev/null 2>&1; then
  gcloud secrets create "${NVIDIA_SECRET}" --replication-policy=automatic
else
  echo "    already exists."
fi
# Runtime SA may read it.
gcloud secrets add-iam-policy-binding "${NVIDIA_SECRET}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/secretmanager.secretAccessor" >/dev/null

# Add a secret value if none exists yet.
if ! gcloud secrets versions list "${NVIDIA_SECRET}" --format='value(name)' | grep -q .; then
  read -rsp "Enter NVIDIA_API_KEY value (leave blank to add later): " NV_KEY; echo
  if [ -n "${NV_KEY}" ]; then
    printf '%s' "${NV_KEY}" | gcloud secrets versions add "${NVIDIA_SECRET}" --data-file=-
    echo "    secret version added."
  else
    echo "    skipped — add later with: printf '%s' KEY | gcloud secrets versions add ${NVIDIA_SECRET} --data-file=-"
  fi
fi

# ---------------------- Workload Identity Federation ------------------------
echo "==> Ensuring Workload Identity pool/provider..."
if ! gcloud iam workload-identity-pools describe "${WIF_POOL_ID}" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "${WIF_POOL_ID}" \
    --location=global --display-name="GitHub Actions Pool"
else
  echo "    pool exists."
fi

if ! gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER_ID}" \
      --location=global --workload-identity-pool="${WIF_POOL_ID}" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER_ID}" \
    --location=global \
    --workload-identity-pool="${WIF_POOL_ID}" \
    --display-name="GitHub provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository == '${GITHUB_REPO}'"
else
  echo "    provider exists."
fi

# Allow ONLY this repo to impersonate the deployer SA.
gcloud iam service-accounts add-iam-policy-binding "${DEPLOYER_SA}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WIF_POOL_ID}/attribute.repository/${GITHUB_REPO}" >/dev/null

WIF_PROVIDER="$(gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER_ID}" \
  --location=global --workload-identity-pool="${WIF_POOL_ID}" --format='value(name)')"

# ------------------------------- Summary ------------------------------------
cat <<EOF

==================================================================
 Setup complete. Add these as GitHub Actions *Variables*
 (repo Settings -> Secrets and variables -> Actions -> Variables):
==================================================================
  GCP_PROJECT_ID         = ${PROJECT_ID}
  GCP_REGION             = ${REGION}
  WIF_PROVIDER           = ${WIF_PROVIDER}
  DEPLOY_SERVICE_ACCOUNT = ${DEPLOYER_SA}
  BUILD_RUNNER_SA        = ${BUILD_RUNNER_SA}
  RUNTIME_SA_NAME        = ${RUNTIME_SA_NAME}
  AR_REPO                = ${AR_REPO}
  BACKEND_SERVICE        = ${BACKEND_SERVICE}
  FRONTEND_SERVICE       = ${FRONTEND_SERVICE}
  NVIDIA_SECRET          = ${NVIDIA_SECRET}

 Or set them all with the GitHub CLI:

  gh variable set GCP_PROJECT_ID --body "${PROJECT_ID}" --repo ${GITHUB_REPO}
  gh variable set GCP_REGION --body "${REGION}" --repo ${GITHUB_REPO}
  gh variable set WIF_PROVIDER --body "${WIF_PROVIDER}" --repo ${GITHUB_REPO}
  gh variable set DEPLOY_SERVICE_ACCOUNT --body "${DEPLOYER_SA}" --repo ${GITHUB_REPO}
  gh variable set BUILD_RUNNER_SA --body "${BUILD_RUNNER_SA}" --repo ${GITHUB_REPO}
  gh variable set RUNTIME_SA_NAME --body "${RUNTIME_SA_NAME}" --repo ${GITHUB_REPO}
  gh variable set AR_REPO --body "${AR_REPO}" --repo ${GITHUB_REPO}
  gh variable set BACKEND_SERVICE --body "${BACKEND_SERVICE}" --repo ${GITHUB_REPO}
  gh variable set FRONTEND_SERVICE --body "${FRONTEND_SERVICE}" --repo ${GITHUB_REPO}
  gh variable set NVIDIA_SECRET --body "${NVIDIA_SECRET}" --repo ${GITHUB_REPO}
==================================================================
EOF
