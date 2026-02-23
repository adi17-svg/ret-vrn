"""
Low Mood Tool: Getting Going With Action
Intent-Driven Conversational Version (RETVRN - Adaptive Flow)

Features:
- Meaning extraction
- Blocker type mapping
- Spiral-aware step sizing
- Progress detection
- Adaptive expansion after movement
- No template repetition
"""

from openai import OpenAI

client = OpenAI()
HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Be natural, not robotic
- If user hasn't started → shrink task
- If user made progress → gently expand step
- No lecturing
- No long analysis
- Keep tone warm and steady
- Stay aligned with: "Start small. No pressure."
- Keep conversation open
"""

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
# BLOCKER DETECTION
# =====================================================

def extract_blocker_type(text):

    prompt = f"""
Analyze this message and classify the main blocker:

Options:
INITIATION – trouble starting
OVERWHELM – task feels too big
DISTRACTION – attention drifting
LOW_ENERGY – tired or drained
FEAR – avoidance due to anxiety
UNCLEAR – none of the above

Message: "{text}"

Return one word only.
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

def detect_spiral_stage(text):

    prompt = f"""
Classify emotional tone into one:

Blue – guilt/responsibility
Red – resistance/frustration
Orange – productivity pressure
Green – emotional overwhelm
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
# PROGRESS DETECTION (NEW)
# =====================================================

def detect_progress(text):

    prompt = f"""
Does this message indicate the user completed a suggested action?

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
# STEP GENERATOR (ADAPTIVE)
# =====================================================

def generate_step(task, blocker, spiral, expand=False):

    if not expand:
        size_instruction = "Generate one extremely small first step."
    else:
        size_instruction = "Generate one slightly bigger but still manageable next step (5–10 min max)."

    prompt = f"""
Task: "{task}"
Blocker: {blocker}
Spiral tone: {spiral}

{size_instruction}
No explanation.
One action only.
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

    if not user_text:
        return {
            "step": "continue",
            "text": "What feels hard to start right now?",
            "memory": memory
        }

    # ----------------------------------
    # Detect Progress First
    # ----------------------------------

    progress = detect_progress(user_text)

    # ----------------------------------
    # If user made progress → expand gently
    # ----------------------------------

    if progress == "YES" and memory.get("task"):

        next_step = generate_step(
            task=memory.get("task"),
            blocker=memory.get("blocker", "UNCLEAR"),
            spiral=memory.get("spiral", "Neutral"),
            expand=True
        )

        response_text = gpt_reply(
            history,
            f"""
Acknowledge progress warmly.

Then suggest this next step:
{next_step}

Keep it gentle.
"""
        )

        return {
            "step": "continue",
            "text": response_text,
            "memory": memory
        }

    # ----------------------------------
    # Otherwise → Fresh Detection
    # ----------------------------------

    blocker_type = extract_blocker_type(user_text)
    spiral_stage = detect_spiral_stage(user_text)

    memory["blocker"] = blocker_type
    memory["spiral"] = spiral_stage
    memory["task"] = user_text

    micro_step = generate_step(
        task=user_text,
        blocker=blocker_type,
        spiral=spiral_stage,
        expand=False
    )

    response_text = gpt_reply(
        history,
        f"""
It sounds like the hard part is {blocker_type.lower()}.

Let’s make it easier.

Try this:
{micro_step}

No pressure.
"""
    )

    return {
        "step": "continue",
        "text": response_text,
        "memory": memory
    }