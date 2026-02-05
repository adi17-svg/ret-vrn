from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "choose",
            "text": tool_gpt_reply(
                user_text,
                "Gently suggest a neutral, low-effort activity they could do for a couple of minutes."
            )
        }

    if step == "choose":
        return {
            "step": "exit",
            "text": tool_gpt_reply(
                user_text,
                "Reassure them they can stop anytime and don’t need to do more."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(user_text, "Pausing here is okay.")
    }
