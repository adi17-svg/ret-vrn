"""
Low Mood Tool: Thought Parking
Fully Conversational + Spiral Integrated Version

Purpose:
- Reduce rumination
- Reduce urgency
- Contain heavy thoughts
- No abrupt exit
- Continue gently
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You gently help users set aside heavy thoughts temporarily.

Rules:
- Calm tone
- No analysis
- No advice
- No solving
- Keep responses short (2–4 lines)
- Reduce urgency
- Focus on containment and nervous system settling
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
    # STEP 0 — REFLECT LOOPING PRESSURE
    # =================================================
    if step is None or step == "start":

        instruction = """
Briefly reflect that the mind seems stuck on something heavy.
Normalize that when things feel uncertain, thoughts loop.
Then gently ask:
What’s one specific thought that feels loud right now?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "name_thought", "text": text}

    # =================================================
    # STEP 1 — EXTERNALIZE THOUGHT
    # =================================================
    if step == "name_thought":

        instruction = f"""
User said: "{user_text}"

Repeat the thought neutrally.
Do not argue or correct it.
Then say gently:
This thought does not need to be solved right now.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "park", "text": text}

    # =================================================
    # STEP 2 — PARK IT SYMBOLICALLY
    # =================================================
    if step == "park":

        instruction = """
Invite them to imagine placing this thought somewhere safe
— like a shelf, box, or outside the room.
Emphasize temporary parking.
Add one slow breath cue.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "settle", "text": text}

    # =================================================
    # STEP 3 — BODY SETTLE + CONTINUE
    # =================================================
    if step == "settle":

        instruction = """
Reinforce that setting it aside reduces pressure.
Then ask softly:
Would you like to stay here for a moment,
shift to something small,
or stop for now?
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "continue_choice", "text": text}

    # =================================================
    # STEP 4 — CONTINUE FLOW
    # =================================================
    if step == "continue_choice":

        decision = classify_continue(user_text)

        if decision == "STAY":
            instruction = """
Encourage resting in the quieter space.
Add one grounding breath.
Keep it calm.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "continue_choice", "text": text}

        if decision == "SHIFT":
            instruction = """
Suggest one very small, neutral action
like noticing the room or moving the body slightly.
Keep it light.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "continue_choice", "text": text}

        if decision == "STOP":
            instruction = """
Acknowledge gently.
Reinforce that even parking the thought helps.
Close calmly.
"""
            text = gpt_reply(history, instruction, spiral_stage)
            return {"step": "exit", "text": text}

        # UNCLEAR → stay steady

        instruction = """
Let them know they can stay in this quieter space.
No rush.
"""
        text = gpt_reply(history, instruction, spiral_stage)
        return {"step": "continue_choice", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "continue_choice",
        "text": "We can let that thought rest for now."
    }