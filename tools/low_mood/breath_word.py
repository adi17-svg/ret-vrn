"""
Low Mood Tool: Breath Word
RETVRN Adaptive Version (v4 – Context Aware)

Upgrades:
- Context-based progress detection
- Repeated no-shift protection
- Distress branching
- Last step memory
- Breath cycle limiter
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a calm breathing and regulation guide.

Rules:
- Short responses (2–4 lines max)
- Grounded and simple
- No therapy explanations
- No repeated phrasing
- Gradually move from breath → awareness → small action
"""


# =====================================================
# GPT HELPER
# =====================================================

def gpt_reply(history, instruction):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[-HISTORY_LIMIT:]:
        role = "assistant" if msg.get("type") == "assistant" else "user"
        content = msg.get("text", "")
        if content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": instruction})

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# CONTEXT BUILDER
# =====================================================

def build_context(history, user_text):
    recent = " ".join([m.get("text", "") for m in history[-3:]])
    return f"{recent} {user_text}".strip()


# =====================================================
# STATE CLASSIFIER (Context Aware)
# =====================================================

def detect_state(context):

    prompt = f"""
Analyze this conversation context:

"{context}"

Classify into ONE:

SHIFT – user feels relief or change
NO_SHIFT – little change
DISTRESS – spike in anxiety/heaviness
ACTION – user took small action
UNCLEAR

Return one word only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MICRO ACTION GENERATOR (Context Based)
# =====================================================

def generate_micro_action(context):

    prompt = f"""
Based on this context:

"{context}"

Generate one very small, practical action (5 minutes max).
Concrete.
One instruction only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None, memory=None):

    history = history or []
    memory = memory or {}
    user_text = (user_text or "").strip()

    if not step:
        step = "start"

    # -------------------------------------------------
    # START
    # -------------------------------------------------

    if step == "start":

        memory["breath_count"] = 1

        text = gpt_reply(
            history,
            "Take one slow breath. Inhale… and exhale gently."
        )

        return {"step": "breath", "text": text, "memory": memory}

    # -------------------------------------------------
    # BREATH LOOP
    # -------------------------------------------------

    if step == "breath":

        memory["breath_count"] = memory.get("breath_count", 1) + 1

        # limit breath loop
        if memory["breath_count"] <= 2:

            text = gpt_reply(
                history,
                "Again. Slow inhale… long exhale."
            )

            return {"step": "notice", "text": text, "memory": memory}

        # after 2 cycles move forward
        return {"step": "notice", "text": "", "memory": memory}

    # -------------------------------------------------
    # NOTICE
    # -------------------------------------------------

    if step == "notice":

        text = gpt_reply(
            history,
            "Let your breath settle. What feels slightly different, if anything?"
        )

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # PROCESS RESPONSE
    # -------------------------------------------------

    if step == "process":

        context = build_context(history, user_text)
        state = detect_state(context)

        # ---------------- SHIFT ----------------

        if state == "SHIFT":

            action = generate_micro_action(context)

            text = gpt_reply(
                history,
                f"""
Okay. There’s a bit of space.

Now try this:
{action}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ---------------- ACTION ----------------

        if state == "ACTION":

            action = generate_micro_action(context)

            text = gpt_reply(
                history,
                f"""
Alright. Stay steady.

Next small step:
{action}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ---------------- DISTRESS ----------------

        if state == "DISTRESS":

            text = gpt_reply(
                history,
                """
Pause.

Place one hand on your chest.
Take one slow breath.

Tell me when done.
"""
            )

            return {"step": "process", "text": text, "memory": memory}

        # ---------------- NO SHIFT ----------------

        memory["no_shift_count"] = memory.get("no_shift_count", 0) + 1

        if memory["no_shift_count"] >= 2:

            action = generate_micro_action(context)

            text = gpt_reply(
                history,
                f"""
Okay. Let’s change direction slightly.

Try this small action:
{action}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # normal no shift

        text = gpt_reply(
            history,
            """
Stay with one more slow breath.
No forcing.

Then tell me what feels present.
"""
        )

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Stay grounded and move gently toward doable action.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "Stay with one steady breath. What feels manageable now?",
        "memory": memory
    }