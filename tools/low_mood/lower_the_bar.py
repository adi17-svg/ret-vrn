"""
Low Mood Tool: Lower the Bar
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "minimum",
            "text": "What’s the absolute minimum that would be enough today?"
        }

    if step == "minimum":
        return {
            "step": "exit",
            "text": "That is enough."
        }

    return {
        "step": "exit",
        "text": "We can stop here."
    }
