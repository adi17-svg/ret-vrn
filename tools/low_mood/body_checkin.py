"""
Low Mood Tool: Body Check-In
RETVRN Adaptive Version (v5 – Context Aware)

Upgrades:
- Context-based shift detection
- Repeat SAME detection protection
- Last body step memory
- Distress branching
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a calm nervous-system regulation guide.

Rules:
- Keep responses short (2–4 lines max)
- One clear physical instruction at a time
- No abstract therapy explanations
- Keep tone practical and grounded
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
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# CONTEXT BUILDER
# =====================================================

def build_context(history, user_text):
    recent = " ".join([msg.get("text", "") for msg in history[-3:]])
    return f"{recent} {user_text}".strip()


# =====================================================
# SHIFT CLASSIFIER (Context Aware)
# =====================================================

def classify_shift(context):

    prompt = f"""
Based on this conversation, classify the shift:

Context:
"{context}"

Return one word:

LIGHTER
HEAVIER
SAME
DISTRESS
UNCLEAR
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# BODY STEP GENERATOR (Avoid repeat)
# =====================================================

def generate_body_step(previous_step=None):

    prompt = f"""
Give one clear physical instruction.
Avoid repeating this:
"{previous_step}"

One instruction only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return resp.choices[0].message.content.strip()


# =====================================================
# MICRO ACTION GENERATOR
# =====================================================

def generate_action_step(context):

    prompt = f"""
Based on this context:

"{context}"

Generate one very small practical action.
5 minutes max.
Concrete.
One instruction only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
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

    # ----------------------------------
    # START
    # ----------------------------------

    if step == "start":

        body_step = generate_body_step()

        memory["last_body_step"] = body_step
        memory["same_count"] = 0

        text = gpt_reply(
            history,
            f"""
Try this:
{body_step}

Then tell me:
lighter, heavier, or same?
"""
        )

        return {"step": "check_shift", "text": text, "memory": memory}

    # ----------------------------------
    # CHECK SHIFT
    # ----------------------------------

    if step == "check_shift":

        context = build_context(history, user_text)
        result = classify_shift(context)

        # ---------- LIGHTER ----------

        if result == "LIGHTER":

            action_step = generate_action_step(context)

            text = gpt_reply(
                history,
                f"""
Okay. Small shift noticed.

Now try this:
{action_step}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ---------- DISTRESS ----------

        if result == "DISTRESS":

            text = gpt_reply(
                history,
                """
Pause.

Place one hand on your chest.
Take one slow breath.

Tell me when done.
"""
            )

            return {"step": "check_shift", "text": text, "memory": memory}

        # ---------- SAME / HEAVIER ----------

        if result in ["SAME", "HEAVIER"]:

            memory["same_count"] = memory.get("same_count", 0) + 1

            # If repeated SAME → break loop differently
            if memory["same_count"] >= 2:

                action_step = generate_action_step(context)

                text = gpt_reply(
                    history,
                    f"""
Okay. Let's shift approach.

Try this small action instead:
{action_step}
"""
                )

                return {"step": "continue", "text": text, "memory": memory}

            # Normal repeat body step
            body_step = generate_body_step(memory.get("last_body_step"))

            memory["last_body_step"] = body_step

            text = gpt_reply(
                history,
                f"""
Try this instead:
{body_step}

Then tell me:
lighter, heavier, or same?
"""
            )

            return {"step": "check_shift", "text": text, "memory": memory}

        # ---------- UNCLEAR ----------

        text = gpt_reply(
            history,
            "Just say lighter, heavier, or same."
        )

        return {"step": "check_shift", "text": text, "memory": memory}

    # ----------------------------------
    # CONTINUE
    # ----------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Keep things steady.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # FALLBACK
    # ----------------------------------

    return {
        "step": "continue",
        "text": "Take one slow breath. What feels manageable now?",
        "memory": memory
    }