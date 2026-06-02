"""HR / Recruitment industry template."""

from .base import IndustryTemplate

hr_template = IndustryTemplate(
    id="hr",
    name="HR & Recruitment",
    terminology=[
        "job posting", "resume", "candidate", "onboarding", "background check",
        "offer letter", "compensation", "benefits", "PTO", "FMLA",
        "performance review", "termination", "severance", "W-2", "direct deposit",
        "open enrollment", "COBRA", "401k", "EEO", "ATS",
        "reference check", "probationary period", "non-compete", "employee handbook",
    ],
    agent_greetings=[
        "Thank you for calling [Company Name] Human Resources. This is {agent_name}. How can I assist you today?",
        "Hello, you've reached the HR department at [Company Name]. My name is {agent_name}. How may I help you?",
        "Thank you for calling our recruitment line. This is {agent_name}. Are you calling about a job application or an existing position?",
    ],
    agent_closings=[
        "Thank you for reaching out. Is there anything else HR can help you with?",
        "We'll be in touch within the next few business days. Thank you for your patience.",
        "Don't forget you can also access HR resources through the employee self-service portal.",
    ],
    hold_phrases=[
        "Let me pull up your application. One moment please.",
        "I'll check on that with our payroll team. Please hold briefly.",
        "Let me look into your benefits enrollment. Just a moment.",
    ],
    compliance_phrases=[
        "All hiring decisions are made without regard to race, color, religion, sex, national origin, disability, or veteran status.",
        "This conversation may be recorded for training and quality assurance purposes.",
        "For employment verification, all requests must be submitted in writing to our HR department.",
    ],
    scenario_context={
        "application_status": "Candidate inquiring about job application status, interview scheduling, or next steps.",
        "benefits": "Employee questions about health insurance, retirement plans, PTO, or other benefits.",
        "payroll": "Employee issues with paycheck, direct deposit, tax withholding, or W-2 forms.",
        "onboarding": "New hire questions about start date, orientation, documentation, or system access.",
        "workplace_issue": "Employee reporting a workplace concern, harassment, accommodation request, or policy question.",
    },
    products_services=[
        "Talent acquisition", "Employee benefits", "Payroll processing",
        "Performance management", "Learning & development", "Employee self-service",
        "Background screening", "Compensation planning",
    ],
    departments=[
        "Talent Acquisition", "Compensation & Benefits", "Payroll",
        "Employee Relations", "Learning & Development", "HR Business Partners",
    ],
)
