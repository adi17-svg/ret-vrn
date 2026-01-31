# backend/tools/low_mood/getting_going.py

"""
Low Mood Tool: Getting Going with Action

Rules:
- NO GPT
- NO interpretation
- Fixed steps
- User text ignored (only for continuity)
"""

def handle(step: str | None):
    """
    step: current step of the tool
    returns: next step + response text
    """

    if step is None or step == "start":
        return {
            "step": "identify_task",
            "text": "When you’re low, even small things feel heavy. What’s one tiny thing you’ve been putting off?"
        }

    if step == "identify_task":
        return {
            "step": "identify_resistance",
            "text": "That makes sense. What feels like the biggest block right now?"
        }

    if step == "identify_resistance":
        return {
            "step": "shrink_action",
            "text": "Let’s shrink it. What’s a version of this that takes under 2 minutes?"
        }

    if step == "shrink_action":
        return {
            "step": "permission",
            "text": "Would you like to try this tiny step now, or later?"
        }

    if step == "permission":
        return {
            "step": "exit",
            "text": "That’s okay either way. Even thinking about it counts. I’m here."
        }

    return {
        "step": "exit",
        "text": "We can pause here. Take care of yourself."
    }
