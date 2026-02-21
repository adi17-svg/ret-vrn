"""
Low Mood Tool: Body Check-In (Spiral Aware - Independent)

Design:
- Independent GPT usage (no shared wrapper)
- Safe classifier functions
- Spiral-aware tone (never mentioned to user)
- Linear step flow
- No loops
- Short, gentle responses only
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
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction: str, user_text: str, valid_options: list, default: str):

    if not user_text or len(user_text.strip()) < 2:
        return default

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip().upper()

        if result in valid_options:
            return result

        return default

    except:
        return default


# =====================================================
# CLASSIFIERS
# =====================================================

def classify_spiral(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.",
        user_text,
        ["BEIGE", "PURPLE", "RED", "BLUE", "ORANGE", "GREEN", "YELLOW"],
        "GREEN"
    )


def classify_yes_no(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: YES, NO, or UNCLEAR.",
        user_text,
        ["YES", "NO", "UNCLEAR"],
        "UNCLEAR"
    )


def classify_shift(user_text: str) -> str:
    return safe_classify(
        "Classify into one word: SUCCESS, NO_CHANGE, or UNCLEAR.",
        user_text,
        ["SUCCESS", "NO_CHANGE", "UNCLEAR"],
        "UNCLEAR"
    )


# =====================================================
# GPT REPLY
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly.
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

def handle(step=None, user_text=None, history=None):

    history = history or []
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # -------------------------------------------------
    # STEP 0 — START
    # -------------------------------------------------
    if step is None or step == "start":

        text = gpt_reply(
            history,
            """
Gently invite:
"Would it feel okay to take a moment to notice your body?"

Keep it optional and soft.
""",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # STEP 1 — PERMISSION
    # -------------------------------------------------
    if step == "permission":

        decision = classify_yes_no(user_text)

        if decision == "YES":

            text = gpt_reply(
                history,
                """
Ask gently:
"When you feel low like this, does your body feel heavy, tight, or tired anywhere?"

Add:
"If you're not sure, that's okay."
""",
                spiral_stage
            )

            return {"step": "scan", "text": text}

        if decision == "NO":

            text = gpt_reply(
                history,
                """
Acknowledge gently.
Let them know that's completely okay.
Close softly.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        # UNCLEAR
        text = gpt_reply(
            history,
            "Gently ask if they'd prefer to try noticing their body or just pause.",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # -------------------------------------------------
    # STEP 2 — SCAN
    # -------------------------------------------------
    if step == "scan":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

Briefly acknowledge.
Invite simply noticing that area for a few moments.
No changing.
""",
            spiral_stage
        )

        return {"step": "soften", "text": text}

    # -------------------------------------------------
    # STEP 3 — SOFTEN
    # -------------------------------------------------
    if step == "soften":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

Invite softening just 5%, if that feels okay.
Then gently ask:
"Did anything shift?"
""",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # -------------------------------------------------
    # STEP 4 — CHECK SHIFT
    # -------------------------------------------------
    if step == "check":

        result = classify_shift(user_text)

        if result == "SUCCESS":

            text = gpt_reply(
                history,
                """
Acknowledge the small shift warmly.
Invite staying briefly.
Close gently.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        if result == "NO_CHANGE":

            text = gpt_reply(
                history,
                """
Normalize that sometimes nothing shifts.
Invite one slow breath.
Close softly.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        # UNCLEAR
        text = gpt_reply(
            history,
            """
Gently ask if it feels the same or slightly different.
Keep it simple.
""",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------
    return {
        "step": "exit",
        "text": "We can pause here."
    }