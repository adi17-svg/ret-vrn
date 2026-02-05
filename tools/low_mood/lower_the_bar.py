from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "minimum",
            "text": tool_gpt_reply(
                user_text,
                "Invite them to consider the absolute minimum that would be enough for today."
            )
        }

    if step == "minimum":
        return {
            "step": "exit",
            "text": tool_gpt_reply(
                user_text,
                "Affirm that this minimum is enough for now."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(user_text, "We can stop here.")
    }
