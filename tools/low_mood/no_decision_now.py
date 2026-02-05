from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "name",
            "text": tool_gpt_reply(
                user_text,
                "Invite them to name one thing they don’t need to decide right now."
            )
        }

    if step == "name":
        return {
            "step": "exit",
            "text": tool_gpt_reply(
                user_text,
                "Remind them they can come back to that decision later."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(user_text, "Stopping here is okay.")
    }
