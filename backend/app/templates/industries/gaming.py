"""Gaming & Entertainment industry template."""

from .base import IndustryTemplate

gaming_template = IndustryTemplate(
    id="gaming",
    name="Gaming & Entertainment",
    terminology=[
        "account ban", "in-game purchase", "microtransaction", "DLC", "patch",
        "server outage", "latency", "game pass", "subscription", "refund policy",
        "chargeback", "cheating", "toxic behavior", "season pass", "battle pass",
        "loot box", "virtual currency", "skin", "achievement", "leaderboard",
        "multiplayer", "matchmaking", "two-factor authentication", "account recovery",
    ],
    agent_greetings=[
        "Thank you for contacting [Game Studio] support. This is {agent_name}. How can I help you today?",
        "Welcome to [Platform] player support. My name is {agent_name}. Are you calling about your account or a game issue?",
        "Thanks for reaching out to [Company] support. This is {agent_name}. How can I make your gaming experience better?",
    ],
    agent_closings=[
        "Is there anything else I can help you with for your gaming account today?",
        "Remember you can also submit tickets and check status at our support portal.",
        "Thanks for playing [Game Name]. Happy gaming!",
    ],
    hold_phrases=[
        "Let me pull up your account information. One moment please.",
        "I'll check the server status in your region. Please hold briefly.",
        "Let me review your purchase history. Just a moment.",
    ],
    compliance_phrases=[
        "In-game purchases are generally non-refundable per our Terms of Service.",
        "Account bans are issued in accordance with our Community Standards and Terms of Service.",
        "For security purposes, we will never ask for your full password.",
    ],
    scenario_context={
        "account_ban": "Player appealing a ban or suspension, or reporting an unjust account action.",
        "refund": "Player requesting a refund for a game, DLC, or in-game purchase.",
        "technical": "Player experiencing game crashes, connectivity issues, or performance problems.",
        "account_recovery": "Player locked out of their account, dealing with hacking, or password reset.",
        "billing": "Questions about subscription charges, payment methods, or unauthorized charges.",
    },
    products_services=[
        "Game subscriptions", "In-game currency", "DLC & expansions",
        "Season passes", "Cloud gaming", "Game streaming", "Digital games",
        "Merchandise", "Game passes",
    ],
    departments=[
        "Account Support", "Billing", "Technical Support", "Trust & Safety",
        "Community Management", "Appeals Team",
    ],
)
