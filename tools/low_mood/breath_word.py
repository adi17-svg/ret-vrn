"""
Low Mood Tool: Breath + Word
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {
            "step": "breathe",
            "text": "Inhale: Here. Exhale: Now. Do this three times."
        }

    if step == "breathe":
        return {
            "step": "exit",
            "text": "Let your breath return naturally."
        }

    return {
        "step": "exit",
        "text": "We can stop."
    }
