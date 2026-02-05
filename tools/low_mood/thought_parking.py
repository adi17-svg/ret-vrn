from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "park",
            "text": tool_gpt_reply(
                user_text,
                "Invite them to name one heavy thought they can set aside for now."
            )
        }

    if step == "park":
        return {
            "step": "exit",
            "text": tool_gpt_reply(
                user_text,
                "Reassure them they don’t need to solve that thought right now."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(user_text, "Pausing here is fine.")
    }
