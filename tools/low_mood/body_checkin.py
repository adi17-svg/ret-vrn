"""
Low Mood Tool: Body Check-In
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "scan",
            "text": "Notice your shoulders, jaw, and hands."
        }

    if step == "scan":
        return {
            "step": "release",
            "text": "Let one of these places soften slightly."
        }

    if step == "release":
        return {
            "step": "exit",
            "text": "That’s enough for now."
        }

    return {
        "step": "exit",
        "text": "Stopping here is okay."
    }
