"""Simple job storage using SQLite for persistence."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from app.models import GenerationJob, GenerationConfig


class JobStore:
    """SQLite-based job storage for persistence across restarts."""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        # timeout lets writers wait out a lock instead of failing immediately;
        # WAL allows readers and a writer to coexist. Roll back on any error so a
        # half-applied write is never left behind.
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    config TEXT NOT NULL,
                    progress REAL DEFAULT 0,
                    total_records INTEGER NOT NULL,
                    completed_records INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    error TEXT,
                    results TEXT
                )
            """)
            conn.commit()
    
    def create_job(self, job: GenerationJob) -> GenerationJob:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (id, status, config, progress, total_records, 
                                  completed_records, created_at, completed_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.status,
                job.config.model_dump_json(),
                job.progress,
                job.total_records,
                job.completed_records,
                job.created_at,
                job.completed_at,
                job.error,
            ))
            conn.commit()
        return job
    
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
            
            if not row:
                return None
            
            return self._row_to_job(row)
    
    def update_job(self, job: GenerationJob):
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE jobs SET 
                    status = ?, progress = ?, completed_records = ?,
                    completed_at = ?, error = ?
                WHERE id = ?
            """, (
                job.status,
                job.progress,
                job.completed_records,
                job.completed_at,
                job.error,
                job.id,
            ))
            conn.commit()
    
    def save_results(self, job_id: str, results: list[dict]):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE jobs SET results = ? WHERE id = ?",
                (json.dumps(results), job_id)
            )
            conn.commit()
    
    def get_results(self, job_id: str) -> Optional[list[dict]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT results FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
            
            if not row or not row["results"]:
                return None
            
            return json.loads(row["results"])
    
    def list_jobs(self, limit: int = 50) -> list[GenerationJob]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
            
            return [self._row_to_job(row) for row in rows]
    
    def delete_job(self, job_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_job(self, row: sqlite3.Row) -> GenerationJob:
        config_data = json.loads(row["config"])
        return GenerationJob(
            id=row["id"],
            status=row["status"],
            config=GenerationConfig(**config_data),
            progress=row["progress"],
            totalRecords=row["total_records"],
            completedRecords=row["completed_records"],
            createdAt=row["created_at"],
            completedAt=row["completed_at"],
            error=row["error"],
        )


# Global instance
job_store = JobStore()
