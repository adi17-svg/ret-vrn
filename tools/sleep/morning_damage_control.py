from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Reframe a rough night as not ruining the day. Encourage a gentler pace without self-judgment."
        )
    }
