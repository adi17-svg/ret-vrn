from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "name",
            "text": tool_gpt_reply(
                user_text,
                "Invite them to name what this feeling is like, without explaining or analyzing it."
            )
        }

    if step == "name":
        return {
            "step": "exit",
            "text": tool_gpt_reply(
                user_text,
                "Reassure them that naming it is enough for now."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(user_text, "We can pause here.")
    }
