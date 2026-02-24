"""
Low Mood Tool: Body Check-In
RETVRN Clean Version (v4 – Clear + Concrete)

Purpose:
Shift attention from overthinking → body regulation → tiny forward movement.

Features:
✔ Semantic meaning extraction
✔ Blocker detection
✔ Spiral detection
✔ Concrete body step (no abstract language)
✔ Closed feedback loop (heavier/lighter/same)
✔ Direct progression toward small action
✔ Rotating subtle validation (no repetition)
✔ History-aware
✔ No abrupt exit
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
- No abstract language
- No sensory poetry
- No therapy explanations
- Give one clear physical instruction at a time
- Use simple feedback options like:
  heavier / lighter / same
- If lighter → gently move toward tiny action
- If same → give another small body instruction
- No repeated phrases
- Keep tone grounded and practical
"""

# =====================================================
# ROTATING VALIDATION (SUBTLE)
# =====================================================

PROGRESS_LINES = [
    "Okay. There’s a small shift.",
    "Alright. That changed a bit.",
    "Hmm. Noticed.",
    "Got it.",
    "That counts."
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
# BLOCKER DETECTION
# =====================================================

def detect_blocker(text):

    prompt = f"""
Return one word:

INITIATION
OVERWHELM
DISTRACTION
LOW_ENERGY
FEAR
UNCLEAR

Message: "{text}"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# SPIRAL DETECTION
# =====================================================

def detect_spiral(text):

    prompt = f"""
Return one word:

BLUE
RED
ORANGE
GREEN
NEUTRAL

Message: "{text}"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# BODY STEP GENERATOR (CLEAR + CONCRETE)
# =====================================================

def generate_body_step():

    prompt = """
Give one extremely clear physical instruction.
No abstract wording.
Examples style:
- Place one hand on your chest.
- Press your feet into the floor.
- Take one slow breath.
- Roll your shoulders once.

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

def generate_action_step(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral: {spiral}

Generate one very small action.
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
# SHIFT CLASSIFIER
# =====================================================

def classify_shift(text):

    prompt = f"""
Classify response as:

LIGHTER
HEAVIER
SAME
UNCLEAR

Message: "{text}"
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
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

        text = gpt_reply(
            history,
            f"""
Try this:
{body_step}

After that, does your body feel
heavier, lighter, or the same?
"""
        )

        return {"step": "check_shift", "text": text, "memory": memory}

    # ----------------------------------
    # CHECK SHIFT
    # ----------------------------------

    if step == "check_shift":

        result = classify_shift(user_text)

        if result == "LIGHTER":

            blocker = detect_blocker(user_text)
            spiral = detect_spiral(user_text)

            index = memory.get("validation_index", 0)
            line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
            memory["validation_index"] = index + 1

            action_step = generate_action_step(blocker, spiral)

            text = gpt_reply(
                history,
                f"""
{line}

Now try this small step:
{action_step}
"""
            )

            return {"step": "continue", "text": text, "memory": memory}

        if result == "SAME" or result == "HEAVIER":

            body_step = generate_body_step()

            text = gpt_reply(
                history,
                f"""
Okay.

Try this instead:
{body_step}

Then tell me:
lighter, heavier, or same?
"""
            )

            return {"step": "check_shift", "text": text, "memory": memory}

        # UNCLEAR

        text = gpt_reply(
            history,
            "No problem. Just tell me — lighter, heavier, or same?"
        )

        return {"step": "check_shift", "text": text, "memory": memory}

    # ----------------------------------
    # CONTINUE
    # ----------------------------------

    if step == "continue":

        text = gpt_reply(
            history,
            f'User said: "{user_text}". Keep things steady and practical.'
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # FALLBACK
    # ----------------------------------

    return {
        "step": "continue",
        "text": "Stay with one slow breath. What feels manageable right now?",
        "memory": memory
    }