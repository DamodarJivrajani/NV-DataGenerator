import asyncio
import json
import uuid
from datetime import datetime
from typing import Any

from data_designer.config import (
    CategorySamplerParams,
    DataDesignerConfigBuilder,
    LLMStructuredColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    SubcategorySamplerParams,
    UniformSamplerParams,
    UUIDSamplerParams,
)
from data_designer.interface.data_designer import DataDesigner
from pydantic import BaseModel, Field

from app.models import GenerationConfig, Transcript
from app.templates.industries import get_template, IndustryTemplate


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""
    speaker: str = Field(description="Either 'agent' or 'customer'")
    text: str = Field(description="The spoken text")


class ConversationOutput(BaseModel):
    """Schema for LLM-generated conversation."""
    conversation: list[ConversationTurn] = Field(description="List of conversation turns")
    duration_seconds: int = Field(description="Estimated call duration in seconds")
    resolution_status: str = Field(description="One of: resolved, escalated, pending, unresolved")
    csat_score: int = Field(description="Customer satisfaction score 1-5")
    escalated: bool = Field(description="Whether the call was escalated")


INDUSTRY_SCENARIOS = {
    "healthcare": ["appointment", "claims", "prescription", "billing", "medical_info"],
    "finance": ["account_inquiry", "fraud_alert", "loan", "card_dispute", "wire_transfer"],
    "retail": ["order_status", "returns", "product_inquiry", "complaint", "loyalty"],
    "telecom": ["outage", "plan_change", "billing", "tech_support", "activation"],
    "insurance": ["claims_filing", "policy_inquiry", "coverage", "premium", "renewal"],
    "travel": ["reservation", "cancellation", "complaint", "rewards", "special_request"],
    "legal": ["consultation", "case_status", "document_request", "billing", "emergency"],
    "education": ["enrollment", "financial_aid", "transcripts", "advising", "technical_support"],
    "hr": ["application_status", "benefits", "payroll", "onboarding", "workplace_issue"],
    "automotive": ["service_appointment", "recall", "warranty", "sales", "roadside"],
    "real_estate": ["property_inquiry", "listing", "mortgage", "inspection", "closing"],
    "government": ["benefits", "permits", "taxes", "dmv", "complaint"],
    "energy": ["outage", "billing", "start_stop_service", "solar", "efficiency"],
    "manufacturing": ["order_status", "quality_issue", "technical", "pricing", "supply_chain"],
    "gaming": ["account_ban", "refund", "technical", "account_recovery", "billing"],
    "logistics": ["tracking", "missing_delivery", "damage_claim", "pickup_scheduling", "customs"],
    "saas": ["technical_bug", "integration", "billing", "onboarding", "account"],
}

SCENARIO_NAMES = {
    "appointment": "Appointment Scheduling",
    "claims": "Insurance Claims",
    "prescription": "Prescription Refills",
    "billing": "Billing Inquiries",
    "medical_info": "Medical Information",
    "account_inquiry": "Account Inquiry",
    "fraud_alert": "Fraud Alert",
    "loan": "Loan Application",
    "card_dispute": "Card Dispute",
    "wire_transfer": "Wire Transfer",
    "order_status": "Order Status",
    "returns": "Returns & Refunds",
    "product_inquiry": "Product Inquiry",
    "complaint": "Complaint",
    "loyalty": "Loyalty Program",
    "outage": "Service Outage",
    "plan_change": "Plan Changes",
    "tech_support": "Technical Support",
    "activation": "New Activation",
    "claims_filing": "Claims Filing",
    "policy_inquiry": "Policy Inquiry",
    "coverage": "Coverage Questions",
    "premium": "Premium Payments",
    "renewal": "Policy Renewal",
    "reservation": "Reservations",
    "cancellation": "Cancellations",
    "rewards": "Loyalty Rewards",
    "special_request": "Special Requests",
    # New domains
    "consultation": "Legal Consultation",
    "case_status": "Case Status",
    "document_request": "Document Request",
    "emergency": "Legal Emergency",
    "enrollment": "Enrollment",
    "financial_aid": "Financial Aid",
    "transcripts": "Academic Transcripts",
    "advising": "Academic Advising",
    "technical_support": "Technical Support",
    "application_status": "Application Status",
    "benefits": "Benefits",
    "payroll": "Payroll",
    "onboarding": "Onboarding",
    "workplace_issue": "Workplace Issue",
    "service_appointment": "Service Appointment",
    "recall": "Safety Recall",
    "warranty": "Warranty Claim",
    "sales": "Vehicle Sales",
    "roadside": "Roadside Assistance",
    "property_inquiry": "Property Inquiry",
    "listing": "Property Listing",
    "mortgage": "Mortgage Inquiry",
    "inspection": "Home Inspection",
    "closing": "Closing Process",
    "permits": "Permits & Licensing",
    "taxes": "Tax Services",
    "dmv": "DMV Services",
    "start_stop_service": "Start/Stop Service",
    "solar": "Solar Program",
    "efficiency": "Energy Efficiency",
    "quality_issue": "Quality Issue",
    "technical": "Technical Inquiry",
    "pricing": "Pricing & Quotes",
    "supply_chain": "Supply Chain",
    "account_ban": "Account Ban Appeal",
    "refund": "Refund Request",
    "account_recovery": "Account Recovery",
    "tracking": "Shipment Tracking",
    "missing_delivery": "Missing Delivery",
    "damage_claim": "Damage Claim",
    "pickup_scheduling": "Pickup Scheduling",
    "customs": "Customs & International",
    "technical_bug": "Technical Bug",
    "integration": "API Integration",
    "account": "Account Management",
}


class TranscriptGenerator:
    def __init__(self):
        self.data_designer = DataDesigner()

    def _build_config(self, config: GenerationConfig) -> DataDesignerConfigBuilder:
        builder = DataDesignerConfigBuilder()

        # Transcript ID
        builder.add_column(SamplerColumnConfig(
            name="transcript_id",
            sampler_type=SamplerType.UUID,
            params=UUIDSamplerParams(prefix="tx-"),
        ))

        # Industry (fixed based on config)
        builder.add_column(SamplerColumnConfig(
            name="industry",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=[config.industry]),
        ))

        # Scenario selection
        scenarios = config.scenarios if config.scenarios else INDUSTRY_SCENARIOS.get(config.industry, ["general"])
        builder.add_column(SamplerColumnConfig(
            name="scenario",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=scenarios),
        ))

        # Call type
        builder.add_column(SamplerColumnConfig(
            name="call_type",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=list(config.call_types)),
        ))

        # Language (fixed from config)
        builder.add_column(SamplerColumnConfig(
            name="language",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=[config.language]),
        ))

        # Customer sentiment
        builder.add_column(SamplerColumnConfig(
            name="customer_sentiment",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(
                values=list(config.sentiments),
                weights=[1.0] * len(config.sentiments),
            ),
        ))

        # Issue complexity
        builder.add_column(SamplerColumnConfig(
            name="issue_complexity",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(
                values=["low", "medium", "high"],
                weights=[0.3, 0.5, 0.2],
            ),
        ))

        # Customer name (using category instead of person to avoid database dependency)
        customer_first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "David", "Sarah"]
        customer_last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        builder.add_column(SamplerColumnConfig(
            name="customer_first_name",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=customer_first_names),
        ))
        builder.add_column(SamplerColumnConfig(
            name="customer_last_name",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=customer_last_names),
        ))
        builder.add_column(SamplerColumnConfig(
            name="customer_age",
            sampler_type=SamplerType.UNIFORM,
            params=UniformSamplerParams(low=18.0, high=75.0, decimal_places=0),
            convert_to="int",
        ))

        # Agent name (using category instead of person)
        agent_first_names = ["Emily", "Daniel", "Jessica", "Matthew", "Ashley", "Christopher", "Amanda", "Andrew", "Stephanie", "Joshua"]
        agent_last_names = ["Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "White", "Harris", "Clark", "Lewis"]
        builder.add_column(SamplerColumnConfig(
            name="agent_first_name",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=agent_first_names),
        ))
        builder.add_column(SamplerColumnConfig(
            name="agent_last_name",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(values=agent_last_names),
        ))

        # Agent experience level
        builder.add_column(SamplerColumnConfig(
            name="agent_experience",
            sampler_type=SamplerType.CATEGORY,
            params=CategorySamplerParams(
                values=["junior", "mid", "senior"],
                weights=[0.3, 0.4, 0.3],
            ),
        ))

        # Number of turns for this conversation
        builder.add_column(SamplerColumnConfig(
            name="num_turns",
            sampler_type=SamplerType.UNIFORM,
            params=UniformSamplerParams(
                low=float(config.min_turns),
                high=float(config.max_turns),
                decimal_places=0,
            ),
            convert_to="int",
        ))

        # Generate conversation using LLM
        conversation_prompt = self._build_conversation_prompt(config.industry)
        builder.add_column(LLMStructuredColumnConfig(
            name="generated_content",
            model_alias="nvidia-text",
            prompt=conversation_prompt,
            output_format=ConversationOutput,
        ))

        return builder


    def _build_conversation_prompt(self, industry: str) -> str:
        template = get_template(industry)
        
        # Build industry-specific context
        industry_context = ""
        if template:
            industry_context = f"""
INDUSTRY-SPECIFIC CONTEXT:
{template.get_prompt_context("{{ scenario }}")}

Sample Agent Greeting Style: "{template.get_agent_greeting()}"
Sample Agent Closing Style: "{template.get_agent_closing()}"

Use domain terminology naturally in the conversation.
"""
        
        return f"""Generate a realistic contact center phone conversation for the {{{{ industry }}}} industry.

Scenario: {{{{ scenario }}}}
Call Type: {{{{ call_type }}}}
Language: {{{{ language }}}}
Customer: {{{{ customer_first_name }}}} {{{{ customer_last_name }}}}, age {{{{ customer_age }}}}
Customer Sentiment: {{{{ customer_sentiment }}}}
Issue Complexity: {{{{ issue_complexity }}}}
Agent: {{{{ agent_first_name }}}} {{{{ agent_last_name }}}}
Agent Experience: {{{{ agent_experience }}}}
Target conversation length: {{{{ num_turns }}}} turns
{industry_context}
MULTILINGUAL INSTRUCTIONS:
- Generate the ENTIRE conversation in {{{{ language }}}}
- ALL dialogue, greetings, and closings MUST be in {{{{ language }}}}
- Use culturally appropriate names, idioms, and communication styles for {{{{ language }}}}
- If language is not English, the conversation must be fully in that language (no English mixing)

CONVERSATION GUIDELINES:
1. Start with a professional greeting from the agent
2. Customer explains their issue (tone matches their sentiment)
3. Agent acknowledges and begins helping
4. Include realistic back-and-forth troubleshooting/discussion
5. For "frustrated" or "angry" customers, show agent de-escalation techniques
6. For "confused" customers, agent should be extra patient and clear
7. Resolution should match issue complexity:
   - Low complexity: Usually resolved quickly
   - Medium complexity: May require holds, transfers, or follow-up
   - High complexity: Often escalated or requires callback
8. End with professional closing

SENTIMENT BEHAVIOR:
- frustrated: Customer is impatient, may interrupt, needs reassurance
- angry: Customer may raise voice, agent must stay calm and empathetic
- neutral: Standard professional interaction
- satisfied: Customer is pleasant, may express gratitude
- confused: Customer needs extra explanation, may ask repeated questions

Return a JSON object with:
- conversation: array of {{speaker: "agent"|"customer", text: "..."}}
- duration_seconds: estimated call duration (120-600 seconds based on complexity)
- resolution_status: "resolved"|"escalated"|"pending"|"unresolved"
- csat_score: customer satisfaction 1-5 (correlate with sentiment and resolution)
- escalated: boolean (true if transferred to supervisor or specialist)"""

    def _parse_result(self, row: dict, config: GenerationConfig) -> Transcript:
        """Parse a DataDesigner result row into a Transcript."""
        generated = row.get("generated_content", {})
        if isinstance(generated, str):
            try:
                generated = json.loads(generated)
            except json.JSONDecodeError:
                generated = {}
        
        # Handle case where generated might be a Pydantic model
        if hasattr(generated, "model_dump"):
            generated = generated.model_dump()

        scenario = row.get("scenario", "general")
        
        # Get customer and agent names from flat columns
        customer_first = row.get("customer_first_name", "John")
        customer_last = row.get("customer_last_name", "Doe")
        customer_age = row.get("customer_age", 35)
        agent_first = row.get("agent_first_name", "Agent")
        agent_last = row.get("agent_last_name", "Smith")
        
        # Parse and validate conversation turns
        raw_conversation = generated.get("conversation", [])
        if not isinstance(raw_conversation, list):
            raw_conversation = []
        
        # Filter valid conversation turns (must have speaker and text)
        valid_conversation = []
        for turn in raw_conversation:
            # Handle ConversationTurn objects or dicts
            if hasattr(turn, "speaker") and hasattr(turn, "text"):
                valid_conversation.append({
                    "speaker": turn.speaker,
                    "text": str(turn.text)
                })
            elif isinstance(turn, dict) and turn.get("speaker") and turn.get("text"):
                valid_conversation.append({
                    "speaker": turn["speaker"],
                    "text": str(turn["text"])
                })
        
        # If no valid conversation, generate a placeholder
        if not valid_conversation:
            valid_conversation = [
                {"speaker": "agent", "text": f"Thank you for calling. My name is {agent_first}. How may I help you today?"},
                {"speaker": "customer", "text": f"Hi, I'm calling about {SCENARIO_NAMES.get(scenario, scenario).lower()}."},
                {"speaker": "agent", "text": "I'd be happy to help you with that. Let me look into it for you."},
                {"speaker": "customer", "text": "Thank you, I appreciate your help."},
                {"speaker": "agent", "text": "Is there anything else I can help you with today?"},
                {"speaker": "customer", "text": "No, that's all. Thank you!"},
                {"speaker": "agent", "text": "Thank you for calling. Have a great day!"},
            ]

        return Transcript(
            id=row.get("transcript_id", str(uuid.uuid4())),
            industry=row.get("industry", config.industry),
            scenario=scenario,
            language=row.get("language", config.language),
            callType=row.get("call_type", "inbound"),
            customer={
                "name": f"{customer_first} {customer_last}",
                "age": int(customer_age) if customer_age else 35,
                "sentiment": row.get("customer_sentiment", "neutral"),
                "issueComplexity": row.get("issue_complexity", "medium"),
            },
            agent={
                "name": f"{agent_first} {agent_last}",
                "department": "Customer Service",
                "experienceLevel": row.get("agent_experience", "mid"),
            },
            conversation=valid_conversation,
            metadata={
                "durationSeconds": generated.get("duration_seconds", 300) or 300,
                "resolutionStatus": generated.get("resolution_status", "resolved") or "resolved",
                "csatScore": generated.get("csat_score"),
                "callReasonPrimary": SCENARIO_NAMES.get(scenario, scenario),
                "escalated": generated.get("escalated", False) or False,
            },
            createdAt=datetime.utcnow().isoformat() + "Z",
        )

    async def generate_preview(self, config: GenerationConfig) -> list[Transcript]:
        """Generate a small preview batch of transcripts."""
        builder = self._build_config(config)
        num_records = min(config.num_records, 5)  # Limit preview to 5

        try:
            # data_designer.preview makes blocking network calls; run it off the
            # event loop so it doesn't freeze other requests (e.g. status polling).
            preview = await asyncio.to_thread(
                self.data_designer.preview, builder, num_records=num_records
            )
            df = preview.dataset

            transcripts = []
            for _, row in df.iterrows():
                transcript = self._parse_result(row.to_dict(), config)
                transcripts.append(transcript)

            return transcripts
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")

    async def generate_batch(self, config: GenerationConfig) -> list[Transcript]:
        """Generate a full batch of transcripts."""
        builder = self._build_config(config)

        try:
            # data_designer.create is a long, blocking call — keep it off the
            # event loop so the async background task doesn't stall the server.
            results = await asyncio.to_thread(
                self.data_designer.create,
                builder,
                num_records=config.num_records,
                dataset_name=f"transcripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )
            df = await asyncio.to_thread(results.load_dataset)

            transcripts = []
            for _, row in df.iterrows():
                transcript = self._parse_result(row.to_dict(), config)
                transcripts.append(transcript)

            return transcripts
        except Exception as e:
            raise RuntimeError(f"Batch generation failed: {str(e)}")
