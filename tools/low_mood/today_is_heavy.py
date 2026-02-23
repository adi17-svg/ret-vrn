"""
Low Mood Tool: Today Is Heavy
Fully Conversational + Spiral Integrated Version

Purpose:
- Normalize heavy days
- Remove performance pressure
- Offer permission to slow down
- Continue gently (no abrupt exit)
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You validate heavy days gently.

Rules:
- No advice
- No pushing
- No productivity coaching
- Warm reassurance
- Keep responses short (2–4 lines)
- Reduce self-pressure
- Continue softly unless user wants to stop
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
    # STEP 0 — REFLECT + NORMALIZE
    # =================================================
    if step is None or step == "start":

        instruction = """
Briefly reflect that today feels heavy.
Normalize that some days genuinely carry more weight.
Remove pressure to perform.
Then gently ask:
If today didn’t have to be perfect, what would feel “enough”?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "minimum", "text": text}

    # =================================================
    # STEP 1 — AFFIRM MINIMUM
    # =================================================
    if step == "minimum":

        instruction = f"""
User said: "{user_text}"

Affirm that this minimum is valid.
Reinforce that slowing down is allowed.
Then ask softly:
Would you like to stay here, lower the bar even more, or stop for now?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "continue_choice", "text": text}

    # =================================================
    # STEP 2 — CONTINUE FLOW
    # =================================================
    if step == "continue_choice":

        decision = classify_continue(user_text)

        if decision == "STAY":
            instruction = """
Encourage resting in this slower pace.
Add one gentle body relaxation cue.
Keep tone calm.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "continue_choice", "text": text}

        if decision == "SHIFT":
            instruction = """
Invite reducing expectations even further.
Emphasize small effort counts.
Keep it gentle.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "minimum", "text": text}

        if decision == "STOP":
            instruction = """
Acknowledge gently.
Reinforce that honoring heavy days matters.
Close warmly.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "exit", "text": text}

        # UNCLEAR → stay gentle

        instruction = """
Reassure that there’s no rush.
Even slowing down is progress today.
"""
        text = gpt_reply(history, instruction, spiral_stage)
        return {"step": "continue_choice", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "continue_choice",
        "text": "You’re allowed to go gently today."
    }