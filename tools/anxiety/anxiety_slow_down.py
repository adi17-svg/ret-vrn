from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Reassure that slowing down is allowed.
Say there is no need to rush this moment.
Invite the body to move at a gentler pace.
"""
        )
    }
