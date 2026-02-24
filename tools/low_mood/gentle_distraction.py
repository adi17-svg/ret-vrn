"""
Low Mood Tool: Gentle Distraction
RETVRN Adaptive Version (v3)

Features:
✔ Meaning extraction (semantic)
✔ Blocker detection
✔ Spiral detection
✔ Spiral-aware micro-step
✔ Direct progression toward action
✔ Progress detection
✔ Rotating validation (no repetition)
✔ History-aware
✔ Natural conversational flow
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
- Short responses (2–4 lines max)
- Natural and grounded tone
- No deep analysis
- No repetitive praise
- No repeated phrasing
- Subtle validation only
- Gradually move toward gentle action
- Never abruptly end conversation
"""

# =====================================================
# ROTATING VALIDATION POOL
# =====================================================

PROGRESS_LINES = [
    "Alright. That shifted something.",
    "Okay. There’s a slight change.",
    "Hmm. Notice that.",
    "That counts.",
    "Got it. Stay with that.",
    "There’s a bit of movement."
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

    prompt = f"""
Summarize in 3-5 words what the person is experiencing.

Message: "{text}"

Return only the short phrase.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

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
# PROGRESS
# =====================================================

def detect_progress(text):
    return safe_classify(
        "Did the user describe improvement, shift, or action? YES or NO.",
        text,
        ["YES","NO"],
        "NO"
    )

# =====================================================
# MICRO ACTIVITY GENERATOR
# =====================================================

def generate_activity(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral tone: {spiral}

Generate one very small, safe distraction activity.
Low effort.
2-5 minutes.
One instruction only.
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
            "Would something light and simple help create a little space right now?"
        )

        return {"step": "process", "text": text, "memory": memory}

    # -------------------------------------------------
    # PROCESS USER INPUT
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
        # IF SHIFT ALREADY HAPPENED
        # ----------------------------------

        if progress == "YES":

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            micro_activity = generate_activity(blocker, spiral)

            text = gpt_reply(
                history,
                f"""
Start with this line exactly:
"{line}"

Then gently move toward this:
{micro_activity}

Keep tone steady.
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        # ----------------------------------
        # OTHERWISE OFFER SMALL ACTIVITY
        # ----------------------------------

        micro_activity = generate_activity(blocker, spiral)

        text = gpt_reply(
            history,
            f"""
Reflect briefly on: {meaning}.

Offer this small option:
{micro_activity}

No pressure.
"""
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # CONTINUE MODE
    # -------------------------------------------------

    if step == "continue":

        progress = detect_progress(user_text)

        if progress == "YES":

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            text = gpt_reply(
                history,
                f'Start with "{line}" then gently build small forward momentum.'
            )

            return {"step": "continue", "text": text, "memory": memory}

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Stay grounded and gently guide toward doable small action.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "step": "continue",
        "text": "I’m here. We can keep it light. What feels manageable right now?",
        "memory": memory
    }