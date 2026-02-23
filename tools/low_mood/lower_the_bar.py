"""
Low Mood Tool: Lower The Bar
Conversational Version
- History aware (last 6 messages)
- Spiral-toned pressure reset
- No abrupt exit
- Continues conversation
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You gently reduce pressure.

Rules:
- Warm, calm tone
- No pushing
- No productivity coaching
- Encourage minimum viable effort only
- Keep responses short (2–4 lines)
- Help lower internal expectations safely
- Never expand goals upward
- Keep conversation open at the end
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
        "Classify emotional tone into one word: BLUE, RED, ORANGE, GREEN, or NEUTRAL.",
        user_text,
        ["BLUE", "RED", "ORANGE", "GREEN", "NEUTRAL"],
        "GREEN"
    )


# =====================================================
# SPIRAL LANGUAGE HELPERS
# =====================================================

def spiral_pressure_line(stage):

    if stage == "BLUE":
        return "When responsibility matters to you, slowing down can feel wrong."

    if stage == "ORANGE":
        return "When progress and achievement matter, falling behind feels heavy."

    if stage == "RED":
        return "When energy feels restless, structure can feel irritating."

    if stage == "GREEN":
        return "When everything feels emotionally heavy, even simple things feel big."

    return "When energy is low, everything can feel bigger than it is."


def spiral_minimum_question(stage):

    if stage == "BLUE":
        return "What would still feel responsible — but lighter?"

    if stage == "ORANGE":
        return "What’s the smallest measurable move that would still count?"

    if stage == "RED":
        return "What’s the smallest thing you wouldn’t mind doing?"

    if stage == "GREEN":
        return "What would feel kind to yourself today?"

    return "What would be the absolute minimum that would still count?"


def spiral_affirmation(stage):

    if stage == "BLUE":
        return "That still honors your sense of responsibility."

    if stage == "ORANGE":
        return "That still moves things forward."

    if stage == "RED":
        return "That keeps it simple."

    if stage == "GREEN":
        return "That feels gentle enough for today."

    return "That’s enough for today."


# =====================================================
# GPT REPLY (History Aware)
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_BASE},
    ]

    if history:
        recent = history[-HISTORY_LIMIT:]

        for msg in recent:
            role = "assistant" if msg.get("type") == "assistant" else "user"
            content = msg.get("text", "")
            if content:
                messages.append({
                    "role": role,
                    "content": content
                })

    messages.append({
        "role": "user",
        "content": instruction
    })

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    spiral_stage = classify_spiral(user_text)

    # ---------------------------------------------
    # STEP 1 — REFLECT PRESSURE
    # ---------------------------------------------

    if not step or step == "start":

        memory["spiral_stage"] = spiral_stage

        instruction = f"""
User said: "{user_text}"

1. Briefly reflect the pressure they seem to be carrying.
2. Use this tone framing if helpful: "{spiral_pressure_line(spiral_stage)}"
3. Normalize that low energy makes things feel bigger.
4. Ask this question gently: "{spiral_minimum_question(spiral_stage)}"
Keep it warm and simple.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "minimum",
            "text": text,
            "memory": memory
        }

    # ---------------------------------------------
    # STEP 2 — AFFIRM MINIMUM
    # ---------------------------------------------

    if step == "minimum":

        stage = memory.get("spiral_stage", "GREEN")

        instruction = f"""
User said their minimum is: "{user_text}"

1. Affirm that this is enough.
2. Use this supportive framing if helpful: "{spiral_affirmation(stage)}"
3. Reinforce that small counts.
4. Ask gently: "How does it feel to lower the bar just a little?"
Keep it grounded.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "continue",
            "text": text,
            "memory": memory
        }

    # ---------------------------------------------
    # CONTINUE MODE
    # ---------------------------------------------

    if step == "continue":

        instruction = f"""
User said: "{user_text}"

Stay aligned with reduced pressure.
Reinforce minimum effort.
Keep tone soft.
Do not increase expectations.
"""

        text = gpt_reply(history, instruction)

        return {
            "step": "continue",
            "text": text,
            "memory": memory
        }

    # ---------------------------------------------
    # FALLBACK
    # ---------------------------------------------

    return {
        "step": "continue",
        "text": "Small is enough for now.",
        "memory": memory
    }