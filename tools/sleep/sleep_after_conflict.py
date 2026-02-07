from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Acknowledge lingering tension after conflict. Encourage letting it pause until tomorrow."
        )
    }
