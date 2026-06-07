import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import GenerationConfig, GenerationJob
from app.services import TranscriptGenerator
from app.services.job_store import job_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])

generator = TranscriptGenerator()


@router.post("/preview")
async def generate_preview(config: GenerationConfig):
    """Generate a preview batch of transcripts (1-5 records)."""
    try:
        transcripts = await generator.generate_preview(config)
        return {"transcripts": [t.model_dump(by_alias=True) for t in transcripts]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def run_batch_generation(job_id: str, config: GenerationConfig):
    """Background task for batch generation."""
    job = job_store.get_job(job_id)
    if not job:
        return

    job.status = "running"
    job_store.update_job(job)
    
    try:
        transcripts = await generator.generate_batch(config)
        results = [t.model_dump(by_alias=True) for t in transcripts]
        
        # Save results to database
        job_store.save_results(job_id, results)
        
        job.status = "completed"
        job.completed_records = len(transcripts)
        job.progress = 100.0
        job.completed_at = datetime.utcnow().isoformat() + "Z"
        job_store.update_job(job)
    except Exception as e:
        # Best-effort: never let a failure to persist the "failed" status leave
        # the job wedged in "running" forever.
        job.status = "failed"
        job.error = str(e)
        try:
            job_store.update_job(job)
        except Exception:
            logger.exception("Failed to mark job %s as failed", job_id)


@router.post("/batch")
async def start_batch_generation(config: GenerationConfig, background_tasks: BackgroundTasks):
    """Start a batch generation job."""
    job = GenerationJob.create(config)
    job_store.create_job(job)
    background_tasks.add_task(run_batch_generation, job.id, config)
    return job.model_dump(by_alias=True)
