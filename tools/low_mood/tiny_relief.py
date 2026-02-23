"""
Low Mood Tool: Tiny Relief (1% Okay)
Fully Conversational + Spiral Integrated Version

Purpose:
- Interrupt negative bias
- Amplify micro relief (glimmers)
- Support nervous system regulation
- Continue gently (no abrupt exit)
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You gently help the user notice small moments of relief.

Rules:
- Warm, calm tone
- No advice
- No fixing
- No toxic positivity
- Keep responses short (2–4 lines)
- Amplify even 1% okay moments
- Continue gently unless user wants to stop
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
        "Classify into one word: STAY, SHIFT, STOP, or UNCLEAR.",
        user_text,
        ["STAY", "SHIFT", "STOP", "UNCLEAR"],
        "UNCLEAR"
    )

# =====================================================
# GPT REPLY (History + Spiral Aware)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User emotional tendency appears closer to {spiral_stage}.
Adjust tone subtly.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.4,
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
    # STEP 0 — REFLECT + INVITE 1%
    # =================================================
    if step is None or step == "start":

        instruction = """
Briefly reflect that things feel heavy.
Then gently ask:
Is there even 1% of this moment that feels neutral or slightly okay?
Keep it simple.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "identify", "text": text}

    # =================================================
    # STEP 1 — AMPLIFY GLIMMER
    # =================================================
    if step == "identify":

        instruction = f"""
User said: "{user_text}"

Acknowledge that small okay moment.
Invite noticing one sensory detail about it (texture, sound, light, warmth).
Keep tone gentle.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "stay", "text": text}

    # =================================================
    # STEP 2 — STAY WITH IT
    # =================================================
    if step == "stay":

        instruction = """
Encourage staying with that small okay feeling for 10–20 seconds.
Add one slow breath cue.
Then ask softly:
Would you like to stay here, notice another small okay thing, or stop?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "continue_choice", "text": text}

    # =================================================
    # STEP 3 — CONTINUE FLOW
    # =================================================
    if step == "continue_choice":

        decision = classify_continue(user_text)

        if decision == "STAY":
            instruction = """
Encourage resting in that small steady feeling.
Add one gentle grounding cue.
Keep it calm.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "continue_choice", "text": text}

        if decision == "SHIFT":
            instruction = """
Invite noticing one more small neutral or slightly okay detail.
Keep it very small.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "identify", "text": text}

        if decision == "STOP":
            instruction = """
Acknowledge gently.
Reinforce that even noticing 1% okay matters.
Close calmly.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "exit", "text": text}

        # UNCLEAR → stay gentle

        instruction = """
Reassure them they can rest in this small steady moment.
No rush.
"""
        text = gpt_reply(history, instruction, spiral_stage)
        return {"step": "continue_choice", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "continue_choice",
        "text": "Even a tiny okay moment is enough for now."
    }