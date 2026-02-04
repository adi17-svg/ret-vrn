"""
Low Mood Tool: It Makes Sense
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "validate",
            "text": "Given what you’re dealing with, this reaction makes sense."
        }

    if step == "validate":
        return {
            "step": "exit",
            "text": "You’re not overreacting."
        }

    return {
        "step": "exit",
        "text": "Pause here."
    }
