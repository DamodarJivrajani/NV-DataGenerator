"""Energy / Utilities industry template."""

from .base import IndustryTemplate

energy_template = IndustryTemplate(
    id="energy",
    name="Energy & Utilities",
    terminology=[
        "kilowatt hour", "meter reading", "outage", "grid", "natural gas",
        "renewable energy", "solar panel", "net metering", "demand charge",
        "rate plan", "budget billing", "levelized payment", "disconnect notice",
        "reconnect fee", "service address", "account number", "peak hours",
        "time-of-use", "energy audit", "carbon offset", "green energy",
        "smart meter", "outage map", "restoration time",
    ],
    agent_greetings=[
        "Thank you for calling [Utility Company]. This is {agent_name}. How can I help you today?",
        "Good day, you've reached [Energy Provider] customer service. My name is {agent_name}. How may I assist you?",
        "Thank you for calling. To better serve you, can I have your account number or service address?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your energy service?",
        "You can also monitor your usage and report outages through our mobile app.",
        "Thank you for calling [Utility Name]. Have a great day and stay safe.",
    ],
    hold_phrases=[
        "Let me pull up your account. One moment please.",
        "I'll check our outage map for your area. Please hold briefly.",
        "Let me look at your billing history. Just a moment.",
    ],
    compliance_phrases=[
        "Payment arrangements are available to help customers avoid service disconnection.",
        "If you are experiencing financial hardship, you may qualify for our Low Income Home Energy Assistance Program.",
        "Disconnection of service may require 24-48 hours notice per regulatory requirements.",
    ],
    scenario_context={
        "outage": "Customer reporting a power or gas outage, or checking restoration status.",
        "billing": "Customer questions about energy bills, charges, or payment options.",
        "start_stop_service": "Customer starting, stopping, or transferring utility service.",
        "solar": "Customer questions about solar panel installation, net metering, or renewable programs.",
        "efficiency": "Customer seeking information about energy efficiency programs, rebates, or audits.",
    },
    products_services=[
        "Electricity service", "Natural gas service", "Solar programs",
        "Green energy plans", "Budget billing", "Paperless billing",
        "Energy efficiency rebates", "Smart home programs", "EV charging",
    ],
    departments=[
        "Customer Service", "Billing", "Outage Management", "Solar & Renewables",
        "New Service", "Energy Efficiency", "Collections",
    ],
)
