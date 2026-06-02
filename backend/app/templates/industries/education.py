"""Education industry template."""

from .base import IndustryTemplate

education_template = IndustryTemplate(
    id="education",
    name="Education",
    terminology=[
        "enrollment", "transcript", "GPA", "credit hours", "semester",
        "financial aid", "FAFSA", "scholarship", "tuition", "bursar",
        "registrar", "advising", "prerequisites", "syllabus", "graduation",
        "accreditation", "student ID", "learning management system", "online portal",
        "academic hold", "withdrawal", "incomplete grade", "dean's list",
    ],
    agent_greetings=[
        "Thank you for calling [University Name]. This is {agent_name} in the registrar's office. How can I help you?",
        "Good morning, [College Name] student services. My name is {agent_name}. How may I assist you today?",
        "Thank you for calling. You've reached the academic advising center. This is {agent_name}. How can I help?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your academic record?",
        "Don't forget you can also check your enrollment status through the student portal.",
        "Thank you for calling. Best of luck with your studies!",
    ],
    hold_phrases=[
        "Let me pull up your student account. One moment please.",
        "I'll check that with our financial aid office. Please hold briefly.",
        "Let me look into your enrollment status. Just a moment.",
    ],
    compliance_phrases=[
        "For privacy purposes, I'll need to verify your student ID before accessing your records.",
        "Under FERPA regulations, I can only discuss your academic record with you directly unless you've authorized a third party.",
        "All academic record changes must be submitted in writing with appropriate signatures.",
    ],
    scenario_context={
        "enrollment": "Student inquiring about course registration, enrollment status, or class availability.",
        "financial_aid": "Questions about financial aid packages, disbursement, scholarship eligibility, or payment plans.",
        "transcripts": "Request for official or unofficial academic transcripts.",
        "advising": "Academic planning, course selection, degree requirements, or graduation audit.",
        "technical_support": "Issues with student portal, LMS access, email, or other academic systems.",
    },
    products_services=[
        "Undergraduate programs", "Graduate programs", "Online courses",
        "Student portal", "Library services", "Financial aid",
        "Student housing", "Campus health", "Career services",
    ],
    departments=[
        "Registrar", "Financial Aid", "Academic Advising", "Bursar",
        "IT Help Desk", "Admissions", "Housing", "Student Affairs",
    ],
)
