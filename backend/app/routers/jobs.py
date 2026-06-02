import json
import csv
import io
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from app.services.job_store import job_store
from app.services.dataset_formats import build_sft_record, build_sft_instruct_record
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
async def list_jobs():
    """List all generation jobs."""
    jobs = job_store.list_jobs()
    return [job.model_dump(by_alias=True) for job in jobs]


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get status of a specific job."""
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump(by_alias=True)


@router.get("/{job_id}/results")
async def get_job_results(job_id: str):
    """Return a job's generated transcripts as a JSON body for in-app viewing.

    Unlike /download (which sets Content-Disposition: attachment for file
    downloads), this is a plain read endpoint the Transcript Viewer page uses to
    render conversations, play audio, and compute KPIs client-side.
    """
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Transcripts not available for this job yet")
    return {"transcripts": transcripts}


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its results."""
    if not job_store.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted"}


@router.get("/{job_id}/download")
async def download_job(job_id: str, format: str = "json"):
    """Download generated transcripts in various formats."""
    settings = get_settings()

    if format == "curated":
        curated_path = settings.artifact_path / f"{job_id}_curated.jsonl"
        if not curated_path.exists():
            raise HTTPException(status_code=404, detail="Curated dataset not found. Run /curate first.")
        return FileResponse(
            str(curated_path),
            media_type="application/x-ndjson",
            filename=f"transcripts_{job_id}_curated.jsonl",
        )

    if format == "audio":
        audio_zip = settings.artifact_path / f"{job_id}_audio.zip"
        if not audio_zip.exists():
            raise HTTPException(status_code=404, detail="Audio not generated yet. Run /generate-audio first.")
        return FileResponse(
            str(audio_zip),
            media_type="application/zip",
            filename=f"transcripts_{job_id}_audio.zip",
        )

    if format == "dpo":
        dpo_path = settings.artifact_path / f"{job_id}_dpo.jsonl"
        if not dpo_path.exists():
            raise HTTPException(status_code=404, detail="DPO dataset not found. Run /generate-dpo first.")
        return FileResponse(
            str(dpo_path),
            media_type="application/x-ndjson",
            filename=f"transcripts_{job_id}_dpo.jsonl",
        )

    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    if format == "json":
        content = json.dumps(transcripts, indent=2)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=transcripts_{job_id}.json"},
        )
    elif format == "jsonl":
        lines = [json.dumps(t) for t in transcripts]
        content = "\n".join(lines)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f"attachment; filename=transcripts_{job_id}.jsonl"},
        )
    elif format == "csv":
        output = io.StringIO()
        if transcripts:
            flat_records = []
            for t in transcripts:
                qs = t.get("qualityScores") or {}
                flat = {
                    "id": t["id"],
                    "industry": t["industry"],
                    "scenario": t["scenario"],
                    "language": t.get("language", "english"),
                    "callType": t["callType"],
                    "customerName": t["customer"]["name"],
                    "customerAge": t["customer"]["age"],
                    "customerSentiment": t["customer"]["sentiment"],
                    "agentName": t["agent"]["name"],
                    "agentExperience": t["agent"]["experienceLevel"],
                    "conversationTurns": len(t["conversation"]),
                    "durationSeconds": t["metadata"]["durationSeconds"],
                    "resolutionStatus": t["metadata"]["resolutionStatus"],
                    "csatScore": t["metadata"]["csatScore"],
                    "qualityOverall": qs.get("overall", ""),
                    "qualityCoherence": qs.get("coherence", ""),
                    "qualityDiversity": qs.get("diversity", ""),
                    "createdAt": t["createdAt"],
                }
                flat_records.append(flat)

            writer = csv.DictWriter(output, fieldnames=flat_records[0].keys())
            writer.writeheader()
            writer.writerows(flat_records)

        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=transcripts_{job_id}.csv"},
        )
    elif format == "sft":
        # Supervised Fine-Tuning format: {prompt, response}
        sft_records = [build_sft_record(t) for t in transcripts]
        lines = [json.dumps(r) for r in sft_records]
        content = "\n".join(lines)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f"attachment; filename=transcripts_{job_id}_sft.jsonl"},
        )
    elif format == "sft_instruct":
        # Chat instruction tuning format with messages array
        sft_records = [build_sft_instruct_record(t) for t in transcripts]
        lines = [json.dumps(r) for r in sft_records]
        content = "\n".join(lines)
        return StreamingResponse(
            io.StringIO(content),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f"attachment; filename=transcripts_{job_id}_sft_instruct.jsonl"},
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Supported: json, jsonl, csv, sft, sft_instruct, curated, audio, dpo")


# ─── Quality Scoring ─────────────────────────────────────────────────────────

@router.post("/{job_id}/score")
def score_job(job_id: str):
    """Score all transcripts in a job using LLM quality judge.

    Defined as a sync handler so FastAPI runs it in a worker thread — the LLM
    scoring makes sequential blocking HTTP calls and must not run on the event
    loop, which would freeze all other requests (including status polling).
    """
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    settings = get_settings()
    if not settings.nvidia_api_key:
        raise HTTPException(status_code=400, detail="NVIDIA API key not configured")

    try:
        from app.services.quality_scorer import QualityScorer
        scorer = QualityScorer(api_key=settings.nvidia_api_key)
        scored = scorer.score_batch(transcripts)
        job_store.save_results(job_id, scored)
        return {"message": f"Scored {len(scored)} transcripts", "job_id": job_id}
    except Exception as e:
        logger.error(f"Quality scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Bias & Safety Report ────────────────────────────────────────────────────

@router.get("/{job_id}/bias-report")
def get_bias_report(job_id: str):
    """Analyze transcripts for bias and safety issues."""
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    try:
        from app.services.bias_analyzer import BiasAnalyzer
        analyzer = BiasAnalyzer()
        report = analyzer.analyze(transcripts)
        return report.model_dump(by_alias=True)
    except Exception as e:
        logger.error(f"Bias analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Statistics ──────────────────────────────────────────────────────────────

@router.get("/{job_id}/statistics")
def get_statistics(job_id: str):
    """Compute dataset statistics for a completed job."""
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    try:
        from app.services.statistics import StatisticsService
        stats_service = StatisticsService()
        stats = stats_service.compute(transcripts)
        return stats.model_dump(by_alias=True)
    except Exception as e:
        logger.error(f"Statistics computation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── NeMo Curator ────────────────────────────────────────────────────────────

class CurateRequest(BaseModel):
    min_quality_score: float = 0.0
    deduplicate: bool = True
    filter_pii: bool = True


@router.post("/{job_id}/curate")
def curate_job(job_id: str, request: CurateRequest):
    """Run NeMo Curator-inspired curation pipeline on job transcripts."""
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    try:
        from app.services.nemo_curator import NemoCurator
        settings = get_settings()
        curator = NemoCurator()
        result = curator.curate(
            transcripts=list(transcripts),  # copy to avoid mutating store
            deduplicate=request.deduplicate,
            filter_pii=request.filter_pii,
            min_quality_score=request.min_quality_score,
            artifacts_dir=settings.artifact_path,
            job_id=job_id,
        )
        # Return result without the full transcript list (too large for response)
        return {
            "originalCount": result.original_count,
            "deduplicatedCount": result.deduplicated_count,
            "piiRemovedCount": result.pii_removed_count,
            "qualityFilteredCount": result.quality_filtered_count,
            "finalCount": result.final_count,
        }
    except Exception as e:
        logger.error(f"Curation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── DPO Generation ──────────────────────────────────────────────────────────

def _generate_dpo_background(job_id: str, transcripts: list[dict], api_key: str, artifact_path: Path):
    """Background task to generate DPO dataset."""
    try:
        from openai import OpenAI
        import json

        client = OpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )

        dpo_records = []
        for t in transcripts:
            turns = t.get("conversation", [])
            if len(turns) < 2:
                continue

            # Build the prompt from all customer turns
            customer_turns = [turn.get("text", "") for turn in turns if turn.get("speaker") == "customer"]
            agent_turns = [turn.get("text", "") for turn in turns if turn.get("speaker") == "agent"]

            if not customer_turns or not agent_turns:
                continue

            prompt_text = f"Customer inquiry in {t.get('industry', 'general')} ({t.get('scenario', 'general')}): {customer_turns[0]}"
            chosen_response = " ".join(agent_turns)

            # Generate a lower-quality "rejected" response
            try:
                reject_resp = client.chat.completions.create(
                    model="meta/llama-3.1-8b-instruct",
                    messages=[{
                        "role": "user",
                        "content": (
                            f"You are a poor customer service agent. Give a brief, unhelpful, "
                            f"slightly rude response to: {prompt_text}. Keep it under 50 words."
                        ),
                    }],
                    temperature=0.8,
                    max_tokens=100,
                )
                rejected_response = reject_resp.choices[0].message.content.strip()
            except Exception:
                rejected_response = "I don't know. You'll have to call back."

            dpo_records.append({
                "prompt": prompt_text,
                "chosen": chosen_response[:500],
                "rejected": rejected_response,
                "metadata": {
                    "industry": t.get("industry"),
                    "scenario": t.get("scenario"),
                    "language": t.get("language", "english"),
                    "transcript_id": t.get("id"),
                },
            })

        out_path = artifact_path / f"{job_id}_dpo.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for record in dpo_records:
                f.write(json.dumps(record) + "\n")

        logger.info(f"DPO dataset saved: {out_path} ({len(dpo_records)} records)")
    except Exception as e:
        logger.error(f"DPO generation background task failed: {e}")


@router.post("/{job_id}/generate-dpo")
async def generate_dpo(job_id: str, background_tasks: BackgroundTasks):
    """Generate DPO (chosen/rejected) dataset for a completed job."""
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    settings = get_settings()
    if not settings.nvidia_api_key:
        raise HTTPException(status_code=400, detail="NVIDIA API key not configured")

    background_tasks.add_task(
        _generate_dpo_background,
        job_id=job_id,
        transcripts=list(transcripts),
        api_key=settings.nvidia_api_key,
        artifact_path=settings.artifact_path,
    )
    return {"message": "DPO generation started in background", "job_id": job_id}


# ─── HuggingFace Upload ───────────────────────────────────────────────────────

class HFUploadRequest(BaseModel):
    hf_token: str
    repo_name: str
    private: bool = True
    format: str = "json"


@router.post("/{job_id}/upload-hf")
def upload_to_hf(job_id: str, request: HFUploadRequest):
    """Upload generated dataset to HuggingFace Hub.

    Sync handler: the HuggingFace upload performs blocking network I/O
    (create_repo, file writes, create_commit) that must run in a worker thread
    rather than on the event loop.
    """
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    try:
        from app.services.hf_uploader import HFUploader
        uploader = HFUploader()
        result = uploader.upload(
            job_id=job_id,
            transcripts=list(transcripts),
            hf_token=request.hf_token,
            repo_name=request.repo_name,
            private=request.private,
            dataset_format=request.format,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"HF upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Audio Generation ─────────────────────────────────────────────────────────

def _generate_audio_background(job_id: str, transcripts: list[dict], riva_endpoint: str | None, artifact_path: Path):
    """Background task to generate audio for all transcripts."""
    try:
        from app.services.audio_generator import AudioGenerator
        generator = AudioGenerator(riva_endpoint=riva_endpoint)
        generator.generate_batch_audio(transcripts, artifacts_dir=artifact_path, job_id=job_id)
        logger.info(f"Audio generation complete for job {job_id}")
    except Exception as e:
        logger.error(f"Audio generation background task failed: {e}")


@router.post("/{job_id}/generate-audio")
async def generate_audio(job_id: str, background_tasks: BackgroundTasks):
    """Generate audio files for all transcripts in a job (async)."""
    transcripts = job_store.get_results(job_id)
    if not transcripts:
        raise HTTPException(status_code=404, detail="Job results not found")

    import os
    riva_endpoint = os.environ.get("RIVA_ENDPOINT")

    settings = get_settings()
    background_tasks.add_task(
        _generate_audio_background,
        job_id=job_id,
        transcripts=list(transcripts),
        riva_endpoint=riva_endpoint,
        artifact_path=settings.artifact_path,
    )
    return {
        "message": "Audio generation started in background",
        "job_id": job_id,
        "riva_available": riva_endpoint is not None,
    }

