from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Gently suggest allowing the body to soften and power down, without trying to force sleep."
        )
    }
