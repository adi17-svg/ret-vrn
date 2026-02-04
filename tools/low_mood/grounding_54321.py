"""
Low Mood Tool: Grounding 5-4-3-2-1
"""

def handle(step: str | None):
    if step in (None, "start"):
        return {"step": "five", "text": "Name 5 things you can see around you."}

    if step == "five":
        return {"step": "four", "text": "Notice 4 things you can feel with your body."}

    if step == "four":
        return {"step": "three", "text": "Listen for 3 different sounds."}

    if step == "three":
        return {"step": "two", "text": "Notice 2 things you can smell."}

    if step == "two":
        return {"step": "one", "text": "Name 1 thing you can taste or enjoy."}

    return {
        "step": "exit",
        "text": "You’re here, in this moment. That’s enough."
    }
