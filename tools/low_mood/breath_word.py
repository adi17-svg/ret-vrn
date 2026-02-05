from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "breathe",
            "text": tool_gpt_reply(
                user_text,
                "Guide a slow inhale with the word 'here' and exhale with 'now'."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "Let the breath return to its own rhythm."
        )
    }
