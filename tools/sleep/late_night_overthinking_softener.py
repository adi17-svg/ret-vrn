from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Acknowledge that late-night thoughts often feel louder. Gently remind that thinking doesn’t need answers tonight."
        )
    }
