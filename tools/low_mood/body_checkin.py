"""
Low Mood Tool: Body Check-In
RETVRN Adaptive Version (v3)

Features:
✔ Meaning extraction (semantic)
✔ Blocker detection
✔ Body-state detection
✔ Spiral-aware regulation
✔ Progress detection
✔ Adaptive progression toward gentle action
✔ Rotating validation (no repetition)
✔ History-aware
✔ No abrupt exit
✔ Natural tone
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
- Short responses (2–4 lines max)
- No therapy explanations
- No lecturing
- No repeated phrases
- Validation should be subtle and varied
- Guide body awareness gently
- If user shifts or progresses → gently expand
- Never abruptly end conversation
- Keep tone grounded and natural
"""

# =====================================================
# ROTATING VALIDATION POOL
# =====================================================

PROGRESS_LINES = [
    "Okay. Something shifted.",
    "Hmm. That’s a change.",
    "Alright. Stay with that.",
    "There’s movement there.",
    "Got it. Notice that.",
    "That’s something."
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
        temperature=0.5,
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# SEMANTIC MEANING EXTRACTION
# =====================================================

def extract_meaning(text):

    prompt = f"""
Summarize in one short phrase what the person is experiencing.

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
# BLOCKER DETECTION
# =====================================================

def detect_blocker(text):

    prompt = f"""
Classify the main blocker:

INITIATION
OVERWHELM
DISTRACTION
LOW_ENERGY
FEAR
UNCLEAR

Message: "{text}"

Return one word.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# BODY STATE DETECTION
# =====================================================

def detect_body_state(text):

    prompt = f"""
Classify dominant body state:

TENSION
NUMB
RESTLESS
FATIGUE
ANXIOUS
UNCLEAR

Message: "{text}"

Return one word.
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
Classify emotional tone:

Blue – guilt/duty
Red – frustration
Orange – performance pressure
Green – overwhelm
Neutral – unclear

Message: "{text}"

Return one word.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# PROGRESS DETECTION
# =====================================================

def detect_progress(text):

    prompt = f"""
Did the user describe a shift, relief, action, or completion?

Message: "{text}"

Answer YES or NO only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# BODY MICRO STEP
# =====================================================

def generate_body_step(body_state, spiral):

    prompt = f"""
Body state: {body_state}
Spiral tone: {spiral}

Generate one tiny nervous-system regulation step.
Very small.
No explanation.
One instruction only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# ACTION SHIFT STEP
# =====================================================

def generate_action_step(blocker, spiral):

    prompt = f"""
Blocker: {blocker}
Spiral tone: {spiral}

Generate one very small action step.
5 minutes max.
No explanation.
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

    # ----------------------------------
    # FIRST ENTRY
    # ----------------------------------

    if not user_text:
        text = gpt_reply(
            history,
            "Pause for a moment. What are you noticing in your body right now?"
        )
        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # PROGRESS BRANCH
    # ----------------------------------

    progress = detect_progress(user_text)

    if progress == "YES" and memory.get("body_state"):

        index = memory.get("validation_index", 0)
        line = PROGRESS_LINES[index % len(PROGRESS_LINES)]
        memory["validation_index"] = index + 1

        action_step = generate_action_step(
            memory.get("blocker", "UNCLEAR"),
            memory.get("spiral", "Neutral")
        )

        response = gpt_reply(
            history,
            f"""
Start with this line exactly:
"{line}"

Then gently move toward action:
{action_step}

Keep it calm.
"""
        )

        return {"step": "continue", "text": response, "memory": memory}

    # ----------------------------------
    # NEW DETECTION
    # ----------------------------------

    meaning = extract_meaning(user_text)
    blocker = detect_blocker(user_text)
    body_state = detect_body_state(user_text)
    spiral = detect_spiral(user_text)

    memory["meaning"] = meaning
    memory["blocker"] = blocker
    memory["body_state"] = body_state
    memory["spiral"] = spiral

    body_step = generate_body_step(body_state, spiral)

    response = gpt_reply(
        history,
        f"""
Reflect briefly on: {meaning}.

Guide attention to the body gently.

Try this:
{body_step}

No forcing.
Tell me what you notice.
"""
    )

    return {"step": "continue", "text": response, "memory": memory}