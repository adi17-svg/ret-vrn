"""
Low Mood Tool: Body Check-In
Intent-Driven + Spiral Aware + No Abrupt Exit
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
- Short responses (2–4 lines)
- No therapy explanations
- No advice
- Guide body awareness gently
- Adjust tone based on emotional intensity
- Keep conversation softly open
"""

# =====================================================
# GPT HELPER (History Aware)
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
# MEANING EXTRACTION (BODY STATE)
# =====================================================

def detect_body_state(text):

    prompt = f"""
Classify the dominant body state in this message.

Options:
TENSION – tight, clenched, pressure
NUMB – blank, disconnected
RESTLESS – agitated, jittery
FATIGUE – heavy, drained
ANXIOUS – racing heart, shallow breath
UNCLEAR – none obvious

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
Red – frustration/intensity
Orange – performance pressure
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
# DYNAMIC MICRO REGULATION STEP
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
            "Pause for a moment. What do you notice in your body right now?"
        )

        return {"step": "continue", "text": text, "memory": memory}

    # ----------------------------------
    # MEANING EXTRACTION
    # ----------------------------------

    body_state = detect_body_state(user_text)
    spiral_stage = detect_spiral(user_text)

    memory["body_state"] = body_state
    memory["spiral"] = spiral_stage

    # ----------------------------------
    # DIRECT REGULATION MODE
    # ----------------------------------

    micro_step = generate_body_step(body_state, spiral_stage)

    response_text = gpt_reply(
        history,
        f"""
It sounds like your body is holding {body_state.lower()}.

Let’s keep it gentle.

Try this:
{micro_step}

No forcing.
Tell me what shifts, even slightly.
"""
    )

    return {
        "step": "continue",
        "text": response_text,
        "memory": memory
    }