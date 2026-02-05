from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "acknowledge",
            "text": tool_gpt_reply(
                user_text,
                "Acknowledge that this is a hard moment."
            )
        }

    if step == "acknowledge":
        return {
            "step": "normalize",
            "text": tool_gpt_reply(
                user_text,
                "Normalize that many people feel this way sometimes."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "You don’t need to fix anything right now."
        )
    }
