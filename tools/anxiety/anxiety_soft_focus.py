from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Guide the eyes to rest on one neutral or gentle object.
Avoid scanning the room.
Encourage soft, relaxed focus for a few breaths.
"""
        )
    }
