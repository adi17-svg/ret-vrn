from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "identify",
            "text": tool_gpt_reply(
                user_text,
                "Invite naming one thing that feels safe right now."
            )
        }

    if step == "identify":
        return {
            "step": "focus",
            "text": tool_gpt_reply(
                user_text,
                "Invite resting attention there briefly."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "You’re safe in this moment."
        )
    }
