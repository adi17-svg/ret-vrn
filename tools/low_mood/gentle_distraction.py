"""
Low Mood Tool: Gentle Distraction
RETVRN Adaptive Version (v4 – Fatigue Aware)

Purpose:
Offer light, safe distraction aligned with energy state.
LOW_ENERGY ≠ movement.
Move gently toward doable micro action.

Features:
✔ Meaning extraction
✔ Blocker detection
✔ Spiral detection
✔ Fatigue-aware activity selection
✔ Rotating subtle validation
✔ Direct progression toward action
✔ History-aware
✔ No repeated phrasing
✔ No abrupt exit
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
- No repetitive praise
- No repeated phrasing
- Match activity to energy level
- If tired → restorative, not active
- Keep it practical
- Never abruptly end
"""

# =====================================================
# ROTATING VALIDATION
# =====================================================

PROGRESS_LINES = [
    "Okay. That shifted a little.",
    "Alright. Noted.",
    "Hmm. That’s something.",
    "Got it.",
    "There’s a small change."
]

# =====================================================
# GPT HELPER
# =====================================================

def gpt_reply(history, instruction):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
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
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction, user_text, valid, default):

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
        return result if result in valid else default

    except:
        return default

# =====================================================
# MEANING EXTRACTION
# =====================================================

def extract_meaning(text):

    prompt = f"""
Summarize what the person is feeling in 3-5 words.

Message: "{text}"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# BLOCKER DETECTION
# =====================================================

def detect_blocker(text):
    return safe_classify(
        "Return one: INITIATION, OVERWHELM, DISTRACTION, LOW_ENERGY, FEAR, UNCLEAR.",
        text,
        ["INITIATION","OVERWHELM","DISTRACTION","LOW_ENERGY","FEAR","UNCLEAR"],
        "UNCLEAR"
    )

# =====================================================
# SPIRAL DETECTION
# =====================================================

def detect_spiral(text):
    return safe_classify(
        "Return one: BLUE, RED, ORANGE, GREEN, NEUTRAL.",
        text,
        ["BLUE","RED","ORANGE","GREEN","NEUTRAL"],
        "NEUTRAL"
    )

# =====================================================
# PROGRESS DETECTION
# =====================================================

def detect_progress(text):
    return safe_classify(
        "Did the user describe improvement or shift? YES or NO.",
        text,
        ["YES","NO"],
        "NO"
    )

# =====================================================
# ACTIVITY GENERATOR (FATIGUE-AWARE)
# =====================================================

def generate_activity(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral tone: {spiral}

If blocker is LOW_ENERGY:
Suggest something restorative (sit back, drink water, close eyes briefly, loosen shoulders).
No walking or active movement.

If OVERWHELM:
Suggest one small organizing or grounding task.

If DISTRACTION:
Suggest short 2-minute focus reset.

If INITIATION:
Suggest tiny starter action (2 minutes).

If FEAR:
Suggest calming grounding (slow breathing, hand on chest).

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
            "Would a small, low-effort reset help right now?"
        )

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # PROCESS INPUT
    # -------------------------------------------------

    if step == "process":

        meaning = extract_meaning(user_text)
        blocker = detect_blocker(user_text)
        spiral = detect_spiral(user_text)
        progress = detect_progress(user_text)

        memory["meaning"] = meaning
        memory["blocker"] = blocker
        memory["spiral"] = spiral

        # ----------------------------------
        # If already shifted → build forward
        # ----------------------------------

        if progress == "YES":

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            micro = generate_activity(blocker, spiral)

            text = gpt_reply(
                history,
                f"""
{line}

Try this small next step:
{micro}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ----------------------------------
        # Otherwise suggest aligned activity
        # ----------------------------------

        micro = generate_activity(blocker, spiral)

        text = gpt_reply(
            history,
            f"""
You mentioned {meaning}.

Here’s something small:
{micro}

No pressure.
"""
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE
    # -------------------------------------------------

    if step == "continue":

        progress = detect_progress(user_text)

        if progress == "YES":

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            text = gpt_reply(
                history,
                f"{line} We can build gently from here."
            )

            return {"step": "continue", "text": text, "memory": memory}

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Stay practical and keep suggestions energy-appropriate.'
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