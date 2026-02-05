from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Encourage letting the exhale be slightly longer than the inhale.
No need to control the breath.
Use slow, gentle language that reduces effort.
"""
        )
    }
