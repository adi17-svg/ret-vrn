from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Guide attention to physical contact.
Mention feeling the chair, the floor, or the ground.
Let the body notice support and stability.
"""
        )
    }
