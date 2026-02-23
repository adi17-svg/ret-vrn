"""
Low Mood Tool: One Safe Thing
Fully Conversational Version
- No READY gate
- History-aware (last messages passed from runner)
- Spiral-aware tone (internal only)
- Nervous system anchoring
- No abrupt exit
- Continue flow
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm grounding guide.

Rules:
- Warm, steady tone
- No advice
- No analysis
- No problem solving
- Short responses (2–4 lines)
- Focus only on safety and nervous system settling
- Always continue gently unless user wants to stop
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
    # STEP 0 — REFLECT + INVITE
    # =================================================
    if step is None or step == "start":

        instruction = """
Briefly reflect that things feel heavy or intense.
Then gently ask:
Is there one thing around you that feels even slightly safe or steady right now?
Keep it simple.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "identify", "text": text}

    # =================================================
    # STEP 1 — IDENTIFY SAFE THING
    # =================================================
    if step == "identify":

        instruction = f"""
User said: "{user_text}"

Acknowledge the safe thing briefly.
Invite resting attention there.
Add one simple sensory cue (texture, temperature, weight).
Keep tone calm.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "deepen", "text": text}

    # =================================================
    # STEP 2 — DEEPEN ANCHOR
    # =================================================
    if step == "deepen":

        instruction = """
Gently reinforce that even one steady thing matters.
Let them know their nervous system can settle a little here.
Then ask softly:
Would you like to stay with this for a moment, shift slightly, or stop?
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
Encourage staying with the safe sensation.
Add one slow breath.
Keep it grounding.
"""

            text = gpt_reply(history, instruction, spiral_stage)

            return {"step": "continue_choice", "text": text}

        if decision == "SHIFT":

            instruction = """
Invite noticing one additional safe detail in the environment.
Keep it simple and steady.
"""

            text = gpt_reply(history, instruction, spiral_stage)

            return {"step": "continue_choice", "text": text}

        if decision == "STOP":

            instruction = """
Acknowledge gently.
Reinforce that even doing this much matters.
Close calmly.
"""

            text = gpt_reply(history, instruction, spiral_stage)

            return {"step": "exit", "text": text}

        # UNCLEAR → stay gentle

        instruction = """
Reassure them they can stay with this steady point.
No rush.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {"step": "continue_choice", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {
        "step": "continue_choice",
        "text": "You can rest in this steady moment."
    }