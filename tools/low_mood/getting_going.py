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
# # backend/tools/low_mood/getting_going.py

# """
# Low Mood Tool: Getting Going

# Design:
# - USE GPT (lightly, for framing only)
# - Tool controls flow via steps
# - User text is used, but NOT deeply analyzed
# - Goal: gently move user toward tiny action

# Flow:
# start → normalize → tiny_ask → pick → act → close
# """

# from spiral_dynamics import client


# SYSTEM_PROMPT = """
# You are a calm, supportive mental health coach.
# This is a guided exercise for low energy and procrastination.

# Rules:
# - Keep responses short
# - Be gentle, never pushy
# - Do NOT analyze deeply
# - Always guide toward a very small action
# - No advice dumping
# """


# def gpt_reply(user_text: str | None, instruction: str) -> str:
#     messages = [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {
#             "role": "user",
#             "content": f"""
# User said:
# {user_text or "(no response)"}

# Instruction:
# {instruction}
# """
#         }
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1",
#         messages=messages,
#         temperature=0.4,
#     )

#     return resp.choices[0].message.content.strip()


# def handle(step: str | None, user_text: str | None):
#     # STEP 0 — INTRO / NORMALIZE
#     if step is None or step == "start":
#         text = gpt_reply(
#             user_text,
#             "Normalize low energy. Make the user feel understood. No questions yet."
#         )
#         return {"step": "tiny_ask", "text": text}

#     # STEP 1 — ASK FOR TINY THING
#     if step == "tiny_ask":
#         text = gpt_reply(
#             user_text,
#             "Ask for one very small thing they’ve been putting off. Keep it non-threatening."
#         )
#         return {"step": "pick", "text": text}

#     # STEP 2 — PICK / SHRINK
#     if step == "pick":
#         text = gpt_reply(
#             user_text,
#             "Acknowledge their response and shrink it into a 30–60 second version."
#         )
#         return {"step": "act", "text": text}

#     # STEP 3 — INVITE ACTION
#     if step == "act":
#         text = gpt_reply(
#             user_text,
#             "Invite them to try the tiny action now. Make it optional and safe."
#         )
#         return {"step": "close", "text": text}

#     # STEP 4 — CLOSE
#     if step == "close":
#         text = gpt_reply(
#             user_text,
#             "Close warmly. Reinforce that effort matters even if they don’t act."
#         )
#         return {"step": "exit", "text": text}

#     # FALLBACK
#     return {
#         "step": "exit",
#         "text": "We can pause here. I’m here whenever you want to try again."
#     }
"""
Low Mood Tool: Getting Going With Action

Design principles:
- GPT used only for tone + continuity
- Tool controls the flow strictly
- No step ever repeats the same question
- Always acknowledge → reframe → advance
"""

from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Sound natural and human
- Do NOT repeat the same question
- Do NOT analyze deeply
- ALWAYS move the exercise forward
"""

def gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction}
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


def handle(step: str | None, user_text: str | None):

    # STEP 0 — INTRO / NORMALIZE (NO USER DEPENDENCE)
    if step is None or step == "start":
        text = gpt_reply(
            user_text,
            """
Normalize low energy.
Explain we start small.
End by asking what feels hardest to begin.
"""
        )
        return {"step": "ack", "text": text}

    # STEP 1 — ACKNOWLEDGE USER RESPONSE (NO REPEAT)
    if step == "ack":
        text = gpt_reply(
            user_text,
            """
Acknowledge what the user said in one line.
Do NOT repeat the same question.
Gently reflect difficulty.
"""
        )
        return {"step": "shrink", "text": text}

    # STEP 2 — SHRINK THE TASK
    if step == "shrink":
        text = gpt_reply(
            user_text,
            """
Acknowledge briefly.
Then propose ONE extremely small action
that takes about 30 seconds.
No questions.
"""
        )
        return {"step": "act", "text": text}

    # STEP 3 — INVITE ACTION (OPTIONAL, NOW)
    if step == "act":
        text = gpt_reply(
            user_text,
            """
Invite them to try the tiny action now.
Make it optional and low pressure.
"""
        )
        return {"step": "close", "text": text}

    # STEP 4 — CLOSE (NO LOOP)
    if step == "close":
        text = gpt_reply(
            user_text,
            """
Close warmly.
Reinforce that effort or showing up matters.
End the exercise.
"""
        )
        return {"step": "exit", "text": text}

    # SAFETY FALLBACK
    return {
        "step": "exit",
        "text": "We can pause here. Showing up is enough for now."
    }
