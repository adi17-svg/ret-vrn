"""
Low Mood Tool: Name the Feeling
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "name",
            "text": "Right now this feels like… (no story, no why)."
        }

    if step == "name":
        return {
            "step": "exit",
            "text": "Naming it is enough."
        }

    return {
        "step": "exit",
        "text": "We can stop here."
    }
