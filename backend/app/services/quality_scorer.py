"""LLM-based quality scoring for generated transcripts."""

import json
import logging
import re
from typing import Any

from app.models.transcript import QualityScores

logger = logging.getLogger(__name__)


QUALITY_JUDGE_PROMPT = """You are an expert data quality evaluator for contact center transcript datasets.

Evaluate the following transcript and score it on three dimensions (each 0-10):

1. COHERENCE (0-10): Does the conversation flow logically? Are responses relevant to previous turns? Does the resolution match the issue?
   - 9-10: Perfectly logical flow, natural conversation
   - 7-8: Minor awkward transitions but overall coherent
   - 5-6: Some non-sequiturs or logic gaps
   - 0-4: Conversation is disjointed or nonsensical

2. DIVERSITY (0-10): Are the turns varied enough? Does each speaker use different phrases, vocabulary, and sentence structures?
   - 9-10: Rich varied vocabulary, unique phrasing each turn
   - 7-8: Mostly varied with some repetition
   - 5-6: Noticeable repetition of phrases or patterns
   - 0-4: Heavy repetition, formulaic dialogue

3. FACTUAL_CONSISTENCY (0-10): Does the agent provide accurate, consistent information? Are there contradictions? Does the agent follow realistic procedures?
   - 9-10: All agent statements are accurate and consistent
   - 7-8: Minor inconsistencies but mostly accurate
   - 5-6: Some factual errors or contradictions
   - 0-4: Major factual errors or inconsistent information

TRANSCRIPT:
Industry: {industry}
Scenario: {scenario}
Language: {language}

Conversation:
{conversation}

Respond with ONLY a valid JSON object in this exact format:
{{"coherence": <float 0-10>, "diversity": <float 0-10>, "factualConsistency": <float 0-10>}}"""


class QualityScorer:
    """Scores transcripts using an LLM judge."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://integrate.api.nvidia.com/v1",
                )
            except ImportError:
                raise RuntimeError("openai package required for quality scoring")
        return self._client

    def score_transcript(self, transcript: dict) -> QualityScores:
        """Score a single transcript dict using LLM judge."""
        try:
            conversation_text = "\n".join(
                f"[{turn.get('speaker', 'unknown').upper()}]: {turn.get('text', '')}"
                for turn in transcript.get("conversation", [])
            )

            prompt = QUALITY_JUDGE_PROMPT.format(
                industry=transcript.get("industry", "unknown"),
                scenario=transcript.get("scenario", "unknown"),
                language=transcript.get("language", "english"),
                conversation=conversation_text[:3000],  # Truncate very long convos
            )

            client = self._get_client()
            response = client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )

            raw = response.choices[0].message.content.strip()
            # Extract the first JSON object regardless of markdown fences or
            # surrounding prose. The previous split("```") approach broke on
            # uppercase ```JSON fences and silently fell back to neutral scores.
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON object found in model output: {raw[:200]!r}")

            scores = json.loads(match.group(0))
            coherence = float(scores.get("coherence", 7.0))
            diversity = float(scores.get("diversity", 7.0))
            factual = float(scores.get("factualConsistency", 7.0))
            overall = round((coherence + diversity + factual) / 3, 2)

            return QualityScores(
                coherence=round(coherence, 2),
                diversity=round(diversity, 2),
                factualConsistency=round(factual, 2),
                overall=overall,
            )

        except Exception as e:
            logger.warning(f"Quality scoring failed for transcript {transcript.get('id', '?')}: {e}")
            # Return neutral scores on failure rather than crashing
            return QualityScores(
                coherence=7.0,
                diversity=7.0,
                factualConsistency=7.0,
                overall=7.0,
            )

    def score_batch(self, transcripts: list[dict]) -> list[dict]:
        """Score a list of transcript dicts in-place, adding qualityScores field."""
        for t in transcripts:
            scores = self.score_transcript(t)
            t["qualityScores"] = scores.model_dump(by_alias=True)
        return transcripts
