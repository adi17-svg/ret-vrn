"""
Low Mood Tool: Name The Feeling (Advanced Conversational Version)

Flow:
User shares
→ Invite naming (open)
→ If unclear → offer clusters
→ Reflect word
→ Scale intensity
→ Body location
→ Normalize
→ Offer 3 micro directions
→ Continue (not exit)

Features:
- History aware (last 6 messages)
- Spiral-toned language (subtle)
- No abrupt exit
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You gently guide emotional labeling.

Rules:
- Calm tone
- No analysis
- No advice
- No fixing
- Keep responses short (2–4 lines)
- Help user name, measure, and notice emotion
- Keep conversation open
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
        "Classify tone into one word: BLUE, RED, ORANGE, GREEN, NEUTRAL.",
        user_text,
        ["BLUE", "RED", "ORANGE", "GREEN", "NEUTRAL"],
        "GREEN"
    )


def classify_unclear(user_text):
    if not user_text:
        return True

    low = user_text.lower().strip()
    unclear_patterns = [
        "don't know",
        "dont know",
        "idk",
        "not sure",
        "mixed",
        "everything"
    ]

    return any(p in low for p in unclear_patterns)


# =====================================================
# SPIRAL TONE LAYER
# =====================================================

def spiral_tone_line(stage):
    if stage == "BLUE":
        return "Naming it honestly matters."
    if stage == "ORANGE":
        return "Clarity helps you move forward."
    if stage == "RED":
        return "Even pausing to name it slows things down."
    if stage == "GREEN":
        return "Staying with it gently matters."
    return ""


# =====================================================
# GPT REPLY
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_BASE}
    ]

    if history:
        recent = history[-HISTORY_LIMIT:]
        for msg in recent:
            role = "assistant" if msg.get("type") == "assistant" else "user"
            text = msg.get("text", "")
            if text:
                messages.append({"role": role, "content": text})

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

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    spiral_stage = classify_spiral(user_text)

    # -------------------------------------------------
    # STEP 1 — INVITE NAMING
    # -------------------------------------------------

    if not step or step == "start":

        memory["spiral"] = spiral_stage

        instruction = """
User seems emotionally unclear or heavy.

Invite them gently:
"If this feeling had one simple name, what might it be?"
Keep it open.
"""

        text = gpt_reply(history, instruction)

        return {"step": "naming", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 2 — HANDLE NAMING
    # -------------------------------------------------

    if step == "naming":

        if classify_unclear(user_text):
            instruction = """
User is unsure.

Offer gentle emotion clusters:
- sadness
- frustration
- loneliness
- pressure
- anger
Ask which feels closest.
"""

            text = gpt_reply(history, instruction)
            return {"step": "naming", "text": text, "memory": memory}

        memory["emotion"] = user_text

        instruction = f"""
User named emotion: "{user_text}"

Reflect the word simply.
Add: "{spiral_tone_line(memory.get('spiral'))}"
Then ask:
"If 10 is very intense and 1 is light, where does it fall right now?"
"""

        text = gpt_reply(history, instruction)

        return {"step": "scale", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 3 — SCALE
    # -------------------------------------------------

    if step == "scale":

        memory["intensity"] = user_text

        instruction = """
Acknowledge the number briefly.
Ask:
"Where do you notice this most in your body — chest, stomach, head?"
"""

        text = gpt_reply(history, instruction)

        return {"step": "body", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 4 — BODY
    # -------------------------------------------------

    if step == "body":

        memory["body_location"] = user_text

        instruction = """
Normalize gently.
Acknowledge that noticing it there matters.
Then offer three options:

Would you like to:
- soften it a little
- stay with it gently
- shift your focus for a moment

Keep it simple.
"""

        text = gpt_reply(history, instruction)

        return {"step": "direction", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 5 — DIRECTION
    # -------------------------------------------------

    if step == "direction":

        instruction = f"""
User chose: "{user_text}"

Respond aligned with their choice.
Keep tone gentle.
Do not exit.
Keep conversation open.
"""

        text = gpt_reply(history, instruction)

        return {"step": "continue", "text": text, "memory": memory}


    # -------------------------------------------------
    # CONTINUE MODE
    # -------------------------------------------------

    if step == "continue":

        instruction = f"""
User said: "{user_text}"

Stay aligned with emotional regulation.
Keep tone soft.
Do not escalate.
Keep conversation open.
"""

        text = gpt_reply(history, instruction)

        return {"step": "continue", "text": text, "memory": memory}


    return {"step": "continue", "text": "Take your time.", "memory": memory}