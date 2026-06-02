"""Real Estate industry template."""

from .base import IndustryTemplate

real_estate_template = IndustryTemplate(
    id="real_estate",
    name="Real Estate",
    terminology=[
        "listing", "MLS", "closing costs", "escrow", "appraisal", "HOA",
        "mortgage rate", "pre-approval", "inspection", "contingency", "earnest money",
        "title insurance", "deed", "zoning", "square footage", "comparables",
        "buyer's agent", "seller's agent", "commission", "multiple offers",
        "short sale", "foreclosure", "equity", "amortization", "PMI",
    ],
    agent_greetings=[
        "Thank you for calling [Agency Name]. This is {agent_name}. Are you looking to buy, sell, or rent?",
        "Good day, you've reached [Realty Company]. My name is {agent_name}. How can I assist you with your real estate needs?",
        "Thank you for calling. This is {agent_name}. Are you calling about a specific property listing?",
    ],
    agent_closings=[
        "Is there anything else I can help you with regarding your real estate search?",
        "We'll send you the listings that match your criteria within the hour.",
        "Thank you for your interest. We look forward to helping you find your perfect home.",
    ],
    hold_phrases=[
        "Let me pull up the listing details. One moment please.",
        "I'll check on the property's availability. Please hold briefly.",
        "Let me look up comparable sales in that neighborhood. Just a moment.",
    ],
    compliance_phrases=[
        "We abide by all Fair Housing laws and welcome clients of all backgrounds.",
        "All property information is provided in good faith but is subject to verification.",
        "Mortgage rate information is for informational purposes only and not a rate lock.",
    ],
    scenario_context={
        "property_inquiry": "Buyer or renter inquiring about a specific property listing, pricing, or availability.",
        "listing": "Seller wanting to list a property, get a valuation, or understand the selling process.",
        "mortgage": "Client questions about mortgage pre-approval, rates, or financing options.",
        "inspection": "Questions about home inspection process, results, or repair negotiations.",
        "closing": "Buyer or seller with questions about closing timeline, costs, or documentation.",
    },
    products_services=[
        "Buyer representation", "Seller representation", "Rental management",
        "Property valuation", "Investment properties", "Commercial real estate",
        "Mortgage referrals", "Title services", "Home staging",
    ],
    departments=[
        "Residential Sales", "Commercial Sales", "Property Management",
        "Mortgage Referrals", "Title & Escrow", "New Construction",
    ],
)
