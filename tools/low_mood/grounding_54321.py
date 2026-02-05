from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "five",
            "text": tool_gpt_reply(user_text, "Invite naming five things you can see.")
        }

    if step == "five":
        return {
            "step": "four",
            "text": tool_gpt_reply(user_text, "Invite noticing four physical sensations.")
        }

    if step == "four":
        return {
            "step": "three",
            "text": tool_gpt_reply(user_text, "Invite listening for three different sounds.")
        }

    if step == "three":
        return {
            "step": "two",
            "text": tool_gpt_reply(user_text, "Invite noticing two smells.")
        }

    if step == "two":
        return {
            "step": "one",
            "text": tool_gpt_reply(user_text, "Invite noticing one taste or pleasant sensation.")
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "You’re here, in this moment. That’s enough."
        )
    }
