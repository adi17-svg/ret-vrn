"""
Low Mood Tool: Getting Going With Action
Intent-Driven Conversational Version (RETVRN)

Features:
- Meaning extraction
- Blocker type mapping
- Spiral-aware micro action
- Dynamic flow progression
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
- Move gently toward small action
- No lecturing
- No long analysis
- Always shrink the task
- Stay aligned with: "Start small. No pressure."
- Keep conversation open after suggesting action
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
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()

# =====================================================
# MEANING EXTRACTION
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
# DYNAMIC MICRO STEP
# =====================================================

def generate_micro_step(task, blocker, spiral):

    base_prompt = f"""
Task: "{task}"
Blocker: {blocker}
Spiral tone: {spiral}

Generate one extremely small first step.
Make it tiny.
No explanation.
One action only.
"""

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": base_prompt}],
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

    if not user_text:
        return {
            "step": "continue",
            "text": "What feels hard to start right now?",
            "memory": memory
        }

    # ----------------------------------
    # MEANING EXTRACTION
    # ----------------------------------

    blocker_type = extract_blocker_type(user_text)
    spiral_stage = detect_spiral_stage(user_text)

    memory["blocker"] = blocker_type
    memory["spiral"] = spiral_stage
    memory["task"] = user_text

    # ----------------------------------
    # DIRECT ACTION MODE (No Redundant Question)
    # ----------------------------------

    micro_step = generate_micro_step(
        task=user_text,
        blocker=blocker_type,
        spiral=spiral_stage
    )

    response_text = gpt_reply(
        history,
        f"""
It sounds like the hard part is {blocker_type.lower()}.

Let’s shrink it.

Try this:
{micro_step}

No pressure.
Tell me when it’s done.
"""
    )

    return {
        "step": "continue",
        "text": response_text,
        "memory": memory
    }