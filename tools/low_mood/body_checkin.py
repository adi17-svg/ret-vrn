from .tool_gpt import tool_gpt_reply

def handle(step: str | None, user_text: str | None):
    if step in (None, "start"):
        return {
            "step": "scan",
            "text": tool_gpt_reply(
                user_text,
                "Invite noticing shoulders, jaw, and hands without changing anything."
            )
        }

    if step == "scan":
        return {
            "step": "release",
            "text": tool_gpt_reply(
                user_text,
                "Invite softening just one area slightly, if it feels okay."
            )
        }

    return {
        "step": "exit",
        "text": tool_gpt_reply(
            user_text,
            "That’s enough for now. You don’t need to do more."
        )
    }
