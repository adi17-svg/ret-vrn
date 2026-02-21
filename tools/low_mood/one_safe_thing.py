"""
Low Mood Tool: One Safe Thing (Context + Spiral Aware)

Design:
- Independent GPT usage
- Uses full chat history
- Spiral-aware tone (internal only)
- Safety anchoring only
- No advice, no analysis
- Gentle nervous system regulation
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You guide safety anchoring gently.

Rules:
- Calm tone
- No fixing
- No analysis
- No problem solving
- Keep responses short (2–4 lines)
- Focus only on safety and grounding
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

    # Include full previous conversation
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
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # =================================================
    # STEP 0 — IDENTIFY SAFE THING
    # =================================================
    if step is None or step == "start":

        instruction = """
Gently invite them to name one thing that feels even slightly safe or steady right now.
Keep it simple.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "identify", "text": text}

    # =================================================
    # STEP 1 — REST ATTENTION THERE
    # =================================================
    if step == "identify":

        instruction = f"""
User said: "{user_text}"

Acknowledge the safe thing briefly.
Invite resting attention there for a few moments.
Keep tone calm and grounding.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "focus", "text": text}

    # =================================================
    # STEP 2 — CONTAINMENT CLOSE
    # =================================================
    if step == "focus":

        instruction = """
Reinforce that even noticing one safe thing matters.
Remind them they are here in this moment.
Close gently.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {"step": "exit", "text": "You’re safe in this moment."}