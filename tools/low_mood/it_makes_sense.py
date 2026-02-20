"""
Low Mood Tool: It Makes Sense (Enhanced)

Added:
- Spiral-aware validation (internal only)
- Self-compassion layering
- Shame-release micro script
- Gentle transition system
- Independent GPT usage
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
- Warm, natural tone
- No advice
- No fixing
- No analysis
- Just validate gently
"""

# =====================================================
# SPIRAL CLASSIFIER (INTERNAL ONLY)
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
# SELF-SHAME DETECTION
# =====================================================

def detect_shame(user_text: str) -> bool:
    keywords = [
        "i'm stupid", "i'm weak", "i'm overreacting",
        "i shouldn't feel", "it's my fault",
        "i'm broken", "i'm too sensitive"
    ]
    if not user_text:
        return False
    lower = user_text.lower()
    return any(k in lower for k in keywords)


# =====================================================
# GPT REPLY (SPIRAL-AWARE)
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

    spiral_stage = classify_spiral(user_text) if user_text else None
    shame_detected = detect_shame(user_text)

    # =================================================
    # STEP 1 — VALIDATE CORE
    # =================================================
    if step is None or step == "start":

        instruction = """
Validate that their reaction makes sense
given what they’re dealing with.

Keep it human and natural.
"""

        # Self-compassion layering
        instruction += """
Add one gentle self-compassion line
(e.g., "Anyone in your place might feel this.").
"""

        # Shame-release micro script
        if shame_detected:
            instruction += """
Gently reduce shame.
Reframe self-judgment softly.
Do not argue.
"""

        # Gentle transition
        instruction += """
Close with a soft transition line like:
"If you'd like, we can take a small step next."
No pressure.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "transition", "text": text}

    # =================================================
    # STEP 2 — TRANSITION HANDLER
    # =================================================
    if step == "transition":

        if not user_text:
            return {"step": "exit", "text": "We can pause here."}

        lower = user_text.lower().strip()

        if lower in ["yes", "okay", "ok", "sure", "let's try"]:
            text = gpt_reply(
                history,
                """
Acknowledge their openness.
Suggest one very gentle next step
like a slow breath or grounding moment.
Keep it optional.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        # If no / hesitation
        text = gpt_reply(
            history,
            """
Acknowledge gently.
Reinforce that just being here counts.
Close warmly.
""",
            spiral_stage
        )

        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {"step": "exit", "text": "We can pause here."}
