"""
Low Mood Tool: Body Check-In
Permission + Adaptive + Spiral-Aware
Independent GPT Version
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, grounding mental health guide.

Rules:
- Keep responses short (1–3 lines)
- Speak gently and naturally
- No advice
- No analysis
- No fixing
- Just guide awareness
"""

# =====================================================
# SPIRAL CLASSIFIER (INTERNAL USE ONLY)
# =====================================================

def classify_spiral(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": """
Classify the user's mindset tendency into one word only:
BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.

Respond with one word only.
"""
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# =====================================================
# YES / NO CLASSIFIER
# =====================================================

def classify_yes_no(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Classify into one word only: YES, NO, or UNCLEAR."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# =====================================================
# SHIFT CLASSIFIER
# =====================================================

def classify_shift(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Classify into one word only: SUCCESS, NO_CHANGE, or UNCLEAR."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# =====================================================
# GPT REPLY (SPIRAL-AWARE)
# =====================================================

def gpt_reply(history: list | None, instruction: str, spiral_stage: str | None) -> str:

    system_prompt = SYSTEM_PROMPT_BASE

    # Inject spiral tone adaptation (hidden from user)
    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly to match that mindset.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step: str | None, user_text: str | None, history: list | None = None):

    history = history or []

    # Spiral detection only when user speaks
    spiral_stage = None
    if user_text:
        spiral_stage = classify_spiral(user_text)

    # =================================================
    # STEP 1 — ASK PERMISSION
    # =================================================
    if step is None or step == "start":
        text = gpt_reply(
            history,
            """
Ask gently:
"Would it feel okay to take a moment to notice your body together?"

Keep it soft and optional.
""",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # =================================================
    # STEP 2 — HANDLE PERMISSION RESPONSE
    # =================================================
    if step == "permission":

        decision = classify_yes_no(user_text or "")

        # YES → Continue
        if decision == "YES":
            text = gpt_reply(
                history,
                """
Ask gently:
"When you feel low like this, does your body feel heavy, tight, or tired anywhere?"

Add: "If you're not sure, that's okay."
""",
                spiral_stage
            )
            return {"step": "scan", "text": text}

        # NO → Exit gracefully
        if decision == "NO":
            text = gpt_reply(
                history,
                """
Acknowledge their choice warmly.
Let them know that's completely okay.
Offer to stay present in another way.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # UNCLEAR → Clarify
        text = gpt_reply(
            history,
            """
Gently ask if they'd prefer to try a body check-in,
or talk about what's on their mind instead.
""",
            spiral_stage
        )
        return {"step": "permission", "text": text}

    # =================================================
    # STEP 3 — NOTICE AREA
    # =================================================
    if step == "scan":
        text = gpt_reply(
            history,
            f"""
The user said: "{user_text}"

Briefly acknowledge what they shared.
Invite them to simply notice that area for a few seconds.
No changing. Just observing.
""",
            spiral_stage
        )
        return {"step": "release", "text": text}

    # =================================================
    # STEP 4 — INVITE SOFTENING
    # =================================================
    if step == "release":
        text = gpt_reply(
            history,
            f"""
The user said: "{user_text}"

Invite softening that area just 5%, if it feels okay.
Then gently ask:
"Did anything shift, even a little?"
""",
            spiral_stage
        )
        return {"step": "check_shift", "text": text}

    # =================================================
    # STEP 5 — CHECK SHIFT
    # =================================================
    if step == "check_shift":

        classification = classify_shift(user_text or "")

        # SUCCESS
        if classification == "SUCCESS":
            text = gpt_reply(
                history,
                """
Acknowledge the small shift warmly.
Invite them to stay with it briefly.
Close gently.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # NO CHANGE
        if classification == "NO_CHANGE":
            text = gpt_reply(
                history,
                """
Reassure them it's completely okay if nothing changed.
Invite one slow breath with that area.
No pressure.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # UNCLEAR
        text = gpt_reply(
            history,
            """
Gently ask if it feels the same, slightly softer, or hard to tell.
Keep it simple.
""",
            spiral_stage
        )
        return {"step": "check_shift", "text": text}

    # =================================================
    # SAFETY FALLBACK
    # =================================================
    return {
        "step": "exit",
        "text": "We can pause here."
    }
