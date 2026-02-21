"""
Low Mood Tool: Lower The Bar (Context + Spiral Aware)

Design:
- Independent GPT usage
- Uses full chat history
- Spiral-aware tone (internal only)
- Reduces pressure gently
- Encourages minimum viable effort
- No advice, no pushing
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You gently reduce pressure.

Rules:
- Warm, calm tone
- No pushing
- No advice
- No productivity coaching
- Encourage minimum effort only
- Keep responses short (2–4 lines)
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


# =====================================================
# GPT REPLY (CONTEXT + SPIRAL AWARE)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly to match mindset.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Include full previous conversation context
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

    # =================================================
    # STEP 0 — REFLECT PRESSURE
    # =================================================
    if step is None or step == "start":

        instruction = """
Briefly reflect the pressure or heaviness they seem to be carrying.
Normalize that when energy is low, everything feels bigger.
Then gently ask:
"If today didn't have to be perfect, what would be the absolute minimum that would be enough?"
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "minimum", "text": text}

    # =================================================
    # STEP 1 — AFFIRM MINIMUM
    # =================================================
    if step == "minimum":

        instruction = """
Affirm that their chosen minimum is enough for today.
Reinforce that small counts.
Do not expand goals.
Close gently.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {"step": "exit", "text": "We can stop here."}