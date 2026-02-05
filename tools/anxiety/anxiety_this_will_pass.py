from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Reassure that anxiety is a temporary state, not permanent.
Say it will change, even if slowly.
Encourage patience without rushing the feeling away.
"""
        )
    }
