from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Explain that anxiety can create strong body sensations like fast heartbeat
or tight chest.
Reassure that these sensations are uncomfortable but not dangerous.
Say the body is trying to protect them.
"""
        )
    }
