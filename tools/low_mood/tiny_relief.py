"""
Low Mood Tool: Tiny Relief
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "find",
            "text": "Is there anything that feels even 1% okay?"
        }

    if step == "find":
        return {
            "step": "stay",
            "text": "Stay with that feeling for about 10 seconds."
        }

    if step == "stay":
        return {
            "step": "exit",
            "text": "That’s enough for now."
        }

    return {
        "step": "exit",
        "text": "We can pause."
    }
