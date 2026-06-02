# Transcript Viewer Page — Design

**Date:** 2026-06-03
**Status:** Approved

## Goal

Add a dedicated page that shows a job's generated transcripts in **readable text format**,
lets the user **listen** to each conversation as **voice**, and surfaces the **important KPIs**
for the dataset. Everything must work end-to-end on the live demo (which has no NVIDIA Riva
server configured).

## Key Decisions

- **Voice playback:** Browser-native **Web Speech API** (`window.speechSynthesis`). Produces
  audible speech with zero backend/setup, works on the deployed demo. Distinct voices for agent
  vs. customer. (The existing Riva-based audio ZIP download is left untouched.)
- **Navigation:** New route `/transcripts/:jobId`, linked from **Job History** (a "View" button
  on completed jobs) and from the **Export step** ("View Transcripts" on completion).
- **KPIs:** Full set, computed **client-side** from the fetched transcript list (no extra
  round-trip): total transcripts, avg duration, avg CSAT, resolution rate, escalation rate,
  avg turns, sentiment breakdown, and avg quality score (shown only when transcripts are scored).
- `TranscriptPreview` is **left untouched**; the shared conversation renderer is used only by the
  new page (lower risk).

## Backend Changes

`backend/app/routers/jobs.py` — add a read endpoint:

```
GET /jobs/{job_id}/results  ->  { "transcripts": [ ...transcript dicts... ] }
```

- Reuses `job_store.get_results(job_id)`.
- Returns `404` when the job has no results yet.
- No new dependencies. Audio/Riva/ZIP paths unchanged.

(Existing `/download?format=json` sets `Content-Disposition: attachment`, which is meant for file
downloads; a dedicated read endpoint is cleaner for in-page rendering.)

## Frontend Changes

- **`services/api.ts`** — `getJobResults(jobId): Promise<{ transcripts: Transcript[] }>`.
- **`App.tsx`** — add `<Route path="/transcripts/:jobId" element={<TranscriptViewer />} />`.
- **`hooks/useSpeech.ts`** *(new)* — wraps `speechSynthesis`. Loads voices (handles async
  `voiceschanged`), exposes `play(turns)`, `pause()`, `resume()`, `stop()`, `currentIndex`,
  `isPlaying`, `isSupported`, and a `rate` control. Picks a male-leaning voice for the agent and a
  female-leaning voice for the customer when the browser exposes them (best effort). Speaks turns
  sequentially, advancing on `onend`. Stops on unmount.
- **`components/TranscriptConversation.tsx`** *(new, shared/presentational)* — chat-bubble
  rendering (extracted styling from `TranscriptPreview`) with optional per-turn ▶ play buttons and
  active-turn highlight.
- **`components/TranscriptViewer.tsx`** *(new, the page)* — header with back link + job id;
  **KPI bar** (full set); search + sentiment filter; list of transcript cards, each with the text
  conversation and **▶ Play call / ⏸ Pause / ⏹ Stop** controls plus a speed slider.
- **`components/JobHistory.tsx`** — add a **"View"** button on completed jobs → navigate to page.
- **`components/ExportPanel.tsx`** — add a **"View Transcripts →"** button when the job completes.

## KPI Definitions (client-side)

| KPI | Source |
|-----|--------|
| Total transcripts | `transcripts.length` |
| Avg duration | mean of `metadata.durationSeconds` |
| Avg CSAT | mean of non-null `metadata.csatScore` |
| Resolution rate | % where `metadata.resolutionStatus === 'resolved'` |
| Escalation rate | % where `metadata.escalated === true` |
| Avg turns | mean of `conversation.length` |
| Sentiment breakdown | counts of `customer.sentiment` |
| Avg quality | mean of `qualityScores.overall` (only if any present) |

## Voice Playback Behavior

- One `SpeechSynthesisUtterance` per turn, spoken in sequence; active turn highlighted; advances on
  `onend`. Play the whole call or a single turn.
- Agent vs. customer get different voices/pitch.
- Audio is stopped on component unmount / route change so it doesn't leak across pages.
- If `speechSynthesis` is unavailable, controls are disabled with a friendly note.

## Error Handling

- Query loading / error / empty states on the page.
- `404` from `/results` → "Transcripts aren't available for this job yet."

## Verification (end-to-end)

1. Backend: generate a small job, confirm `GET /jobs/{id}/results` returns transcripts.
2. Frontend: `npm run build` (type-checks via `tsc`) passes.
3. Browser (Playwright): load `/transcripts/:jobId` — KPIs render, text shows, filters work, and
   `speechSynthesis.speak` is invoked on Play. Confirm the existing wizard still works.

## Out of Scope

- Changes to Riva/audio ZIP generation.
- Refactoring `TranscriptPreview`.
- Server-side KPI computation (reuses client-side derivation).
