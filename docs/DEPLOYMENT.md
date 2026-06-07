# Deployment & CI/CD

End-to-end continuous delivery for NV-DataGenerator:

```
GitHub push to main ─▶ GitHub Actions ─▶ Cloud Build ─▶ Artifact Registry ─▶ Cloud Run
        (OIDC / Workload Identity Federation — no JSON keys)
```

- **GitHub Actions** authenticates to GCP with **Workload Identity Federation** (keyless) and submits the build.
- **Cloud Build** builds both images (with layer caching), pushes them to **Artifact Registry**, and deploys to **Cloud Run**.
- The **backend** deploys first; its URL is injected into the **frontend** so nginx can proxy `/api/v1` to it.
- A post-deploy **smoke test** verifies `/api/v1/health` and frontend reachability before the build is marked green.

## Files

| File | Purpose |
|------|---------|
| [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) | CD: on push to `main`, auth via WIF → `gcloud builds submit` |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | CI: on PRs, typecheck/build frontend, smoke-import backend, build both images |
| [`cloudbuild.yaml`](../cloudbuild.yaml) | Build → push → deploy both Cloud Run services |
| [`scripts/setup-gcp.ps1`](../scripts/setup-gcp.ps1) / [`.sh`](../scripts/setup-gcp.sh) | One-time GCP provisioning (idempotent) |
| [`.gcloudignore`](../.gcloudignore) | Keeps the Cloud Build source upload lean |

## Identity model (least privilege)

Three service accounts, each with the minimum it needs:

| Service account | Used by | Roles |
|-----------------|---------|-------|
| `github-deployer` | GitHub Actions (via WIF) | `cloudbuild.builds.editor`, `storage.admin`, `logging.viewer`, `actAs` on build-runner |
| `cloud-build-runner` | Cloud Build steps | `artifactregistry.writer`, `run.admin`, `storage.objectViewer`, `logging.logWriter`, `actAs` on runtime SA |
| `nv-data-generator-run` | Cloud Run services | `secretmanager.secretAccessor` on `nvidia-api-key` only |

WIF is scoped with an attribute condition (`assertion.repository == 'Yash-Kavaiya/NV-DataGenerator'`) so **only this repo** can impersonate the deployer.

---

## One-time setup

### 1. Provision GCP

From a machine with `gcloud` authenticated as a project Owner:

```powershell
# Windows / PowerShell (defaults target project genaiguruyoutube, us-central1)
./scripts/setup-gcp.ps1
```

```bash
# Linux / macOS / Cloud Shell
chmod +x scripts/setup-gcp.sh
./scripts/setup-gcp.sh
```

The script enables APIs, creates the Artifact Registry repo, the three service
accounts and their IAM bindings, the `nvidia-api-key` secret (it will prompt for
the value), and the Workload Identity pool/provider. It prints the GitHub
variables to set in the next step.

### 2. Add the GitHub Actions variables

Repo → **Settings → Secrets and variables → Actions → Variables** (these are
non-secret — that's the point of WIF). The setup script prints exact values and
ready-to-paste `gh variable set` commands.

| Variable | Example |
|----------|---------|
| `GCP_PROJECT_ID` | `genaiguruyoutube` |
| `GCP_REGION` | `us-central1` |
| `WIF_PROVIDER` | `projects/123.../locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `DEPLOY_SERVICE_ACCOUNT` | `github-deployer@genaiguruyoutube.iam.gserviceaccount.com` |
| `BUILD_RUNNER_SA` | `cloud-build-runner@genaiguruyoutube.iam.gserviceaccount.com` |
| `RUNTIME_SA_NAME` | `nv-data-generator-run` |
| `AR_REPO` | `nv-data-generator` |
| `BACKEND_SERVICE` | `nv-data-generator-backend` |
| `FRONTEND_SERVICE` | `nv-data-generator-frontend` |
| `NVIDIA_SECRET` | `nvidia-api-key` |

> The `deploy` workflow targets a GitHub Environment named `production`. Create it
> (Settings → Environments) — optionally add required reviewers to gate prod deploys.

### 3. Ship it

Push to `main` (or run the workflow manually from the Actions tab). Watch the run,
then the Cloud Build logs it streams. On success the build prints the live URLs.

---

## Day-to-day

- **Deploy:** merge/push to `main` → automatic. Or Actions tab → *Deploy to Cloud Run* → *Run workflow*.
- **PR checks:** open a PR → `CI` runs typecheck, build, and Docker builds.
- **Manual deploy from your laptop** (same pipeline, bypassing GitHub):
  ```bash
  gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_REGION=us-central1,_AR_REPO=nv-data-generator .
  ```

### Rollback

Cloud Run keeps every revision. Roll back instantly without rebuilding:

```bash
gcloud run services update-traffic nv-data-generator-backend \
  --region us-central1 --to-revisions PREVIOUS_REVISION=100
```

List revisions with `gcloud run revisions list --service nv-data-generator-backend --region us-central1`.
Images are also tagged by commit SHA in Artifact Registry, so any past commit is redeployable.

### Rotate the NVIDIA API key

```bash
printf '%s' "NEW_KEY" | gcloud secrets versions add nvidia-api-key --data-file=-
# Redeploy (or wait for next deploy) — the backend mounts :latest.
gcloud run services update nv-data-generator-backend --region us-central1 \
  --update-secrets=NVIDIA_API_KEY=nvidia-api-key:latest
```

---

## Tuning

Override sizing via `--substitutions` (in [`deploy.yml`](../.github/workflows/deploy.yml)
or on a manual submit). Defaults live in [`cloudbuild.yaml`](../cloudbuild.yaml):
`_BACKEND_MEMORY`, `_BACKEND_CPU`, `_BACKEND_TIMEOUT`, `_BACKEND_CONCURRENCY`,
`_BACKEND_MIN_INSTANCES`/`_MAX_INSTANCES`, and the `_FRONTEND_*` equivalents.

The backend runs with `--no-cpu-throttling` so FastAPI `BackgroundTasks`
(generation jobs) keep running after the HTTP response returns.

> **State note:** the backend uses a local SQLite `jobs.db` and a local
> `artifacts/` dir. On Cloud Run these are **ephemeral per instance**. For durable
> job history across revisions/instances, move to Cloud SQL + GCS (future work).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Permission denied` on `builds submit` | Re-run the setup script; confirm the GitHub variables match the printed values. |
| WIF auth fails in Actions | `WIF_PROVIDER` must be the full `projects/NUMBER/.../providers/...` path; the workflow must have `permissions: id-token: write`. |
| Build can't push to Artifact Registry | `cloud-build-runner` needs `artifactregistry.writer` (granted by setup); confirm `AR_REPO`/`_REGION`. |
| Backend boots but 500s on generation | Verify the `nvidia-api-key` secret has a version and the runtime SA has `secretmanager.secretAccessor`. |
| Frontend loads but API calls 502 | `BACKEND_URL` env var on the frontend service must be the backend's `https://...run.app` URL (the pipeline sets this automatically). |
| `logging must not be DEFAULT` | Already handled via `options.logging: CLOUD_LOGGING_ONLY` in `cloudbuild.yaml`. |
