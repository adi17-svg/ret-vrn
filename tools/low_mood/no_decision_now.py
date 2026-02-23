"""
Low Mood Tool: No Decision Now (Spiral Integrated + Conversational)

- History aware (last 6 messages)
- Spiral tone modulation
- No solving
- No pros/cons
- No abrupt exit
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You gently reduce decision pressure.

Rules:
- Do NOT solve the decision
- Do NOT give advice
- Do NOT analyze pros/cons
- Reduce urgency
- Keep responses short (2–4 lines)
- Keep conversation open
"""


# =====================================================
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction, user_text, valid_options, default):
    if not user_text or len(user_text.strip()) < 2:
        return default

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0
        )

        result = resp.choices[0].message.content.strip().upper()
        if result in valid_options:
            return result

        return default
    except:
        return default


def detect_spiral_stage(user_text):
    return safe_classify(
        "Classify emotional tone into one word: BLUE, RED, ORANGE, GREEN, NEUTRAL.",
        user_text,
        ["BLUE", "RED", "ORANGE", "GREEN", "NEUTRAL"],
        "GREEN"
    )


# =====================================================
# SPIRAL TONE LINES
# =====================================================

def spiral_reflect(stage):
    if stage == "BLUE":
        return "When responsibility matters to you, decisions can feel especially heavy."
    if stage == "ORANGE":
        return "When progress matters, being stuck can feel frustrating."
    if stage == "RED":
        return "Being pushed to decide can feel irritating."
    if stage == "GREEN":
        return "When everything feels emotionally heavy, even choices feel bigger."
    return "Decisions can feel heavier when energy is low."


def spiral_release(stage):
    if stage == "BLUE":
        return "Responsible decisions deserve steady energy."
    if stage == "ORANGE":
        return "Decisions are clearer when your mind isn’t overloaded."
    if stage == "RED":
        return "You don’t have to force it right now."
    if stage == "GREEN":
        return "Giving yourself space before deciding is allowed."
    return "You don’t have to decide this right now."


# =====================================================
# GPT REPLY
# =====================================================

def gpt_reply(history, instruction):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        recent = history[-HISTORY_LIMIT:]
        for msg in recent:
            role = "assistant" if msg.get("type") == "assistant" else "user"
            text = msg.get("text", "")
            if text:
                messages.append({"role": role, "content": text})

    messages.append({"role": "user", "content": instruction})

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    stage = detect_spiral_stage(user_text)
    memory["spiral_stage"] = stage

    # -------------------------------------------------
    # STEP 1 — REFLECT + INVITE DECISION
    # -------------------------------------------------

    if not step or step == "start":

        instruction = f"""
User feels decision pressure.

1. Reflect using:
"{spiral_reflect(stage)}"

2. Normalize that low energy increases pressure.

3. Ask gently:
"What’s the one decision that feels most urgent right now?"
"""

        text = gpt_reply(history, instruction)

        return {"step": "name_decision", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 2 — RELEASE URGENCY
    # -------------------------------------------------

    if step == "name_decision":

        memory["decision"] = user_text

        instruction = f"""
User decision: "{user_text}"

1. Acknowledge briefly.
2. Say:
"{spiral_release(stage)}"
3. Tell them it does not need to be decided in this moment.
4. Invite them to imagine placing it aside gently.
5. Ask what shifts in their body.
"""

        text = gpt_reply(history, instruction)

        return {"step": "body_check", "text": text, "memory": memory}


    # -------------------------------------------------
    # STEP 3 — OFFER DIRECTIONS
    # -------------------------------------------------

    if step == "body_check":

        instruction = """
Acknowledge whatever they noticed.

Then offer three gentle options:
- sit with this space
- shift focus briefly
- explore what feels underneath the pressure

Keep it calm.
Do not exit.
"""

        text = gpt_reply(history, instruction)

        return {"step": "continue", "text": text, "memory": memory}


    # -------------------------------------------------
    # CONTINUE MODE
    # -------------------------------------------------

    if step == "continue":

        instruction = f"""
User said: "{user_text}"

Stay aligned with reduced urgency.
Keep pressure low.
Do not solve the decision.
Keep conversation open.
"""

        text = gpt_reply(history, instruction)

        return {"step": "continue", "text": text, "memory": memory}


    return {"step": "continue", "text": "Take your time.", "memory": memory}