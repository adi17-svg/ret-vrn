from tool_gpt_sleep import sleep_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": sleep_gpt_reply(
            user_text,
            "Soften the belief that you are ‘bad at sleeping’. Reassure that sleep ability isn’t an identity."
        )
    }
