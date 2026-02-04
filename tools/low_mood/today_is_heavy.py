"""
Low Mood Tool: Today Is Heavy
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "acknowledge",
            "text": "Some days feel heavier than others. Today might be one."
        }

    if step == "acknowledge":
        return {
            "step": "exit",
            "text": "You’re allowed to go slower today."
        }

    return {
        "step": "exit",
        "text": "That’s enough."
    }
