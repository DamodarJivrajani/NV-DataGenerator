"""Shared converters from transcript dicts to fine-tuning dataset records.

Used by both the download endpoints and the HuggingFace uploader so the two
paths always emit identical SFT formats.
"""


def build_sft_record(transcript: dict) -> dict:
    """Convert a transcript to SFT format: {prompt, response}.

    The response is the final agent turn; the prompt is the conversation up to
    (but not including) that turn. Any turns after the final agent turn are
    dropped so the prompt never contains text that comes after the response.
    """
    turns = transcript.get("conversation", [])

    last_agent_idx = None
    for i, turn in enumerate(turns):
        if turn.get("speaker") == "agent":
            last_agent_idx = i

    if last_agent_idx is None:
        # No agent turn to use as a response; keep all turns as prompt context.
        prompt_turns = turns
        response = ""
    else:
        prompt_turns = turns[:last_agent_idx]
        response = turns[last_agent_idx].get("text", "")

    prompt_parts = [
        f"[{turn.get('speaker', 'agent').upper()}]: {turn.get('text', '')}"
        for turn in prompt_turns
    ]

    return {
        "prompt": "\n".join(prompt_parts),
        "response": response,
        "metadata": {
            "industry": transcript.get("industry"),
            "scenario": transcript.get("scenario"),
            "language": transcript.get("language", "english"),
        },
    }


def build_sft_instruct_record(transcript: dict) -> dict:
    """Convert a transcript to instruction-tuning SFT format ({messages: [...]})."""
    industry = transcript.get("industry", "")
    scenario = transcript.get("scenario", "")
    language = transcript.get("language", "english")
    turns = transcript.get("conversation", [])

    system_prompt = (
        f"You are a professional contact center agent in the {industry} industry. "
        f"You are handling a {scenario} scenario in {language}. "
        f"Be helpful, empathetic, and resolve the customer's issue efficiently."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for turn in turns:
        role = "assistant" if turn.get("speaker") == "agent" else "user"
        messages.append({"role": role, "content": turn.get("text", "")})

    return {"messages": messages}
