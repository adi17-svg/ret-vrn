"""
Low Mood Tool: One Safe Thing
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "identify",
            "text": "Name one thing that feels safe right now."
        }

    if step == "identify":
        return {
            "step": "focus",
            "text": "Let your attention rest there briefly."
        }

    if step == "focus":
        return {
            "step": "exit",
            "text": "You’re safe in this moment."
        }

    return {
        "step": "exit",
        "text": "Stopping here is okay."
    }
