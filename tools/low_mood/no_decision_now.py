"""
Low Mood Tool: No Decision Right Now
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "name",
            "text": "Name one thing you don’t need to decide right now."
        }

    if step == "name":
        return {
            "step": "exit",
            "text": "You can come back to it later."
        }

    return {
        "step": "exit",
        "text": "Stopping here is okay."
    }
