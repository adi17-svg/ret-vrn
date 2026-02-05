from tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "vent",
            "text": tool_gpt_reply(
                user_text,
                "Invite sharing freely here. No fixing. No judging."
            )
        }

    if step == "vent":
        return {
            "step": "contain",
            "text": tool_gpt_reply(
                user_text,
                "Thank them for letting it out."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "You don’t have to solve anything right now."
        )
    }
