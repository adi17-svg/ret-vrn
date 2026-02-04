"""
Low Mood Tool: Gentle Distraction
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "choose",
            "text": "Name one neutral activity you could do for 2 minutes."
        }

    if step == "choose":
        return {
            "step": "exit",
            "text": "You can stop after 2 minutes."
        }

    return {
        "step": "exit",
        "text": "Pause here."
    }
