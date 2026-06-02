"""Manufacturing industry template."""

from .base import IndustryTemplate

manufacturing_template = IndustryTemplate(
    id="manufacturing",
    name="Manufacturing",
    terminology=[
        "purchase order", "invoice", "SKU", "lead time", "MOQ",
        "quality control", "defect rate", "SLA", "RMA", "batch number",
        "production schedule", "inventory", "BOM", "ISO certification",
        "tolerance", "calibration", "MSDS", "shipment tracking", "customs",
        "warranty claim", "technical drawing", "prototype", "tooling", "machining",
    ],
    agent_greetings=[
        "Thank you for calling [Company Name] manufacturing support. This is {agent_name}. How can I assist you?",
        "Good day, you've reached [Manufacturer] customer service. My name is {agent_name}. How may I help you?",
        "Thank you for calling. Could you please provide your customer account number or purchase order number?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your order or product today?",
        "I'll follow up with our production team and contact you within 24 hours.",
        "Thank you for your business. We value your partnership.",
    ],
    hold_phrases=[
        "Let me check the production status of your order. One moment please.",
        "I'll look into our inventory for that part. Please hold briefly.",
        "Let me check with our quality control team. Just a moment.",
    ],
    compliance_phrases=[
        "All products are manufactured to ISO 9001 quality standards.",
        "For safety data sheet requests, please contact our regulatory compliance team.",
        "Returns and RMA processing requires a valid purchase order number.",
    ],
    scenario_context={
        "order_status": "Customer inquiring about production progress, delivery date, or order status.",
        "quality_issue": "Customer reporting a product defect, quality concern, or requesting RMA.",
        "technical": "Customer with technical questions about specifications, tolerances, or product compatibility.",
        "pricing": "Customer requesting quotes, pricing, or bulk order discounts.",
        "supply_chain": "Customer inquiring about material availability, lead times, or supply disruptions.",
    },
    products_services=[
        "Custom parts manufacturing", "OEM components", "Quality testing",
        "Engineering support", "Supply chain management", "Just-in-time delivery",
        "Prototype development", "Tooling design",
    ],
    departments=[
        "Sales", "Production Planning", "Quality Assurance", "Shipping & Receiving",
        "Engineering", "Procurement", "Customer Service",
    ],
)
