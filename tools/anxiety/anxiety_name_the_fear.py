from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Invite gently naming the fear in a few simple words.
No explanation or fixing.
Explain that naming alone can soften its intensity.
"""
        )
    }
