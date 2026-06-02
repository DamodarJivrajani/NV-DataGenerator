"""Dataset statistics computation for generated transcript batches."""

from collections import Counter
from app.models.transcript import DatasetStats


def _bucket_turns(n: int) -> str:
    if n <= 4:
        return "2-4"
    elif n <= 8:
        return "5-8"
    elif n <= 12:
        return "9-12"
    elif n <= 18:
        return "13-18"
    elif n <= 25:
        return "19-25"
    else:
        return "26+"


def _quality_bucket(score: float) -> str:
    if score >= 8.0:
        return "high (8-10)"
    elif score >= 6.0:
        return "medium (6-8)"
    else:
        return "low (0-6)"


class StatisticsService:
    """Computes summary statistics over a list of transcript dicts."""

    def compute(self, transcripts: list[dict]) -> DatasetStats:
        if not transcripts:
            return DatasetStats(
                sentimentDistribution={},
                turnLengthHistogram=[],
                industryBreakdown={},
                scenarioBreakdown={},
                languageDistribution={},
                resolutionStatusDistribution={},
                csatDistribution={},
                qualityScoreDistribution={},
                avgDurationSeconds=0.0,
                totalTranscripts=0,
            )

        sentiment_counts = Counter()
        turn_bucket_counts = Counter()
        industry_counts = Counter()
        scenario_counts = Counter()
        language_counts = Counter()
        resolution_counts = Counter()
        csat_counts = Counter()
        quality_bucket_counts = Counter()
        total_duration = 0.0

        for t in transcripts:
            # Sentiment
            sentiment = t.get("customer", {}).get("sentiment", "unknown")
            sentiment_counts[sentiment] += 1

            # Turn length
            num_turns = len(t.get("conversation", []))
            turn_bucket_counts[_bucket_turns(num_turns)] += 1

            # Industry & Scenario
            industry_counts[t.get("industry", "unknown")] += 1
            scenario_counts[t.get("scenario", "unknown")] += 1

            # Language
            language_counts[t.get("language", "english")] += 1

            # Resolution
            metadata = t.get("metadata", {})
            resolution_counts[metadata.get("resolutionStatus", "unknown")] += 1

            # CSAT
            csat = metadata.get("csatScore")
            if csat is not None:
                csat_counts[str(csat)] += 1

            # Duration
            total_duration += metadata.get("durationSeconds", 0) or 0

            # Quality score distribution
            qs = t.get("qualityScores") or t.get("quality_scores")
            if qs:
                overall = qs.get("overall", 7.0) if isinstance(qs, dict) else 7.0
                quality_bucket_counts[_quality_bucket(overall)] += 1

        # Build histogram list sorted by bucket
        bucket_order = ["2-4", "5-8", "9-12", "13-18", "19-25", "26+"]
        turn_histogram = [
            {"range": b, "count": turn_bucket_counts.get(b, 0)} for b in bucket_order
        ]

        avg_duration = total_duration / len(transcripts) if transcripts else 0.0

        return DatasetStats(
            sentimentDistribution=dict(sentiment_counts),
            turnLengthHistogram=turn_histogram,
            industryBreakdown=dict(industry_counts),
            scenarioBreakdown=dict(scenario_counts),
            languageDistribution=dict(language_counts),
            resolutionStatusDistribution=dict(resolution_counts),
            csatDistribution=dict(csat_counts),
            qualityScoreDistribution=dict(quality_bucket_counts),
            avgDurationSeconds=round(avg_duration, 1),
            totalTranscripts=len(transcripts),
        )
