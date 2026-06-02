"""Logistics & Supply Chain industry template."""

from .base import IndustryTemplate

logistics_template = IndustryTemplate(
    id="logistics",
    name="Logistics & Supply Chain",
    terminology=[
        "tracking number", "waybill", "manifest", "customs clearance", "freight",
        "last-mile delivery", "carrier", "pallet", "SKU", "warehouse",
        "dispatch", "POD", "proof of delivery", "exception", "detention",
        "drayage", "intermodal", "LTL", "FTL", "cross-docking",
        "demurrage", "incoterms", "dangerous goods", "bonded warehouse", "3PL",
    ],
    agent_greetings=[
        "Thank you for calling [Logistics Company]. This is {agent_name}. How can I assist you with your shipment?",
        "Good day, [Courier Service] customer support. My name is {agent_name}. May I have your tracking number?",
        "Thank you for calling. You've reached [Company] freight services. This is {agent_name}. How can I help?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your shipment today?",
        "You can also track your shipment in real time on our website or mobile app.",
        "Thank you for choosing [Company]. We appreciate your business.",
    ],
    hold_phrases=[
        "Let me pull up the tracking details for your shipment. One moment please.",
        "I'll contact our dispatch team. Please hold briefly.",
        "Let me check the customs status for your package. Just a moment.",
    ],
    compliance_phrases=[
        "Claims for lost or damaged shipments must be filed within 30 days of delivery.",
        "Hazardous materials must be declared and properly packaged per regulatory requirements.",
        "Customs duties and taxes are the responsibility of the consignee unless otherwise agreed.",
    ],
    scenario_context={
        "tracking": "Customer checking the status or location of a shipment.",
        "missing_delivery": "Customer reporting a missing, delayed, or failed delivery.",
        "damage_claim": "Customer reporting damaged goods and initiating a freight claim.",
        "pickup_scheduling": "Customer scheduling a freight pickup or requesting a delivery appointment.",
        "customs": "Customer with questions about international shipping, customs clearance, or duties.",
    },
    products_services=[
        "Express shipping", "Ground freight", "LTL freight", "FTL freight",
        "International shipping", "Warehousing", "Last-mile delivery",
        "Cold chain logistics", "White glove delivery",
    ],
    departments=[
        "Customer Service", "Dispatch", "Claims", "International",
        "Customs Brokerage", "Warehousing", "Driver Support",
    ],
)
