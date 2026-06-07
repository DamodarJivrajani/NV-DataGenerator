"""Bias and safety analysis for generated transcript datasets."""

import re
import logging
from collections import Counter
from app.models.transcript import BiasReport

logger = logging.getLogger(__name__)

# Gendered pronouns
MALE_PRONOUNS = {"he", "him", "his", "himself"}
FEMALE_PRONOUNS = {"she", "her", "hers", "herself"}

# Safety word list (partial — real deployments use a proper classifier)
OFFENSIVE_PATTERNS = [
    r"\b(idiot|stupid|moron|dumb)\b",
    r"\b(hate|despise|loathe)\s+(you|this|all)\b",
    r"\b(racist|sexist|bigot)\b",
    r"\b(discrimination|harass)\b",
]

# Diverse name origins heuristic (simplified)
WESTERN_NAMES = {"james", "mary", "john", "patricia", "robert", "jennifer", "michael", "linda",
                 "david", "sarah", "emily", "daniel", "jessica", "matthew", "ashley", "christopher"}
HISPANIC_NAMES = {"garcia", "rodriguez", "martinez", "hernandez", "lopez", "gonzalez", "perez",
                  "maria", "jose", "juan", "carlos", "ana", "luis", "miguel"}
ASIAN_NAMES = {"kim", "chen", "wang", "li", "zhang", "tanaka", "kumar", "patel", "singh",
               "ahmed", "ali", "hassan", "fatima", "priya", "yuki", "hiroshi"}
AFRICAN_NAMES = {"jackson", "washington", "johnson", "williams", "davis", "adebayo", "okafor",
                 "nkosi", "amara", "kofi", "kwame", "ama", "abebe"}


def _extract_pronouns(text: str) -> tuple[int, int]:
    """Count male vs female pronoun occurrences."""
    words = re.findall(r"\b\w+\b", text.lower())
    male = sum(1 for w in words if w in MALE_PRONOUNS)
    female = sum(1 for w in words if w in FEMALE_PRONOUNS)
    return male, female


def _check_safety(text: str) -> list[str]:
    """Return list of safety flags found in text."""
    flags = []
    for pattern in OFFENSIVE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            flags.append(f"Pattern '{pattern}' matched: {matches[:2]}")
    return flags


def _name_origin_label(name: str) -> str:
    # Match on whole name tokens, not substrings. Substring matching wrongly
    # classifies e.g. "linda" as asian (contains "li") or "diana" as hispanic
    # (contains "ana"), which made the diversity score meaningless.
    tokens = set(re.findall(r"[a-z]+", name.lower()))
    if tokens & ASIAN_NAMES:
        return "asian"
    if tokens & HISPANIC_NAMES:
        return "hispanic"
    if tokens & AFRICAN_NAMES:
        return "african"
    return "western"


class BiasAnalyzer:
    """Analyzes a batch of transcripts for bias and safety issues."""

    def analyze(self, transcripts: list[dict]) -> BiasReport:
        if not transcripts:
            return BiasReport(
                genderBiasScore=0.0,
                sentimentDistribution={},
                demographicDiversityScore=0.0,
                safetyFlags=[],
                overallFairnessGrade="A",
                totalAnalyzed=0,
            )

        # --- Gender bias ---
        agent_male = agent_female = 0
        customer_male = customer_female = 0

        for t in transcripts:
            for turn in t.get("conversation", []):
                text = turn.get("text", "")
                m, f = _extract_pronouns(text)
                if turn.get("speaker") == "agent":
                    agent_male += m
                    agent_female += f
                else:
                    customer_male += m
                    customer_female += f

        total_gendered = agent_male + agent_female + customer_male + customer_female
        if total_gendered > 0:
            # Bias = deviation from 50/50 split
            male_ratio = (agent_male + customer_male) / total_gendered
            gender_bias = abs(male_ratio - 0.5) * 2  # 0=balanced, 1=all one gender
        else:
            gender_bias = 0.0

        # --- Sentiment distribution ---
        sentiment_counts = Counter(
            t.get("customer", {}).get("sentiment", "unknown") for t in transcripts
        )

        # --- Demographic diversity ---
        name_origins = Counter()
        for t in transcripts:
            customer_name = t.get("customer", {}).get("name", "")
            agent_name = t.get("agent", {}).get("name", "")
            name_origins[_name_origin_label(customer_name)] += 1
            name_origins[_name_origin_label(agent_name)] += 1

        num_categories = len([v for v in name_origins.values() if v > 0])
        diversity_score = min(num_categories / 4.0, 1.0)  # 4 = max categories

        # --- Safety flags ---
        all_flags = []
        for t in transcripts:
            for turn in t.get("conversation", []):
                flags = _check_safety(turn.get("text", ""))
                if flags:
                    all_flags.extend([f"Transcript {t.get('id', '?')[:8]}: {flag}" for flag in flags])

        # --- Overall grade ---
        penalty = gender_bias * 3 + (len(all_flags) * 0.5) + max(0, (1 - diversity_score) * 2)
        if penalty < 0.5:
            grade = "A"
        elif penalty < 1.5:
            grade = "B"
        elif penalty < 3.0:
            grade = "C"
        elif penalty < 5.0:
            grade = "D"
        else:
            grade = "F"

        return BiasReport(
            genderBiasScore=round(gender_bias, 3),
            sentimentDistribution=dict(sentiment_counts),
            demographicDiversityScore=round(diversity_score, 3),
            safetyFlags=all_flags[:20],  # Cap at 20 flags
            overallFairnessGrade=grade,
            totalAnalyzed=len(transcripts),
        )
