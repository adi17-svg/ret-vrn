"""
Low Mood Tool: Thought Parking
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "park",
            "text": "Name one heavy thought you can set aside for now."
        }

    if step == "park":
        return {
            "step": "exit",
            "text": "You don’t need to solve it right now."
        }

    return {
        "step": "exit",
        "text": "Pause here."
    }
