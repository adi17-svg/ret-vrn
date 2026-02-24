"""
Low Mood Tool: Gentle Distraction
RETVRN Adaptive Version (v5 – Context + Fatigue Aware)

Upgrades:
- Context-based state detection
- Repeated no-shift protection
- Distress override
- Energy drift detection
- Avoid repeated activity
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You suggest small, safe, neutral activities.

Rules:
- 2–4 lines max
- Natural tone
- No motivational language
- No repeated phrasing
- Match activity to energy level
- If tired → restorative only
- Keep it practical
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
    recent = " ".join([m.get("text", "") for m in history[-3:]])
    return f"{recent} {user_text}".strip()


# =====================================================
# STATE DETECTION (Context Aware)
# =====================================================

def detect_state(context):

    prompt = f"""
Analyze this conversation:

"{context}"

Classify into ONE:

SHIFT – improvement or relief
NO_SHIFT – little change
DISTRESS – spike in heaviness/anxiety
LOW_ENERGY – tired/foggy
ACTION – user completed activity
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
# ACTIVITY GENERATOR (Avoid Repeat)
# =====================================================

def generate_activity(context, previous_activity=None):

    prompt = f"""
Based on this context:

"{context}"

Avoid repeating this:
"{previous_activity}"

If LOW_ENERGY → restorative only.
If OVERWHELM → tiny organizing step.
If DISTRESS → calming grounding.
Otherwise → small neutral reset.

One instruction only.
Very small.
No explanation.
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

        text = gpt_reply(
            history,
            "Would a very small reset help right now?"
        )

        memory["no_shift_count"] = 0

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # PROCESS
    # -------------------------------------------------

    if step == "process":

        context = build_context(history, user_text)
        state = detect_state(context)

        # ---------- DISTRESS OVERRIDE ----------

        if state == "DISTRESS":

            text = gpt_reply(
                history,
                """
Pause.

Place one hand on your chest.
Take one slow breath.
"""
            )

            return {"step": "process", "text": text, "memory": memory}

        # ---------- SHIFT OR ACTION ----------

        if state in ["SHIFT", "ACTION"]:

            activity = generate_activity(
                context,
                memory.get("last_activity")
            )

            memory["last_activity"] = activity
            memory["no_shift_count"] = 0

            text = gpt_reply(
                history,
                f"""
Okay. There’s a small shift.

Next gentle step:
{activity}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ---------- LOW ENERGY ----------

        if state == "LOW_ENERGY":

            activity = generate_activity(
                context,
                memory.get("last_activity")
            )

            memory["last_activity"] = activity

            text = gpt_reply(
                history,
                f"""
Let’s keep it restorative.

Try this:
{activity}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ---------- NO SHIFT ----------

        memory["no_shift_count"] = memory.get("no_shift_count", 0) + 1

        # If repeated no shift → change direction
        if memory["no_shift_count"] >= 2:

            activity = generate_activity(
                context,
                memory.get("last_activity")
            )

            memory["last_activity"] = activity
            memory["no_shift_count"] = 0

            text = gpt_reply(
                history,
                f"""
Let’s try a slightly different reset.

{activity}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # Normal suggestion

        activity = generate_activity(
            context,
            memory.get("last_activity")
        )

        memory["last_activity"] = activity

        text = gpt_reply(
            history,
            f"""
Here’s something small:
{activity}

No pressure.
"""
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE
    # -------------------------------------------------

    if step == "continue":

        context = build_context(history, user_text)
        state = detect_state(context)

        if state == "SHIFT":

            text = gpt_reply(
                history,
                "Alright. Stay with that. We can build slowly from here."
            )
            return {"step": "continue", "text": text, "memory": memory}

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Keep suggestions small and energy-appropriate.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "We can keep it very small. What feels manageable right now?",
        "memory": memory
    }