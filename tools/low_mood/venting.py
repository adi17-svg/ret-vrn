"""
Low Mood Tool: Vent Without Fixing
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "vent",
            "text": "You can let things out here. No fixing. No judging."
        }

    if step == "vent":
        return {
            "step": "contain",
            "text": "Thank you for letting that out."
        }

    if step == "contain":
        return {
            "step": "exit",
            "text": "You don’t have to solve it."
        }

    return {
        "step": "exit",
        "text": "We can pause here."
    }
