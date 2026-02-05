from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "find",
            "text": tool_gpt_reply(
                user_text,
                "Invite noticing anything that feels even 1% okay right now."
            )
        }

    if step == "find":
        return {
            "step": "stay",
            "text": tool_gpt_reply(
                user_text,
                "Invite staying with that feeling for about ten seconds."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "That’s enough for now."
        )
    }
