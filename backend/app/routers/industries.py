from fastapi import APIRouter

router = APIRouter(prefix="/industries", tags=["industries"])

INDUSTRIES = [
    {
        "id": "healthcare",
        "name": "Healthcare",
        "description": "Medical facilities, insurance, pharmacies",
        "icon": "🏥",
        "scenarios": [
            {"id": "appointment", "name": "Appointment Scheduling", "description": "Book, reschedule, or cancel appointments"},
            {"id": "claims", "name": "Insurance Claims", "description": "File or check status of insurance claims"},
            {"id": "prescription", "name": "Prescription Refills", "description": "Request medication refills"},
            {"id": "billing", "name": "Billing Inquiries", "description": "Questions about medical bills"},
            {"id": "medical_info", "name": "Medical Information", "description": "General health questions and guidance"},
        ],
    },
    {
        "id": "finance",
        "name": "Finance & Banking",
        "description": "Banks, credit unions, financial services",
        "icon": "🏦",
        "scenarios": [
            {"id": "account_inquiry", "name": "Account Inquiry", "description": "Balance checks, transaction history"},
            {"id": "fraud_alert", "name": "Fraud Alert", "description": "Report suspicious activity"},
            {"id": "loan", "name": "Loan Application", "description": "Apply for or inquire about loans"},
            {"id": "card_dispute", "name": "Card Dispute", "description": "Dispute unauthorized charges"},
            {"id": "wire_transfer", "name": "Wire Transfer", "description": "Initiate or track transfers"},
        ],
    },
    {
        "id": "retail",
        "name": "Retail & E-commerce",
        "description": "Online and physical retail stores",
        "icon": "🛒",
        "scenarios": [
            {"id": "order_status", "name": "Order Status", "description": "Track orders and deliveries"},
            {"id": "returns", "name": "Returns & Refunds", "description": "Process returns and refunds"},
            {"id": "product_inquiry", "name": "Product Inquiry", "description": "Questions about products"},
            {"id": "complaint", "name": "Complaint", "description": "File complaints about service or products"},
            {"id": "loyalty", "name": "Loyalty Program", "description": "Points, rewards, membership"},
        ],
    },
    {
        "id": "telecom",
        "name": "Telecommunications",
        "description": "Phone, internet, cable providers",
        "icon": "📱",
        "scenarios": [
            {"id": "outage", "name": "Service Outage", "description": "Report or check on outages"},
            {"id": "plan_change", "name": "Plan Changes", "description": "Upgrade, downgrade, or modify plans"},
            {"id": "billing", "name": "Billing Issues", "description": "Questions about bills and charges"},
            {"id": "tech_support", "name": "Technical Support", "description": "Troubleshoot technical issues"},
            {"id": "activation", "name": "New Activation", "description": "Activate new services or devices"},
        ],
    },
    {
        "id": "insurance",
        "name": "Insurance",
        "description": "Auto, home, life, and other insurance",
        "icon": "🛡️",
        "scenarios": [
            {"id": "claims_filing", "name": "Claims Filing", "description": "File new insurance claims"},
            {"id": "policy_inquiry", "name": "Policy Inquiry", "description": "Questions about coverage"},
            {"id": "coverage", "name": "Coverage Questions", "description": "What is and isn't covered"},
            {"id": "premium", "name": "Premium Payments", "description": "Pay or inquire about premiums"},
            {"id": "renewal", "name": "Policy Renewal", "description": "Renew or update policies"},
        ],
    },
    {
        "id": "travel",
        "name": "Travel & Hospitality",
        "description": "Airlines, hotels, travel agencies",
        "icon": "✈️",
        "scenarios": [
            {"id": "reservation", "name": "Reservations", "description": "Book flights, hotels, rentals"},
            {"id": "cancellation", "name": "Cancellations", "description": "Cancel or modify bookings"},
            {"id": "complaint", "name": "Complaints", "description": "Issues with service or accommodations"},
            {"id": "rewards", "name": "Loyalty Rewards", "description": "Points, miles, status inquiries"},
            {"id": "special_request", "name": "Special Requests", "description": "Accessibility, dietary, preferences"},
        ],
    },
    {
        "id": "legal",
        "name": "Legal Services",
        "description": "Law firms, legal aid, paralegal services",
        "icon": "⚖️",
        "scenarios": [
            {"id": "consultation", "name": "Legal Consultation", "description": "Initial consultation about a legal matter"},
            {"id": "case_status", "name": "Case Status", "description": "Inquire about existing case progress"},
            {"id": "document_request", "name": "Document Request", "description": "Request legal documents or records"},
            {"id": "billing", "name": "Billing & Fees", "description": "Questions about legal fees and invoices"},
            {"id": "emergency", "name": "Legal Emergency", "description": "Urgent legal matter requiring immediate help"},
        ],
    },
    {
        "id": "education",
        "name": "Education",
        "description": "Universities, colleges, online learning platforms",
        "icon": "🎓",
        "scenarios": [
            {"id": "enrollment", "name": "Enrollment", "description": "Course registration or enrollment questions"},
            {"id": "financial_aid", "name": "Financial Aid", "description": "Scholarships, loans, payment plans"},
            {"id": "transcripts", "name": "Academic Transcripts", "description": "Request official or unofficial transcripts"},
            {"id": "advising", "name": "Academic Advising", "description": "Degree planning and course selection"},
            {"id": "technical_support", "name": "Tech Support", "description": "Student portal or LMS access issues"},
        ],
    },
    {
        "id": "hr",
        "name": "HR & Recruitment",
        "description": "Human resources, talent acquisition, employee services",
        "icon": "👥",
        "scenarios": [
            {"id": "application_status", "name": "Application Status", "description": "Check job application or interview status"},
            {"id": "benefits", "name": "Benefits", "description": "Health insurance, retirement, PTO questions"},
            {"id": "payroll", "name": "Payroll", "description": "Paycheck, direct deposit, tax form issues"},
            {"id": "onboarding", "name": "Onboarding", "description": "New hire orientation and documentation"},
            {"id": "workplace_issue", "name": "Workplace Issue", "description": "HR concerns, accommodations, policy questions"},
        ],
    },
    {
        "id": "automotive",
        "name": "Automotive",
        "description": "Car dealerships, manufacturers, repair centers",
        "icon": "🚗",
        "scenarios": [
            {"id": "service_appointment", "name": "Service Appointment", "description": "Schedule vehicle maintenance or repair"},
            {"id": "recall", "name": "Safety Recall", "description": "Inquire about or schedule recall repair"},
            {"id": "warranty", "name": "Warranty Claim", "description": "Questions about warranty coverage or claims"},
            {"id": "sales", "name": "Vehicle Sales", "description": "Inquire about buying or leasing a vehicle"},
            {"id": "roadside", "name": "Roadside Assistance", "description": "Request towing or roadside help"},
        ],
    },
    {
        "id": "real_estate",
        "name": "Real Estate",
        "description": "Real estate agencies, property management, mortgage",
        "icon": "🏠",
        "scenarios": [
            {"id": "property_inquiry", "name": "Property Inquiry", "description": "Questions about a specific listing"},
            {"id": "listing", "name": "Property Listing", "description": "List a property for sale or rent"},
            {"id": "mortgage", "name": "Mortgage Inquiry", "description": "Mortgage pre-approval and rate questions"},
            {"id": "inspection", "name": "Home Inspection", "description": "Inspection scheduling, results, repairs"},
            {"id": "closing", "name": "Closing Process", "description": "Closing timeline, costs, and documentation"},
        ],
    },
    {
        "id": "government",
        "name": "Government & Public Services",
        "description": "Federal, state, and local government agencies",
        "icon": "🏛️",
        "scenarios": [
            {"id": "benefits", "name": "Benefits Inquiry", "description": "Government benefits eligibility and status"},
            {"id": "permits", "name": "Permits & Licensing", "description": "Business or construction permits"},
            {"id": "taxes", "name": "Tax Services", "description": "Filing, refunds, or payment plans"},
            {"id": "dmv", "name": "DMV Services", "description": "Driver licenses, vehicle registration"},
            {"id": "complaint", "name": "Complaint / Request", "description": "Public complaint or record request"},
        ],
    },
    {
        "id": "energy",
        "name": "Energy & Utilities",
        "description": "Electric, gas, water, and renewable energy providers",
        "icon": "⚡",
        "scenarios": [
            {"id": "outage", "name": "Outage Report", "description": "Report or check status of power/gas outage"},
            {"id": "billing", "name": "Billing", "description": "Questions about energy bills or payment"},
            {"id": "start_stop_service", "name": "Start/Stop Service", "description": "Start, stop, or transfer utility service"},
            {"id": "solar", "name": "Solar Program", "description": "Solar panel installation or net metering"},
            {"id": "efficiency", "name": "Energy Efficiency", "description": "Efficiency programs, rebates, audits"},
        ],
    },
    {
        "id": "manufacturing",
        "name": "Manufacturing",
        "description": "Industrial manufacturers, OEM suppliers, distributors",
        "icon": "🏭",
        "scenarios": [
            {"id": "order_status", "name": "Order Status", "description": "Production progress and delivery timeline"},
            {"id": "quality_issue", "name": "Quality Issue", "description": "Product defect or quality concern"},
            {"id": "technical", "name": "Technical Inquiry", "description": "Specifications, tolerances, compatibility"},
            {"id": "pricing", "name": "Pricing & Quotes", "description": "Request quotes or bulk order pricing"},
            {"id": "supply_chain", "name": "Supply Chain", "description": "Material availability and lead times"},
        ],
    },
    {
        "id": "gaming",
        "name": "Gaming & Entertainment",
        "description": "Video game studios, streaming, digital entertainment",
        "icon": "🎮",
        "scenarios": [
            {"id": "account_ban", "name": "Account Ban Appeal", "description": "Appeal a ban or account suspension"},
            {"id": "refund", "name": "Refund Request", "description": "Request refund for game or in-game purchase"},
            {"id": "technical", "name": "Technical Issue", "description": "Crashes, connectivity, or performance problems"},
            {"id": "account_recovery", "name": "Account Recovery", "description": "Locked out or compromised account"},
            {"id": "billing", "name": "Billing", "description": "Subscription charges or unauthorized purchases"},
        ],
    },
    {
        "id": "logistics",
        "name": "Logistics & Supply Chain",
        "description": "Couriers, freight carriers, 3PL providers",
        "icon": "📦",
        "scenarios": [
            {"id": "tracking", "name": "Shipment Tracking", "description": "Check status or location of shipment"},
            {"id": "missing_delivery", "name": "Missing Delivery", "description": "Report missing or delayed package"},
            {"id": "damage_claim", "name": "Damage Claim", "description": "Report damaged goods and file claim"},
            {"id": "pickup_scheduling", "name": "Pickup Scheduling", "description": "Schedule freight pickup or delivery"},
            {"id": "customs", "name": "Customs & International", "description": "International shipping and customs clearance"},
        ],
    },
    {
        "id": "saas",
        "name": "SaaS & Tech Support",
        "description": "Software companies, cloud platforms, developer tools",
        "icon": "💻",
        "scenarios": [
            {"id": "technical_bug", "name": "Technical Bug", "description": "Report a bug or unexpected behavior"},
            {"id": "integration", "name": "API Integration", "description": "Help with API, webhooks, or third-party connections"},
            {"id": "billing", "name": "Billing", "description": "Subscription, invoice, or seat count questions"},
            {"id": "onboarding", "name": "Onboarding", "description": "Getting started and configuration help"},
            {"id": "account", "name": "Account Management", "description": "Login, SSO, permissions, or user management"},
        ],
    },
]


@router.get("")
async def list_industries():
    """List all available industries."""
    return INDUSTRIES


@router.get("/{industry_id}/scenarios")
async def get_industry_scenarios(industry_id: str):
    """Get scenarios for a specific industry."""
    for industry in INDUSTRIES:
        if industry["id"] == industry_id:
            return industry["scenarios"]
    return {"error": "Industry not found"}

