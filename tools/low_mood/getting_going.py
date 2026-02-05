# # backend/tools/low_mood/getting_going.py

# """
# Low Mood Tool: Getting Going with Action

# Rules:
# - NO GPT
# - NO interpretation
# - Fixed steps
# - User text ignored (only for continuity)
# """

# def handle(step: str | None):
#     """
#     step: current step of the tool
#     returns: next step + response text
#     """

#     if step is None or step == "start":
#         return {
#             "step": "identify_task",
#             "text": "When you’re low, even small things feel heavy. What’s one tiny thing you’ve been putting off?"
#         }

#     if step == "identify_task":
#         return {
#             "step": "identify_resistance",
#             "text": "That makes sense. What feels like the biggest block right now?"
#         }

#     if step == "identify_resistance":
#         return {
#             "step": "shrink_action",
#             "text": "Let’s shrink it. What’s a version of this that takes under 2 minutes?"
#         }

#     if step == "shrink_action":
#         return {
#             "step": "permission",
#             "text": "Would you like to try this tiny step now, or later?"
#         }

#     if step == "permission":
#         return {
#             "step": "exit",
#             "text": "That’s okay either way. Even thinking about it counts. I’m here."
#         }

#     return {
#         "step": "exit",
#         "text": "We can pause here. Take care of yourself."
#     }
# backend/tools/low_mood/getting_going.py

"""
Low Mood Tool: Getting Going with Action (Wysa-style)

Rules:
- NO GPT
- NO interpretation
- Simple bucket logic
- Predictable, safe flow
- User input is acknowledged, not analyzed
"""


def bucketize(text: str | None) -> str:
    """
    Very simple buckets.
    This is NOT NLP. This is safety routing.
    """
    if not text or not text.strip():
        return "silence"

    t = text.lower().strip()

    if len(t.split()) <= 2:
        return "unclear"

    if "everything" in t or "all" in t:
        return "overwhelmed"

    if t in ["yes", "yeah", "ok", "okay", "sure"]:
        return "yes"

    if "no" in t or "not now" in t:
        return "no"

    return "something"


def handle(step: str | None = None, user_text: str | None = None):
    """
    step: current step of the tool
    user_text: whatever the user typed (meaning ignored, bucketed)
    returns: next step + response text
    """

    # --------------------------------------------------
    # STEP 0 — INTRO
    # --------------------------------------------------
    if step is None or step == "start":
        return {
            "step": "ask_tiny",
            "text": (
                "When energy is low, even small things feel heavy. "
                "What’s one tiny thing you’ve been putting off?"
            )
        }

    # --------------------------------------------------
    # STEP 1 — USER RESPONDS (ANYTHING)
    # --------------------------------------------------
    if step == "ask_tiny":
        bucket = bucketize(user_text)

        # User unsure / overwhelmed / silent
        if bucket in ["silence", "unclear", "overwhelmed"]:
            return {
                "step": "normalize",
                "text": (
                    "That makes sense. When everything feels heavy, "
                    "it’s really hard to pick just one thing."
                )
            }

        # User said something concrete (or at least something)
        return {
            "step": "shrink",
            "text": (
                "Okay. Let’s make it even smaller. "
                "What’s a version of that which takes under 30 seconds?"
            )
        }

    # --------------------------------------------------
    # STEP 2 — NORMALIZE + OFFER EXAMPLES
    # --------------------------------------------------
    if step == "normalize":
        return {
            "step": "suggest",
            "text": (
                "We can choose something very small — like standing up, "
                "opening one app, or taking one deep breath."
            )
        }

    # --------------------------------------------------
    # STEP 3 — INVITE ACTION (NO PRESSURE)
    # --------------------------------------------------
    if step == "suggest" or step == "shrink":
        return {
            "step": "invite",
            "text": (
                "If it feels okay, try doing just 30 seconds of that. "
                "No need to do more."
            )
        }

    # --------------------------------------------------
    # STEP 4 — CLOSE (SAFE EXIT)
    # --------------------------------------------------
    if step == "invite":
        bucket = bucketize(user_text)

        if bucket == "no":
            return {
                "step": "close",
                "text": (
                    "That’s okay. There’s no rush. "
                    "Even thinking about it counts."
                )
            }

        return {
            "step": "close",
            "text": (
                "You can stop anytime. "
                "I’m here, and you did enough for now."
            )
        }

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------
    return {
        "step": "close",
        "text": "We can pause here. Take care of yourself."
    }
