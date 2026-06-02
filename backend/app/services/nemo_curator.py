"""NeMo Curator-inspired data curation: dedup, PII filtering, quality filtering."""

import re
import logging
import json
from pathlib import Path
from app.models.transcript import CurationResult

logger = logging.getLogger(__name__)

# PII patterns
PII_PATTERNS = [
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"), "[SSN_REDACTED]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL_REDACTED]"),
    (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[CARD_REDACTED]"),
    (re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"), "[DATE_REDACTED]"),
    (re.compile(r"\b\d{5}(?:-\d{4})?\b"), "[ZIP_REDACTED]"),
]


def _redact_pii(text: str) -> tuple[str, int]:
    """Redact PII from text. Returns (cleaned_text, count_redacted)."""
    count = 0
    for pattern, replacement in PII_PATTERNS:
        new_text, n = pattern.subn(replacement, text)
        text = new_text
        count += n
    return text, count


def _conversation_fingerprint(transcript: dict) -> str:
    """Generate a simple fingerprint of a transcript for deduplication."""
    turns = transcript.get("conversation", [])
    # Take first 3 and last 2 turns for fingerprint
    sample_turns = turns[:3] + turns[-2:] if len(turns) > 5 else turns
    text = " ".join(t.get("text", "")[:50] for t in sample_turns).lower()
    # Normalize whitespace
    return re.sub(r"\s+", " ", text).strip()


def _minhash_similarity(fp1: str, fp2: str) -> float:
    """Simple token-level Jaccard similarity as MinHash approximation."""
    tokens1 = set(fp1.split())
    tokens2 = set(fp2.split())
    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1 & tokens2) / len(tokens1 | tokens2)


class NemoCurator:
    """
    NeMo Curator-inspired curation pipeline.
    Performs deduplication, PII filtering, and quality-based filtering
    using lightweight Python implementations (no local NeMo install required).
    """

    SIMILARITY_THRESHOLD = 0.85  # Transcripts above this similarity are considered duplicates

    def curate(
        self,
        transcripts: list[dict],
        deduplicate: bool = True,
        filter_pii: bool = True,
        min_quality_score: float = 0.0,
        artifacts_dir: Path | None = None,
        job_id: str | None = None,
    ) -> CurationResult:
        original_count = len(transcripts)
        pii_removed_count = 0
        quality_filtered_count = 0

        # Step 1: Quality filtering
        if min_quality_score > 0:
            filtered = []
            for t in transcripts:
                qs = t.get("qualityScores") or t.get("quality_scores")
                if qs:
                    overall = qs.get("overall", 10.0) if isinstance(qs, dict) else 10.0
                    if overall >= min_quality_score:
                        filtered.append(t)
                    else:
                        quality_filtered_count += 1
                else:
                    filtered.append(t)  # No score → keep
            transcripts = filtered

        # Step 2: PII filtering
        if filter_pii:
            for t in transcripts:
                total_pii = 0
                for turn in t.get("conversation", []):
                    cleaned, count = _redact_pii(turn.get("text", ""))
                    if count > 0:
                        turn["text"] = cleaned
                        total_pii += count
                if total_pii > 0:
                    pii_removed_count += 1

        # Step 3: Deduplication (approximate, similarity-based)
        deduplicated_count = 0
        if deduplicate and len(transcripts) > 1:
            fingerprints = [_conversation_fingerprint(t) for t in transcripts]
            keep = [True] * len(transcripts)

            for i in range(len(transcripts)):
                if not keep[i]:
                    continue
                for j in range(i + 1, len(transcripts)):
                    if not keep[j]:
                        continue
                    sim = _minhash_similarity(fingerprints[i], fingerprints[j])
                    if sim >= self.SIMILARITY_THRESHOLD:
                        keep[j] = False
                        deduplicated_count += 1

            transcripts = [t for t, k in zip(transcripts, keep) if k]

        # Step 4: Save curated output
        if artifacts_dir and job_id:
            out_path = artifacts_dir / f"{job_id}_curated.jsonl"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                for t in transcripts:
                    f.write(json.dumps(t) + "\n")

        return CurationResult(
            originalCount=original_count,
            deduplicatedCount=deduplicated_count,
            piiRemovedCount=pii_removed_count,
            qualityFilteredCount=quality_filtered_count,
            finalCount=len(transcripts),
            curatedTranscripts=transcripts,
        )
