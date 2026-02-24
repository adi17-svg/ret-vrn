"""
Low Mood Tool: Breath Word
RETVRN Adaptive Version (v3)

Features:
✔ Meaning extraction
✔ Blocker detection
✔ Spiral detection
✔ Breath → Body → Action progression
✔ Progress detection
✔ Rotating subtle validations
✔ No repeated phrasing
✔ History-aware
✔ Natural flow
✔ No abrupt exit
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
- Gentle and grounded tone
- No analysis or lecturing
- No repeated phrases
- Validation must be subtle and varied
- Gradually move from breath → awareness → small action
- Never abruptly end the conversation
- Keep things natural and human
"""

# =====================================================
# ROTATING VALIDATION POOL
# =====================================================

PROGRESS_LINES = [
    "Alright. Stay with that.",
    "Okay. There’s a slight shift.",
    "Hmm. Notice that.",
    "That’s something.",
    "Got it. Let’s keep it steady.",
    "There’s a bit of space now."
]

# =====================================================
# GPT REPLY
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

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()

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
# SEMANTIC MEANING
# =====================================================

def extract_meaning(text):
    return safe_classify(
        "Summarize core experience in 3-5 words.",
        text,
        [],
        text
    )

# =====================================================
# BLOCKER
# =====================================================

def detect_blocker(text):
    return safe_classify(
        "Return one: INITIATION, OVERWHELM, DISTRACTION, LOW_ENERGY, FEAR, UNCLEAR.",
        text,
        ["INITIATION","OVERWHELM","DISTRACTION","LOW_ENERGY","FEAR","UNCLEAR"],
        "UNCLEAR"
    )

# =====================================================
# SPIRAL
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
        "Did the user describe relief, shift, action, or completion? YES or NO.",
        text,
        ["YES","NO"],
        "NO"
    )

# =====================================================
# MICRO ACTION
# =====================================================

def generate_micro_action(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral tone: {spiral}

Generate one very small action (5 min max).
No explanation.
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

        text = gpt_reply(
            history,
            "Let’s take one slow breath together. Inhale… and exhale gently."
        )

        return {"step": "breath_2", "text": text, "memory": memory}

    # -------------------------------------------------
    # SECOND BREATH
    # -------------------------------------------------

    if step == "breath_2":

        text = gpt_reply(
            history,
            "Again. Slow inhale… long exhale."
        )

        return {"step": "notice", "text": text, "memory": memory}

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
    # PROCESS USER RESPONSE
    # -------------------------------------------------

    if step == "process":

        meaning = user_text
        blocker = detect_blocker(user_text)
        spiral = detect_spiral(user_text)
        progress = detect_progress(user_text)

        memory["meaning"] = meaning
        memory["blocker"] = blocker
        memory["spiral"] = spiral

        # ----------------------------------
        # If shift happened → move toward action
        # ----------------------------------

        if progress == "YES":

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            micro_action = generate_micro_action(blocker, spiral)

            text = gpt_reply(
                history,
                f"""
Start with this line exactly:
"{line}"

Then gently move toward this:
{micro_action}

Keep it grounded.
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ----------------------------------
        # If no shift → regulate gently
        # ----------------------------------

        text = gpt_reply(
            history,
            """
Stay with the breath for one more slow cycle.
No forcing.

Then tell me what feels most present.
"""
        )

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE
    # -------------------------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Stay grounded. If stable, gently move toward small doable action.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "I’m here. Stay with one slow breath and tell me what feels present.",
        "memory": memory
    }