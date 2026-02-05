from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Guide a slow breathing rhythm:
inhale through the nose for four,
hold gently for seven,
exhale slowly through the mouth for eight.
Keep the tone steady and calm.
"""
        )
    }
