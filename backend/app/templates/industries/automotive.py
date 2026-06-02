"""Automotive industry template."""

from .base import IndustryTemplate

automotive_template = IndustryTemplate(
    id="automotive",
    name="Automotive",
    terminology=[
        "VIN", "recall", "warranty", "service interval", "OBD", "transmission",
        "brake pads", "oil change", "tire rotation", "alignment", "emissions",
        "trade-in value", "financing APR", "MSRP", "invoice price", "lease",
        "powertrain", "infotainment", "roadside assistance", "lemon law",
        "extended warranty", "certified pre-owned", "mileage", "carfax",
    ],
    agent_greetings=[
        "Thank you for calling [Dealership Name]. This is {agent_name}. Are you calling about sales, service, or parts?",
        "Good day, you've reached [Brand] customer care. My name is {agent_name}. How may I assist you?",
        "Thank you for calling our service center. This is {agent_name}. How can I help you today?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your vehicle today?",
        "Thank you for choosing [Brand]. Drive safely!",
        "Don't forget to bring your vehicle in for your scheduled service. Is there anything else?",
    ],
    hold_phrases=[
        "Let me pull up your vehicle's service history. One moment please.",
        "I'll check on parts availability for your model. Please hold briefly.",
        "Let me look into the recall status for your VIN. Just a moment.",
    ],
    compliance_phrases=[
        "For your safety, please do not drive your vehicle if you believe it is unsafe.",
        "Recall repairs are performed at no cost to the vehicle owner under federal law.",
        "All service recommendations are based on manufacturer guidelines.",
    ],
    scenario_context={
        "service_appointment": "Customer scheduling or rescheduling a vehicle service appointment.",
        "recall": "Customer inquiring about safety recall status or scheduling recall repair.",
        "warranty": "Customer questions about warranty coverage, claims, or extended warranty.",
        "sales": "Customer interested in purchasing or leasing a new or pre-owned vehicle.",
        "roadside": "Customer requesting roadside assistance, towing, or emergency support.",
    },
    products_services=[
        "New vehicle sales", "Pre-owned vehicles", "Vehicle leasing",
        "Financing", "Service & maintenance", "Parts & accessories",
        "Extended warranty", "Roadside assistance", "Body shop",
    ],
    departments=[
        "Sales", "Service", "Finance", "Parts", "Body Shop",
        "Roadside Assistance", "Customer Relations",
    ],
)
