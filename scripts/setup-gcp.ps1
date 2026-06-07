<#
.SYNOPSIS
  One-time GCP setup for the GitHub Actions -> Cloud Build -> Cloud Run pipeline.

.DESCRIPTION
  Idempotently provisions APIs, an Artifact Registry repo, three least-privilege
  service accounts (runtime / build-runner / deployer), IAM bindings, a Secret
  Manager secret for the NVIDIA API key, and Workload Identity Federation scoped
  to this GitHub repo. Run as a project Owner.

.EXAMPLE
  ./scripts/setup-gcp.ps1
  ./scripts/setup-gcp.ps1 -ProjectId my-proj -Region europe-west1
#>
[CmdletBinding()]
param(
  [string]$ProjectId        = "genaiguruyoutube",
  [string]$Region           = "us-central1",
  [string]$GithubRepo       = "Yash-Kavaiya/NV-DataGenerator",
  [string]$ArRepo           = "nv-data-generator",
  [string]$BackendService   = "nv-data-generator-backend",
  [string]$FrontendService  = "nv-data-generator-frontend",
  [string]$NvidiaSecret     = "nvidia-api-key",
  [string]$RuntimeSaName    = "nv-data-generator-run",
  [string]$BuildRunnerSaName= "cloud-build-runner",
  [string]$DeployerSaName   = "github-deployer",
  [string]$WifPoolId        = "github-pool",
  [string]$WifProviderId    = "github-provider"
)

$ErrorActionPreference = "Stop"

$RuntimeSa     = "$RuntimeSaName@$ProjectId.iam.gserviceaccount.com"
$BuildRunnerSa = "$BuildRunnerSaName@$ProjectId.iam.gserviceaccount.com"
$DeployerSa    = "$DeployerSaName@$ProjectId.iam.gserviceaccount.com"

function Exists([string[]]$GcloudArgs) {
  & gcloud @GcloudArgs *> $null
  return ($LASTEXITCODE -eq 0)
}
function Gcloud([string[]]$GcloudArgs) {
  & gcloud @GcloudArgs
  if ($LASTEXITCODE -ne 0) { throw "gcloud $($GcloudArgs -join ' ') failed (exit $LASTEXITCODE)" }
}

Write-Host "==> Project: $ProjectId | Region: $Region | Repo: $GithubRepo" -ForegroundColor Cyan
Gcloud @("config","set","project",$ProjectId)
$ProjectNumber = (& gcloud projects describe $ProjectId --format="value(projectNumber)").Trim()
Write-Host "==> Project number: $ProjectNumber"

Write-Host "==> Enabling APIs..." -ForegroundColor Cyan
Gcloud @("services","enable",
  "run.googleapis.com","cloudbuild.googleapis.com","artifactregistry.googleapis.com",
  "secretmanager.googleapis.com","iam.googleapis.com","iamcredentials.googleapis.com",
  "sts.googleapis.com","cloudresourcemanager.googleapis.com")

Write-Host "==> Ensuring Artifact Registry repo '$ArRepo'..." -ForegroundColor Cyan
if (-not (Exists @("artifacts","repositories","describe",$ArRepo,"--location",$Region))) {
  Gcloud @("artifacts","repositories","create",$ArRepo,"--repository-format=docker",
    "--location",$Region,"--description","Images for NV-DataGenerator (Cloud Run)")
} else { Write-Host "    already exists." }

function New-Sa([string]$Name,[string]$Display,[string]$Email) {
  if (-not (Exists @("iam","service-accounts","describe",$Email))) {
    Gcloud @("iam","service-accounts","create",$Name,"--display-name",$Display)
  } else { Write-Host "    SA $Email already exists." }
}
Write-Host "==> Ensuring service accounts..." -ForegroundColor Cyan
New-Sa $RuntimeSaName     "Cloud Run runtime (NV-DataGenerator)" $RuntimeSa
New-Sa $BuildRunnerSaName "Cloud Build runner"                   $BuildRunnerSa
New-Sa $DeployerSaName    "GitHub Actions deployer (WIF)"        $DeployerSa

function Grant-Project([string]$Member,[string]$Role) {
  Gcloud @("projects","add-iam-policy-binding",$ProjectId,"--member",$Member,"--role",$Role,"--condition=None") | Out-Null
}
Write-Host "==> Granting project-level roles..." -ForegroundColor Cyan
Grant-Project "serviceAccount:$DeployerSa"    "roles/cloudbuild.builds.editor"
Grant-Project "serviceAccount:$DeployerSa"    "roles/storage.admin"
Grant-Project "serviceAccount:$DeployerSa"    "roles/logging.viewer"
Grant-Project "serviceAccount:$BuildRunnerSa" "roles/artifactregistry.writer"
Grant-Project "serviceAccount:$BuildRunnerSa" "roles/run.admin"
Grant-Project "serviceAccount:$BuildRunnerSa" "roles/storage.objectViewer"
Grant-Project "serviceAccount:$BuildRunnerSa" "roles/logging.logWriter"

Write-Host "==> Granting service-account impersonation (actAs) chains..." -ForegroundColor Cyan
Gcloud @("iam","service-accounts","add-iam-policy-binding",$BuildRunnerSa,
  "--member","serviceAccount:$DeployerSa","--role","roles/iam.serviceAccountUser") | Out-Null
Gcloud @("iam","service-accounts","add-iam-policy-binding",$RuntimeSa,
  "--member","serviceAccount:$BuildRunnerSa","--role","roles/iam.serviceAccountUser") | Out-Null

Write-Host "==> Ensuring secret '$NvidiaSecret'..." -ForegroundColor Cyan
if (-not (Exists @("secrets","describe",$NvidiaSecret))) {
  Gcloud @("secrets","create",$NvidiaSecret,"--replication-policy=automatic")
} else { Write-Host "    already exists." }
Gcloud @("secrets","add-iam-policy-binding",$NvidiaSecret,
  "--member","serviceAccount:$RuntimeSa","--role","roles/secretmanager.secretAccessor") | Out-Null

$hasVersion = (& gcloud secrets versions list $NvidiaSecret --format="value(name)")
if (-not $hasVersion) {
  $sec = Read-Host -AsSecureString "Enter NVIDIA_API_KEY value (leave blank to add later)"
  $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
  if ($plain) {
    $tmp = New-TemporaryFile
    [IO.File]::WriteAllText($tmp.FullName, $plain)
    try { Gcloud @("secrets","versions","add",$NvidiaSecret,"--data-file=$($tmp.FullName)") }
    finally { Remove-Item $tmp.FullName -Force }
    Write-Host "    secret version added."
  } else {
    Write-Host "    skipped - add later via: gcloud secrets versions add $NvidiaSecret --data-file=PATH"
  }
}

Write-Host "==> Ensuring Workload Identity pool/provider..." -ForegroundColor Cyan
if (-not (Exists @("iam","workload-identity-pools","describe",$WifPoolId,"--location","global"))) {
  Gcloud @("iam","workload-identity-pools","create",$WifPoolId,"--location","global",
    "--display-name","GitHub Actions Pool")
} else { Write-Host "    pool exists." }

if (-not (Exists @("iam","workload-identity-pools","providers","describe",$WifProviderId,
                   "--location","global","--workload-identity-pool",$WifPoolId))) {
  Gcloud @("iam","workload-identity-pools","providers","create-oidc",$WifProviderId,
    "--location","global","--workload-identity-pool",$WifPoolId,"--display-name","GitHub provider",
    "--issuer-uri","https://token.actions.githubusercontent.com",
    "--attribute-mapping","google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref",
    "--attribute-condition","assertion.repository == '$GithubRepo'")
} else { Write-Host "    provider exists." }

$member = "principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/$WifPoolId/attribute.repository/$GithubRepo"
Gcloud @("iam","service-accounts","add-iam-policy-binding",$DeployerSa,
  "--role","roles/iam.workloadIdentityUser","--member",$member) | Out-Null

$WifProvider = (& gcloud iam workload-identity-pools providers describe $WifProviderId `
  --location="global" --workload-identity-pool=$WifPoolId --format="value(name)").Trim()

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host " Setup complete. Add these as GitHub Actions *Variables*"           -ForegroundColor Green
Write-Host " (Settings -> Secrets and variables -> Actions -> Variables):"      -ForegroundColor Green
Write-Host "=================================================================="  -ForegroundColor Green
Write-Host "  GCP_PROJECT_ID         = $ProjectId"
Write-Host "  GCP_REGION             = $Region"
Write-Host "  WIF_PROVIDER           = $WifProvider"
Write-Host "  DEPLOY_SERVICE_ACCOUNT = $DeployerSa"
Write-Host "  BUILD_RUNNER_SA        = $BuildRunnerSa"
Write-Host "  RUNTIME_SA_NAME        = $RuntimeSaName"
Write-Host "  AR_REPO                = $ArRepo"
Write-Host "  BACKEND_SERVICE        = $BackendService"
Write-Host "  FRONTEND_SERVICE       = $FrontendService"
Write-Host "  NVIDIA_SECRET          = $NvidiaSecret"
Write-Host ""
Write-Host " Or set them all with the GitHub CLI:" -ForegroundColor Green
@(
  "gh variable set GCP_PROJECT_ID --body `"$ProjectId`" --repo $GithubRepo",
  "gh variable set GCP_REGION --body `"$Region`" --repo $GithubRepo",
  "gh variable set WIF_PROVIDER --body `"$WifProvider`" --repo $GithubRepo",
  "gh variable set DEPLOY_SERVICE_ACCOUNT --body `"$DeployerSa`" --repo $GithubRepo",
  "gh variable set BUILD_RUNNER_SA --body `"$BuildRunnerSa`" --repo $GithubRepo",
  "gh variable set RUNTIME_SA_NAME --body `"$RuntimeSaName`" --repo $GithubRepo",
  "gh variable set AR_REPO --body `"$ArRepo`" --repo $GithubRepo",
  "gh variable set BACKEND_SERVICE --body `"$BackendService`" --repo $GithubRepo",
  "gh variable set FRONTEND_SERVICE --body `"$FrontendService`" --repo $GithubRepo",
  "gh variable set NVIDIA_SECRET --body `"$NvidiaSecret`" --repo $GithubRepo"
) | ForEach-Object { Write-Host "  $_" }
Write-Host "==================================================================" -ForegroundColor Green
