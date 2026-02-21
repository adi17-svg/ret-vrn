"""
Low Mood Tool: It Makes Sense (Context + Spiral Aware)

Design:
- Independent GPT usage
- Spiral-aware tone (internal only)
- Uses full chat history
- Shame detection
- Self-compassion layering
- Gentle optional transition
- Clean exit logic
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, validating mental health guide.

Rules:
- Keep responses short (2–4 lines)
- Warm and natural tone
- No advice
- No fixing
- No analysis
- Just validate gently
"""

# =====================================================
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction, user_text, valid_options, default):

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


def classify_spiral(user_text):
    return safe_classify(
        "Classify into one word only: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.",
        user_text,
        ["BEIGE", "PURPLE", "RED", "BLUE", "ORANGE", "GREEN", "YELLOW"],
        "GREEN"
    )


def classify_yes_no(user_text):
    return safe_classify(
        "Classify into one word: YES, NO, or UNCLEAR.",
        user_text,
        ["YES", "NO", "UNCLEAR"],
        "UNCLEAR"
    )


# =====================================================
# SHAME DETECTION
# =====================================================

def detect_shame(user_text):

    if not user_text:
        return False

    shame_keywords = [
        "i'm stupid",
        "i am stupid",
        "i'm weak",
        "i am weak",
        "it's my fault",
        "i shouldn't feel",
        "i'm broken",
        "i am broken",
        "i'm too sensitive"
    ]

    lower = user_text.lower()
    return any(k in lower for k in shame_keywords)


# =====================================================
# GPT REPLY (SPIRAL + CONTEXT AWARE)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust validation tone subtly to match mindset.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []

    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"
    shame_detected = detect_shame(user_text)

    # =================================================
    # STEP 0 — VALIDATE
    # =================================================
    if step is None or step == "start":

        instruction = """
Reflect their emotional experience briefly.
Validate that their reaction makes sense given what they're facing.
Keep it human and grounded.
Add one gentle self-compassion line.
"""

        if shame_detected:
            instruction += """
Gently soften self-judgment.
Reduce shame without arguing or correcting them.
"""

        instruction += """
Close with:
"If you'd like, we can take a small step next."
Keep it optional.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "transition", "text": text}

    # =================================================
    # STEP 1 — TRANSITION HANDLER
    # =================================================
    if step == "transition":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":

            text = gpt_reply(
                history,
                """
Acknowledge their openness warmly.
Suggest one very small, optional next step
(like one slow breath or noticing the room).
Keep it gentle and brief.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        if decision == "NO":

            text = gpt_reply(
                history,
                """
Acknowledge gently.
Reinforce that just sharing this already matters.
Close warmly.
""",
                spiral_stage
            )

            return {"step": "exit", "text": text}

        # UNCLEAR → neutral close
        text = gpt_reply(
            history,
            """
Let them know it's okay to pause.
Reassure them they're not alone in this.
Close softly.
""",
            spiral_stage
        )

        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {"step": "exit", "text": "We can pause here."}