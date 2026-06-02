"""SaaS / Tech Support industry template."""

from .base import IndustryTemplate

saas_template = IndustryTemplate(
    id="saas",
    name="SaaS & Tech Support",
    terminology=[
        "API key", "webhook", "integration", "SSO", "OAuth",
        "rate limit", "SLA", "uptime", "sandbox", "production environment",
        "subscription tier", "seat license", "admin console", "data export",
        "two-factor authentication", "audit log", "SAML", "LDAP", "provisioning",
        "incident", "escalation", "rollback", "deployment", "feature flag",
    ],
    agent_greetings=[
        "Thank you for contacting [SaaS Company] support. This is {agent_name}. How can I help you today?",
        "Hi, welcome to [Platform] technical support. My name is {agent_name}. Can you describe the issue you're experiencing?",
        "Thanks for reaching out to [Company] support. This is {agent_name}. Are you calling about a technical issue or account question?",
    ],
    agent_closings=[
        "Is there anything else I can help you with today?",
        "I'll send you a summary of today's support session via email. Is there anything else?",
        "You can also find documentation, release notes, and community forums at our developer portal.",
    ],
    hold_phrases=[
        "Let me pull up your account details. One moment please.",
        "I'll check our system status page. Please hold briefly.",
        "Let me reproduce that issue in our test environment. Just a moment.",
    ],
    compliance_phrases=[
        "All data is processed in accordance with our Privacy Policy and applicable data protection regulations.",
        "For enterprise compliance inquiries, please contact your dedicated Customer Success Manager.",
        "Security vulnerabilities should be reported through our responsible disclosure program.",
    ],
    scenario_context={
        "technical_bug": "Customer reporting a bug, error, or unexpected behavior in the platform.",
        "integration": "Customer needing help with API integration, webhooks, or third-party connections.",
        "billing": "Customer with questions about subscription, invoice, seat count, or upgrade/downgrade.",
        "onboarding": "New customer needing help getting started, configuring settings, or understanding features.",
        "account": "Customer issues with login, SSO, permissions, or user management.",
    },
    products_services=[
        "Core platform", "API access", "Enterprise tier", "Professional services",
        "Developer sandbox", "Advanced analytics", "Integrations marketplace",
        "Training & certification", "Priority support",
    ],
    departments=[
        "Tier 1 Support", "Tier 2 Technical", "Engineering Escalations",
        "Billing", "Customer Success", "Security Team",
    ],
)
