"""HuggingFace Hub dataset uploader."""

import json
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class HFUploader:
    """Uploads generated datasets to HuggingFace Hub."""

    def upload(
        self,
        job_id: str,
        transcripts: list[dict],
        hf_token: str,
        repo_name: str,
        private: bool = True,
        dataset_format: str = "json",
    ) -> dict:
        """
        Upload a transcript dataset to HuggingFace Hub.

        Args:
            job_id: The generation job ID (used in dataset card)
            transcripts: List of transcript dicts to upload
            hf_token: HuggingFace API token (used in-memory, never stored)
            repo_name: Full repo name e.g. "username/my-dataset"
            private: Whether the repo is private
            dataset_format: "json" or "jsonl" or "sft" or "dpo"

        Returns:
            dict with repo_url and files_uploaded
        """
        try:
            from huggingface_hub import HfApi, CommitOperationAdd
        except ImportError:
            raise RuntimeError("huggingface_hub package is required. Install with: pip install huggingface_hub")

        # Sanitize repo name — only allow alphanumeric, hyphens, underscores, slashes
        import re
        if not re.match(r"^[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+$", repo_name):
            raise ValueError("Invalid repo_name. Must be 'username/dataset-name' with alphanumeric characters, hyphens, and underscores only.")

        api = HfApi(token=hf_token)

        # Create repository
        try:
            api.create_repo(repo_id=repo_name, repo_type="dataset", private=private, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create repository: {e}")

        files_uploaded = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Write main data file
            if dataset_format == "sft":
                from app.services.dataset_formats import build_sft_record
                data_file = tmp_path / "data.jsonl"
                with open(data_file, "w", encoding="utf-8") as f:
                    for t in transcripts:
                        f.write(json.dumps(build_sft_record(t)) + "\n")
                hf_data_path = "data/train.jsonl"
            elif dataset_format == "jsonl":
                data_file = tmp_path / "data.jsonl"
                with open(data_file, "w", encoding="utf-8") as f:
                    for t in transcripts:
                        f.write(json.dumps(t) + "\n")
                hf_data_path = "data/train.jsonl"
            else:
                data_file = tmp_path / "data.json"
                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(transcripts, f, indent=2)
                hf_data_path = "data/train.json"

            # Generate dataset card
            readme_content = self._generate_dataset_card(
                job_id=job_id,
                repo_name=repo_name,
                num_records=len(transcripts),
                dataset_format=dataset_format,
                transcripts=transcripts,
            )
            readme_file = tmp_path / "README.md"
            readme_file.write_text(readme_content, encoding="utf-8")

            # Upload files
            operations = [
                CommitOperationAdd(path_in_repo=hf_data_path, path_or_fileobj=str(data_file)),
                CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=str(readme_file)),
            ]

            api.create_commit(
                repo_id=repo_name,
                repo_type="dataset",
                operations=operations,
                commit_message=f"Add synthetic contact center dataset (job {job_id[:8]})",
            )

            files_uploaded = [hf_data_path, "README.md"]

        repo_url = f"https://huggingface.co/datasets/{repo_name}"
        logger.info(f"Dataset uploaded to {repo_url}")
        return {"repo_url": repo_url, "files_uploaded": files_uploaded}

    def _generate_dataset_card(
        self,
        job_id: str,
        repo_name: str,
        num_records: int,
        dataset_format: str,
        transcripts: list[dict],
    ) -> str:
        """Generate a HuggingFace dataset card (README.md)."""
        industries = list(set(t.get("industry", "unknown") for t in transcripts))
        languages = list(set(t.get("language", "english") for t in transcripts))

        return f"""---
language:
{chr(10).join(f'- {lang}' for lang in languages)}
license: apache-2.0
task_categories:
- conversational
- text-generation
tags:
- synthetic
- contact-center
- customer-service
- nvidia
- nemo
size_categories:
- {'n<1K' if num_records < 1000 else '1K<n<10K'}
---

# Synthetic Contact Center Transcripts

Generated with [NV-DataGenerator](https://github.com) using NVIDIA NeMo Data Designer.

## Dataset Description

This dataset contains **{num_records}** synthetic contact center transcripts covering the following industries: {', '.join(industries)}.

All conversations are AI-generated for training purposes and do not represent real customer interactions.

## Dataset Details

| Property | Value |
|----------|-------|
| Records | {num_records} |
| Industries | {', '.join(industries)} |
| Languages | {', '.join(languages)} |
| Format | {dataset_format.upper()} |
| Job ID | `{job_id}` |

## Data Fields

- `id`: Unique transcript identifier
- `industry`: Industry vertical
- `scenario`: Call scenario type
- `language`: Language of the transcript
- `customer`: Customer profile (name, age, sentiment, issue complexity)
- `agent`: Agent profile (name, department, experience level)
- `conversation`: List of turn-by-turn dialogue
- `metadata`: Call metadata (duration, resolution status, CSAT score)
- `qualityScores`: LLM-evaluated quality scores (coherence, diversity, factual consistency)

## Generation

Generated using the NV-DataGenerator tool with NVIDIA NeMo Data Designer and LLM-based quality scoring.
"""
