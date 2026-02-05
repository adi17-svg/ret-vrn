from tool_gpt_anxiety import anxiety_gpt_reply

def handle(step=None, user_text=None):
    return {
        "step": "exit",
        "text": anxiety_gpt_reply(
            user_text,
            """
Explain that not every worry needs attention right now.
Offer the phrase “not now, I’ll come back later.”
Encourage returning attention to the present moment.
"""
        )
    }
