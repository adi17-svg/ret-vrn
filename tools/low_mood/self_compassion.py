"""
Low Mood Tool: Self Compassion
Structured + Activation Gated + History Aware
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, warm self-compassion guide.

Rules:
- Warm and natural tone
- No advice
- No fixing
- No problem solving
- Keep responses short (2–4 lines)
- Encourage gentle self-talk
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


def classify_yes_no(user_text):
    return safe_classify(
        "Classify into one word: YES, NO, or UNCLEAR.",
        user_text,
        ["YES", "NO", "UNCLEAR"],
        "UNCLEAR"
    )


# =====================================================
# GPT REPLY (History Aware)
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust tone subtly.
Never mention stages.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Include full previous chat history
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
    user_text = user_text or ""

    # -------------------------------------------------
    # STEP 0 — ACTIVATION
    # -------------------------------------------------

    if step is None or step == "await_activation":

        if user_text.strip().upper() != "READY":
            return {
                "step": "await_activation",
                "text": "This is a short self-compassion moment.\nType READY when you're ready to begin."
            }

        return {
            "step": "await_emotion",
            "text": "What feels heavy right now?"
        }

    # -------------------------------------------------
    # STEP 1 — AWAIT EMOTION
    # -------------------------------------------------

    if step == "await_emotion":

        spiral_stage = classify_spiral(user_text)

        instruction = f"""
User said: "{user_text}"

Reflect their emotional experience warmly.
Acknowledge that this feels hard.
Keep it natural.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {
            "step": "invite_self_talk",
            "text": text
        }

    # -------------------------------------------------
    # STEP 2 — INVITE SELF TALK
    # -------------------------------------------------

    if step == "invite_self_talk":

        spiral_stage = classify_spiral(user_text)

        instruction = """
Invite them to imagine speaking to themselves gently.
Ask:
"If a close friend felt this way, what would you tell them?"
Keep it soft.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {
            "step": "reinforce",
            "text": text
        }

    # -------------------------------------------------
    # STEP 3 — REINFORCE
    # -------------------------------------------------

    if step == "reinforce":

        spiral_stage = classify_spiral(user_text)

        instruction = f"""
User said: "{user_text}"

Reflect their compassionate words.
Reinforce that offering that kindness to themselves matters.

Then gently ask:
"Would you like to stay with this softness for a moment?"
Keep it optional.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {
            "step": "continuation",
            "text": text
        }

    # -------------------------------------------------
    # STEP 4 — CONTINUATION
    # -------------------------------------------------

    if step == "continuation":

        spiral_stage = classify_spiral(user_text)
        decision = classify_yes_no(user_text)

        if decision == "YES":

            instruction = """
Guide one slow breath.
Encourage letting that self-kind tone stay.
Keep it gentle.
Close softly.
"""

            text = gpt_reply(history, instruction, spiral_stage)

            return {
                "step": "exit",
                "text": text
            }

        instruction = """
Acknowledge gently.
Reassure that even trying this matters.
Close warmly.
"""

        text = gpt_reply(history, instruction, spiral_stage)

        return {
            "step": "exit",
            "text": text
        }

    # -------------------------------------------------
    # STEP 5 — EXIT
    # -------------------------------------------------

    return {
        "step": "exit",
        "text": "We can pause here."
    }