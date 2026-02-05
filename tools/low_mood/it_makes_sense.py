from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "validate",
            "text": tool_gpt_reply(
                user_text,
                "Validate that their reaction makes sense given what they’re dealing with."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "They’re not overreacting."
        )
    }
