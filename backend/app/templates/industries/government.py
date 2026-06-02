"""Government / Public Services industry template."""

from .base import IndustryTemplate

government_template = IndustryTemplate(
    id="government",
    name="Government & Public Services",
    terminology=[
        "permit", "license", "tax return", "refund", "benefits",
        "social security", "Medicare", "Medicaid", "unemployment", "citation",
        "DMV", "voter registration", "public record", "FOIA", "zoning variance",
        "municipal code", "ordinance", "property tax", "business license",
        "case number", "hearing date", "appeal", "compliance", "regulation",
    ],
    agent_greetings=[
        "Thank you for calling [Agency Name]. This is {agent_name}. How may I assist you today?",
        "Good day, you've reached the [Department] office. My name is {agent_name}. How can I help you?",
        "Thank you for calling. For quality assurance this call may be recorded. This is {agent_name}. How can I assist?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your inquiry today?",
        "Your case number for this interaction is [case_number]. Please reference this in future inquiries.",
        "Thank you for contacting us. Processing times may vary. We appreciate your patience.",
    ],
    hold_phrases=[
        "Let me pull up your account in our system. One moment please.",
        "I'll check the status of your application. Please hold briefly.",
        "Let me transfer you to the appropriate department. Please hold.",
    ],
    compliance_phrases=[
        "We are required by law to inform you that this call may be monitored and recorded.",
        "All information provided must be accurate and complete. Providing false information may result in penalties.",
        "Your personal information is protected under applicable privacy laws.",
    ],
    scenario_context={
        "benefits": "Citizen inquiring about eligibility for government benefits, application status, or payment issues.",
        "permits": "Business or individual requesting information about permits, licenses, or regulatory requirements.",
        "taxes": "Taxpayer with questions about filing, refunds, notices, or payment plans.",
        "dmv": "Driver or vehicle owner with questions about licenses, registrations, or violations.",
        "complaint": "Citizen filing a complaint, reporting an issue, or requesting a public record.",
    },
    products_services=[
        "Business licensing", "Building permits", "Tax services",
        "Vehicle registration", "Driver licensing", "Benefits enrollment",
        "Public records", "Code enforcement", "Voter services",
    ],
    departments=[
        "Tax Office", "DMV", "Permits & Licensing", "Benefits Division",
        "Code Enforcement", "Records Office", "Complaints Department",
    ],
)
