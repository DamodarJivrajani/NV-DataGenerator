import re
from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator, model_validator

# Scenario ids are slugs (e.g. "appointment", "card_dispute"). Constraining to
# this shape — rather than to a registry that could drift from the frontend —
# blocks free-text being interpolated into the generation prompt (injection).
_SCENARIO_RE = re.compile(r"^[a-z0-9_]+$")

Sentiment = Literal["frustrated", "neutral", "satisfied", "angry", "confused"]
CallType = Literal["inbound", "outbound"]
ResolutionStatus = Literal["resolved", "escalated", "pending", "unresolved"]
ExperienceLevel = Literal["junior", "mid", "senior"]
IssueComplexity = Literal["low", "medium", "high"]
Language = Literal[
    "english", "spanish", "french", "german", "portuguese",
    "italian", "japanese", "mandarin", "hindi", "arabic",
    "korean", "dutch", "russian"
]


class QualityScores(BaseModel):
    coherence: float = Field(ge=0, le=10, description="Logical flow score 0-10")
    diversity: float = Field(ge=0, le=10, description="Turn variety score 0-10")
    factual_consistency: float = Field(alias="factualConsistency", ge=0, le=10, description="Factual accuracy score 0-10")
    overall: float = Field(ge=0, le=10, description="Average quality score 0-10")

    class Config:
        populate_by_name = True


class BiasReport(BaseModel):
    gender_bias_score: float = Field(alias="genderBiasScore", ge=0, le=1, description="0=no bias, 1=high bias")
    sentiment_distribution: dict = Field(alias="sentimentDistribution", default_factory=dict)
    demographic_diversity_score: float = Field(alias="demographicDiversityScore", ge=0, le=1)
    safety_flags: list[str] = Field(alias="safetyFlags", default_factory=list)
    overall_fairness_grade: str = Field(alias="overallFairnessGrade", description="A/B/C/D/F")
    total_analyzed: int = Field(alias="totalAnalyzed", default=0)

    class Config:
        populate_by_name = True


class DatasetStats(BaseModel):
    sentiment_distribution: dict = Field(alias="sentimentDistribution", default_factory=dict)
    turn_length_histogram: list = Field(alias="turnLengthHistogram", default_factory=list)
    industry_breakdown: dict = Field(alias="industryBreakdown", default_factory=dict)
    scenario_breakdown: dict = Field(alias="scenarioBreakdown", default_factory=dict)
    language_distribution: dict = Field(alias="languageDistribution", default_factory=dict)
    resolution_status_distribution: dict = Field(alias="resolutionStatusDistribution", default_factory=dict)
    csat_distribution: dict = Field(alias="csatDistribution", default_factory=dict)
    quality_score_distribution: dict = Field(alias="qualityScoreDistribution", default_factory=dict)
    avg_duration_seconds: float = Field(alias="avgDurationSeconds", default=0.0)
    total_transcripts: int = Field(alias="totalTranscripts", default=0)

    class Config:
        populate_by_name = True


class CurationResult(BaseModel):
    original_count: int = Field(alias="originalCount")
    deduplicated_count: int = Field(alias="deduplicatedCount")
    pii_removed_count: int = Field(alias="piiRemovedCount")
    quality_filtered_count: int = Field(alias="qualityFilteredCount")
    final_count: int = Field(alias="finalCount")
    curated_transcripts: list = Field(alias="curatedTranscripts", default_factory=list)

    class Config:
        populate_by_name = True


class CustomerProfile(BaseModel):
    name: str
    age: int
    sentiment: Sentiment
    issue_complexity: IssueComplexity = Field(alias="issueComplexity")

    class Config:
        populate_by_name = True


class AgentProfile(BaseModel):
    name: str
    department: str
    experience_level: ExperienceLevel = Field(alias="experienceLevel")

    class Config:
        populate_by_name = True


class ConversationTurn(BaseModel):
    speaker: Literal["agent", "customer"]
    text: str
    timestamp: Optional[str] = None


class TranscriptMetadata(BaseModel):
    duration_seconds: int = Field(alias="durationSeconds")
    resolution_status: ResolutionStatus = Field(alias="resolutionStatus")
    csat_score: Optional[int] = Field(alias="csatScore", default=None)
    call_reason_primary: str = Field(alias="callReasonPrimary")
    call_reason_secondary: Optional[str] = Field(alias="callReasonSecondary", default=None)
    escalated: bool = False

    class Config:
        populate_by_name = True


class Transcript(BaseModel):
    id: str
    industry: str
    scenario: str
    call_type: CallType = Field(alias="callType")
    customer: CustomerProfile
    agent: AgentProfile
    conversation: list[ConversationTurn]
    metadata: TranscriptMetadata
    created_at: str = Field(alias="createdAt")
    language: str = "english"
    quality_scores: Optional[QualityScores] = Field(alias="qualityScores", default=None)

    class Config:
        populate_by_name = True


class GenerationConfig(BaseModel):
    industry: str
    scenarios: list[str]
    call_types: list[CallType] = Field(alias="callTypes", default=["inbound"])
    sentiments: list[Sentiment] = Field(default=["neutral", "frustrated", "satisfied"])
    num_records: int = Field(alias="numRecords", default=10, ge=1, le=1000)
    min_turns: int = Field(alias="minTurns", default=4, ge=2, le=30)
    max_turns: int = Field(alias="maxTurns", default=12, ge=2, le=30)
    include_metadata: bool = Field(alias="includeMetadata", default=True)
    language: Language = "english"

    class Config:
        populate_by_name = True

    @field_validator("scenarios")
    @classmethod
    def _check_scenarios(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one scenario is required")
        if len(v) > 50:
            raise ValueError("Too many scenarios (max 50)")
        for s in v:
            if not _SCENARIO_RE.fullmatch(s):
                raise ValueError(f"Invalid scenario id: {s!r}")
        return v

    @model_validator(mode="after")
    def _check_turn_range(self) -> "GenerationConfig":
        if self.min_turns > self.max_turns:
            raise ValueError("minTurns must be less than or equal to maxTurns")
        return self


# NOTE: GenerationJob and JobStatus live in app.models.job (the package re-exports
# those). They were previously duplicated here, which risked two divergent schemas
# being imported from different modules.


