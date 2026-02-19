"""
Low Mood Tool: 5-4-3-2-1 Grounding (Enhanced)

Added:
- Permission version
- Spiral-aware tone (internal only)
- Energy adaptive pacing
- Sensory skip option
- Adaptive exit
- Independent GPT usage
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a grounding guide.

Rules:
- Calm tone
- Short steps
- No analysis
- Step-by-step only
- Keep language simple
"""

# =====================================================
# SPIRAL CLASSIFIER (INTERNAL)
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
# ENERGY LEVEL CLASSIFIER
# =====================================================

def classify_energy(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "Classify energy level into one word: LOW, MEDIUM, HIGH."
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
            {"role": "system", "content": "Classify into one word: YES, NO, or UNCLEAR."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# =====================================================
# GPT REPLY (SPIRAL-AWARE)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

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
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []

    spiral_stage = classify_spiral(user_text) if user_text else None
    energy_level = classify_energy(user_text) if user_text else "MEDIUM"

    # =================================================
    # STEP 0 — ASK PERMISSION
    # =================================================
    if step is None or step == "start":

        text = gpt_reply(
            history,
            """
Ask gently:
"Would it feel okay to try a short grounding exercise together?"

Keep it optional.
""",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # =================================================
    # STEP 1 — HANDLE PERMISSION
    # =================================================
    if step == "permission":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":
            return {"step": "five", "text": _step_five(history, spiral_stage, energy_level)}

        text = gpt_reply(
            history,
            "Acknowledge gently. Let them know pausing is okay.",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # =================================================
    # 5 THINGS YOU SEE
    # =================================================
    if step == "five":
        return {"step": "four", "text": _step_four(history, spiral_stage, energy_level)}

    # =================================================
    # 4 SENSATIONS (SKIPPABLE)
    # =================================================
    if step == "four":

        if user_text and user_text.lower().strip() in ["skip", "can't", "not sure"]:
            return {"step": "three", "text": _step_three(history, spiral_stage, energy_level)}

        return {"step": "three", "text": _step_three(history, spiral_stage, energy_level)}

    # =================================================
    # 3 SOUNDS
    # =================================================
    if step == "three":
        return {"step": "two", "text": _step_two(history, spiral_stage, energy_level)}

    # =================================================
    # 2 SMELLS (SKIPPABLE)
    # =================================================
    if step == "two":

        if user_text and user_text.lower().strip() in ["skip", "none"]:
            return {"step": "one", "text": _step_one(history, spiral_stage, energy_level)}

        return {"step": "one", "text": _step_one(history, spiral_stage, energy_level)}

    # =================================================
    # 1 TASTE / SENSATION
    # =================================================
    if step == "one":

        text = gpt_reply(
            history,
            """
Invite noticing one taste or small pleasant sensation.

Then gently ask:
"How does your body feel now?"
""",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # =================================================
    # ADAPTIVE EXIT
    # =================================================
    if step == "check":

        text = gpt_reply(
            history,
            f"""
User said: "{user_text}"

If calmer, acknowledge.
If same, normalize.
If still unsettled, suggest one slow breath.
Close warmly.
""",
            spiral_stage
        )

        return {"step": "exit", "text": text}

    return {"step": "exit", "text": "You’re here. That’s enough for now."}


# =====================================================
# STEP HELPERS (ENERGY ADAPTIVE PACING)
# =====================================================

def _step_five(history, spiral_stage, energy_level):
    speed = "slowly" if energy_level == "LOW" else "steadily"
    return gpt_reply(
        history,
        f"Invite naming five things you can see. Move {speed}.",
        spiral_stage
    )

def _step_four(history, spiral_stage, energy_level):
    speed = "gently" if energy_level == "LOW" else "clearly"
    return gpt_reply(
        history,
        f"Invite noticing four physical sensations. Move {speed}.",
        spiral_stage
    )

def _step_three(history, spiral_stage, energy_level):
    return gpt_reply(
        history,
        "Invite listening for three sounds around you.",
        spiral_stage
    )

def _step_two(history, spiral_stage, energy_level):
    return gpt_reply(
        history,
        "Invite noticing two smells. If none, that's okay.",
        spiral_stage
    )

def _step_one(history, spiral_stage, energy_level):
    return gpt_reply(
        history,
        "Invite noticing one taste or small pleasant sensation.",
        spiral_stage
    )
