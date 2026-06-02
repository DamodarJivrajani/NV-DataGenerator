"""Legal industry template."""

from .base import IndustryTemplate

legal_template = IndustryTemplate(
    id="legal",
    name="Legal Services",
    terminology=[
        "retainer", "deposition", "affidavit", "subpoena", "plaintiff",
        "defendant", "litigation", "settlement", "arbitration", "mediation",
        "discovery", "brief", "motion", "statute of limitations", "jurisdiction",
        "pro bono", "contingency fee", "power of attorney", "notarization",
        "paralegal", "due process", "habeas corpus", "injunction", "precedent",
    ],
    agent_greetings=[
        "Thank you for calling [Law Firm Name]. This is {agent_name}. How may I assist you today?",
        "Good day, you've reached the legal offices of [Firm Name]. My name is {agent_name}. How can I help you?",
        "Thank you for calling. Please be aware that speaking with a legal intake specialist is not the same as retaining an attorney. How may I assist you?",
    ],
    agent_closings=[
        "Is there anything else I can help clarify for you today?",
        "We'll have an attorney contact you within one business day to discuss your case further.",
        "Thank you for reaching out. Please don't hesitate to call if you have any additional questions.",
    ],
    hold_phrases=[
        "Let me check on the status of your case. Please hold for a moment.",
        "I'll need to pull up your file. One moment please.",
        "Let me transfer you to the attorney handling your matter. Please hold.",
    ],
    compliance_phrases=[
        "Please note that this conversation does not constitute legal advice and does not create an attorney-client relationship.",
        "All information shared today is confidential under attorney-client privilege.",
        "For specific legal advice, you will need to schedule a consultation with one of our attorneys.",
    ],
    scenario_context={
        "consultation": "Prospective client seeking initial legal consultation. Gather basic case facts and schedule attorney meeting.",
        "case_status": "Existing client inquiring about case progress, court dates, or filing status.",
        "document_request": "Client requesting copies of legal documents, contracts, or case files.",
        "billing": "Client with questions about legal fees, invoices, or payment plans.",
        "emergency": "Urgent legal matter requiring immediate attorney attention (arrest, restraining order, etc.).",
    },
    products_services=[
        "Legal consultation", "Contract drafting", "Litigation representation",
        "Estate planning", "Corporate law", "Family law", "Criminal defense",
        "Intellectual property", "Real estate law", "Immigration services",
    ],
    departments=[
        "Legal Intake", "Civil Litigation", "Criminal Defense", "Corporate Law",
        "Family Law", "Estate Planning", "Billing", "Records Department",
    ],
)
