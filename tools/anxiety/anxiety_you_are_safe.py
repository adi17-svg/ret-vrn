from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Invite a brief pause.
Reassure that in this moment, they are safe.
Say nothing needs to be solved immediately.
"""
        )
    }
