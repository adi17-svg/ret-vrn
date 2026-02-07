from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    if step in (None, "start"):
        return {
            "step": "unload",
            "text": sleep_gpt_reply(
                user_text,
                "Invite gently placing any remaining thoughts or to-dos outside the mind, as if setting them down for the night."
            )
        }

    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Reassure that nothing needs to be solved right now."
        )
    }
