"""
Low Mood Tool: Self Compassion
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "acknowledge",
            "text": "This is a hard moment. You’re not weak for feeling this way."
        }

    if step == "acknowledge":
        return {
            "step": "normalize",
            "text": "Many people feel like this sometimes. You’re not alone."
        }

    if step == "normalize":
        return {
            "step": "exit",
            "text": "You don’t have to fix anything right now."
        }

    return {
        "step": "exit",
        "text": "We can pause here."
    }
