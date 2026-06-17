# QA Prioritization Report: NV-DataGenerator

**Project:** Contact Center Synthetic Transcript Generator  
**Date:** 2026-06-17  
**Analysis Type:** Feature Coverage & Risk Assessment

---

## Executive Summary
Multi-tier web application (React + FastAPI) for generating synthetic call center transcripts with async job processing, multiple export formats, and industry-specific templates. **Critical testing focus:** data generation accuracy, async task reliability, and export format integrity.

---

## Prioritized Test Coverage by Severity

### 🔴 CRITICAL (P0) - Must Test Before Release

| # | Feature | Test Type | Acceptance Criteria |
|---|---------|-----------|-------------------|
| 1 | **Batch Generation Job Lifecycle** | Functional + Integration | Job creation → running → completion → persisted results; failed jobs mark status="failed" with error message; no hanging jobs |
| 2 | **Data Export Integrity (All 8 Formats)** | Data Validation | JSON/CSV/JSONL/SFT/SFT_Instruct/Curated/Audio/DPO all output valid; CSV proper escaping; JSON array structure; no truncated files |
| 3 | **Async Task Error Handling** | Reliability | Background task failures caught and persisted in `.error` sidecar; job status updates atomically; no orphaned running jobs |
| 4 | **Preview Generation** | Functional | Returns 1-5 records within timeout; output matches batch format; handles edge cases (max batch size) |
| 5 | **Configuration Validation** | Boundary Testing | Empty scenarios/callTypes/sentiments rejected with 400 error; invalid sentiment/type combinations fail gracefully |

---

### 🟠 HIGH (P1) - Should Test Before Release

| # | Feature | Test Type | Acceptance Criteria |
|---|---------|-----------|-------------------|
| 6 | **Job History Persistence** | Data Storage | SQLite: job metadata persists across restarts; results retrievable by job_id; timestamps accurate; status transitions logged |
| 7 | **Download Stream Reliability** | API Integration | All 8 export formats stream correctly; large files (>100MB) download without OOM; HTTP 404 for missing jobs; HTTP 500 for failed background tasks |
| 8 | **Industry/Scenario Mapping** | Data Mapping | All 6 industries load; scenario count correct per industry; filter logic returns expected scenarios; no data corruption |
| 9 | **Wizard Navigation & Form State** | UI/UX Flow | Step progression validates before advance; reset clears all state; back button maintains form data; no lost user input |
| 10 | **CORS & API Security** | Security | Production ALLOWED_ORIGINS respected; job IDs validated as UUID (prevent path traversal); credentials handled per config |

---

### 🟡 MEDIUM (P2) - Test If Resources Available

| # | Feature | Test Type | Acceptance Criteria |
|---|---------|-----------|-------------------|
| 11 | **NeMo Curator Integration** | External API | API timeout <30s; malformed responses handled gracefully; quota errors surfaced to user |
| 12 | **HuggingFace Upload** | External API | Auth token validation; network retry on transient failures; partial upload recovery; upload progress tracking |
| 13 | **Bias Analysis Engine** | Data Quality | Report generation completes within timeout; scoring logic validated against sample data; edge cases handled (empty transcripts) |
| 14 | **Audio Generation** | Background Task | Generated files in correct format (WAV/MP3); storage cleanup on job deletion; silence/noise thresholds validated |
| 15 | **Statistics Dashboard** | Calculation | KPI calculations accurate (count, sentiment distribution, avg length); pagination works on large datasets |

---

### 🟢 LOW (P3) - Test Last / Nice-to-Have

| # | Feature | Test Type | Acceptance Criteria |
|---|---------|-----------|-------------------|
| 16 | **Health Check Endpoint** | API Monitoring | `/api/v1/health` returns 200 + `{"status": "healthy"}` |
| 17 | **Docker Build/Deployment** | Infrastructure | Image builds successfully; startup health checks pass; environment variables load correctly |
| 18 | **API Documentation** | Documentation | Swagger `/docs` accessible; all endpoints documented; request/response schemas correct |

---

## Test Execution Plan by Severity

## Test Execution Plan by Severity

### Phase 1: P0 (CRITICAL) - Day 1 Testing
**Goal:** Verify core functionality; block release if any fail.

```
1. Unit + Integration: Job lifecycle (create → pending → running → completed)
2. Integration: Preview generation (1-5 records, <5s latency)
3. Data Validation: Export all 8 formats; validate output structure & encoding
4. Reliability: Async error handling (intentionally fail 1 job; verify .error sidecar)
5. Unit: Config validation (empty scenarios, invalid types → HTTP 400)
```

**Exit Criteria:** All 5 pass. If any fail: **STOP** - fix before proceeding.

---

### Phase 2: P1 (HIGH) - Day 1-2 Testing
**Goal:** Verify data persistence, security, and download reliability.

```
6. Data: SQLite job history (CRUD across restarts)
7. API: Download 8 formats; test large files (>100MB) & stream reliability
8. Data: Industry/Scenario mapping (6 industries × scenario counts)
9. UI: Wizard navigation (validate form state across steps)
10. Security: CORS enforcement, job ID UUID validation, path traversal attempts
```

**Exit Criteria:** All 5 pass. Release can proceed with P2 items.

---

### Phase 3: P2 (MEDIUM) - Day 2-3 Testing
**Goal:** Verify external integrations and background tasks.

```
11-15. External API timeouts, bias analysis accuracy, audio generation, statistics KPIs
```

**Exit Criteria:** Issues logged; non-critical failures don't block release.

---

### Phase 4: P3 (LOW) - Before Deployment
**Goal:** Final validation and polish.

```
16-18. Health checks, Docker build, API docs
```

---

| Risk | Impact | Mitigation |
|------|--------|-----------|
| No visible test suite in pyproject.toml | High | Add pytest coverage; automate critical paths |
| External API timeouts not visible | Medium | Add timeout tests; implement circuit breaker pattern |
| No rate limiting on generation endpoints | Medium | Implement rate limiting; document usage quotas |
| Async error handling uses file sidecar `.error` | Low | Monitor error file cleanup; add retention policy |
| Large export files may cause OOM | Medium | Implement streaming responses; chunk downloads |

---

## Quick Test Checklist (Severity-Based)

### 🔴 P0 CRITICAL - MUST PASS
- [ ] Job creation endpoint returns job_id (UUID format)
- [ ] Job transitions: pending → running → completed
- [ ] Failed job marked status="failed" with error message (no hanging)
- [ ] Preview generation returns 1-5 records in <5s
- [ ] All 8 export formats produce valid output files
- [ ] Empty config (no scenarios/callTypes/sentiments) rejected with HTTP 400
- [ ] CSV exports have proper escaping; JSON is valid array

### 🟠 P1 HIGH - SHOULD PASS
- [ ] Job metadata persists in SQLite across restart
- [ ] Download endpoint streams large files without OOM
- [ ] Missing job_id returns HTTP 404; failed background task returns HTTP 500
- [ ] All 6 industries load; scenario counts correct
- [ ] Wizard step validation blocks forward progression on invalid form
- [ ] CORS headers match production config
- [ ] Job ID validation rejects non-UUID strings (path traversal attempt)

### 🟡 P2 MEDIUM - NICE-TO-HAVE
- [ ] NeMo API timeout <30s; errors handled gracefully
- [ ] HuggingFace upload auth works; retry on failure
- [ ] Bias report generation completes within timeout
- [ ] Audio files generated in correct format
- [ ] Statistics KPIs match expected calculations

### 🟢 P3 LOW - BEFORE DEPLOY
- [ ] Health check `/api/v1/health` → 200 OK
- [ ] Docker image builds and starts
- [ ] Swagger `/docs` accessible and complete

---

## Known Risks & Gaps (Severity-Based)

| Severity | Risk | Impact | Mitigation |
|----------|------|--------|-----------|
| 🔴 P0 | No visible test suite in pyproject.toml | Tests may not run in CI; coverage unknown | Add pytest coverage; auto-run before deployment |
| 🔴 P0 | Async error handling via `.error` sidecar (file-based) | Job fails silently if file not created | Log all exceptions; implement centralized error tracking |
| 🟠 P1 | External API timeouts not documented | Unknown failure modes; potential OOM on retries | Set explicit timeout <30s; implement circuit breaker |
| 🟠 P1 | No rate limiting on generation endpoints | API abuse / resource exhaustion | Implement rate limiter; document usage quotas |
| 🟡 P2 | Large export files may cause OOM | Deployments crash on 1GB+ exports | Implement streaming responses; chunk downloads |
| 🟡 P2 | Error message disclosure | Sensitive data leak risk | Sanitize error messages; audit logs for sensitive info |

---

## Recommended Testing Tools

- **Backend API**: pytest + httpx (unit + integration)
- **Frontend**: Vitest + React Testing Library (component + integration)
- **E2E**: Playwright (full user workflows)
- **Load**: k6 or Apache JMeter (concurrent job submissions)
- **Data**: Pandas (export format validation)

---

## Deployment Validation Checklist

- [ ] Health check endpoint responds (`/api/v1/health`)
- [ ] API documentation accessible (`/docs`)
- [ ] CORS headers correct for production frontend origin
- [ ] Database file created + writable on first run
- [ ] External APIs reachable (NeMo, HuggingFace)
- [ ] Background tasks execute in GCP Cloud Run environment
