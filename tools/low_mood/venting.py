"""
Low Mood Tool: Venting
Fully Conversational + Spiral Integrated Version

Purpose:
- Allow emotional release
- Reflect emotion (not analyze story)
- Contain intensity safely
- Continue gently (no abrupt exit)
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You hold space for emotional release.

Rules:
- No advice
- No fixing
- No analysis
- Reflect emotions, not story details
- Warm, steady tone
- Keep responses short (2–4 lines)
- Help regulate intensity gently
- Continue unless user wants to stop
"""

# =====================================================
# SAFE CLASSIFIER
# =====================================================

def safe_classify(system_instruction, user_text, valid_options, default):

    if not user_text or len(user_text.strip()) < 2:
        return default

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip().upper()

        if result in valid_options:
            return result

        return default

    except:
        return default


def classify_spiral(user_text):
    return safe_classify(
        "Classify into one word only: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW.",
        user_text,
        ["BEIGE", "PURPLE", "RED", "BLUE", "ORANGE", "GREEN", "YELLOW"],
        "GREEN"
    )


def classify_continue(user_text):
    return safe_classify(
        "Classify into one word: CONTINUE, SHIFT, STOP, or UNCLEAR.",
        user_text,
        ["CONTINUE", "SHIFT", "STOP", "UNCLEAR"],
        "UNCLEAR"
    )

# =====================================================
# GPT REPLY (History + Spiral Aware)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User emotional tone appears closer to {spiral_stage}.
Adjust reflection tone subtly.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()

# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    user_text = (user_text or "").strip()
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # =================================================
    # STEP 0 — INVITE SAFE VENTING
    # =================================================
    if step is None or step == "start":

        instruction = """
Let them know this is a safe space.
Invite them to let it out freely.
Reassure: no fixing, no judging.
Keep it warm.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "venting", "text": text}

    # =================================================
    # STEP 1 — REFLECT + VALIDATE
    # =================================================
    if step == "venting":

        instruction = f"""
User said: "{user_text}"

Reflect the emotional intensity.
Do NOT analyze the situation.
Validate how heavy it sounds.
Add one gentle containment cue (like slowing breath).
Then ask softly:
Would you like to keep letting it out, shift slightly, or pause?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "continue_choice", "text": text}

    # =================================================
    # STEP 2 — CONTINUE FLOW
    # =================================================
    if step == "continue_choice":

        decision = classify_continue(user_text)

        if decision == "CONTINUE":
            instruction = """
Encourage them to continue sharing.
Reinforce safety.
Keep tone steady.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "venting", "text": text}

        if decision == "SHIFT":
            instruction = """
Acknowledge what they've shared.
Suggest a gentle grounding shift (like one breath or noticing body).
Keep it soft.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "continue_choice", "text": text}

        if decision == "STOP":
            instruction = """
Thank them for sharing.
Reinforce that expressing this matters.
Close calmly.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "exit", "text": text}

        # UNCLEAR → stay supportive

        instruction = """
Reassure they can take their time.
They don't need to solve anything here.
"""
        text = gpt_reply(history, instruction, spiral_stage)
        return {"step": "continue_choice", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "continue_choice",
        "text": "You can let it out here. I’m listening."
    }