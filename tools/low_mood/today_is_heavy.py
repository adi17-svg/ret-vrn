from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "acknowledge",
            "text": tool_gpt_reply(
                user_text,
                "Acknowledge that some days feel heavier than others."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "You’re allowed to go slower today."
        )
    }
