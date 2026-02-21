"""
Low Mood Tool: 5-4-3-2-1 Grounding (Context + Spiral Aware)

Design:
- Independent GPT usage
- Spiral-aware tone (internal only)
- Uses full chat history
- Step-by-step progression
- Implicit confirmation (waits for user reply)
- Skip support
- Gentle adaptive close
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm grounding guide.

Rules:
- Calm tone
- Short instructions
- Step-by-step only
- No analysis
- No therapy explanations
- Keep language simple
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
        "Classify into one word: YES, NO, or STOP.",
        user_text,
        ["YES", "NO", "STOP"],
        "YES"
    )


def classify_state_response(user_text):
    return safe_classify(
        "Classify into one word: CALMER, SAME, UNSETTLED.",
        user_text,
        ["CALMER", "SAME", "UNSETTLED"],
        "SAME"
    )


# =====================================================
# GPT REPLY (SPIRAL + CONTEXT AWARE)
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

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": instruction})

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# MAIN HANDLER
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    spiral_stage = classify_spiral(user_text) if user_text else "GREEN"

    # =================================================
    # STEP 0 — PERMISSION
    # =================================================
    if step is None or step == "start":

        text = gpt_reply(
            history,
            "Would it feel okay to try a short grounding exercise together?",
            spiral_stage
        )

        return {"step": "permission", "text": text}

    # =================================================
    # STEP 1 — HANDLE PERMISSION
    # =================================================
    if step == "permission":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":
            text = gpt_reply(
                history,
                "Let’s begin. Name 5 things you can see around you.",
                spiral_stage
            )
            return {"step": "five", "text": text}

        return {
            "step": "exit",
            "text": "That's completely okay. We can pause here."
        }

    # =================================================
    # STEP 2 — 5 THINGS
    # =================================================
    if step == "five":

        text = gpt_reply(
            history,
            "Good. Now notice 4 physical sensations — what you can feel right now.",
            spiral_stage
        )

        return {"step": "four", "text": text}

    # =================================================
    # STEP 3 — 4 SENSATIONS
    # =================================================
    if step == "four":

        if user_text and user_text.lower().strip() in ["skip", "none", "can't"]:
            pass

        text = gpt_reply(
            history,
            "Now listen for 3 different sounds around you.",
            spiral_stage
        )

        return {"step": "three", "text": text}

    # =================================================
    # STEP 4 — 3 SOUNDS
    # =================================================
    if step == "three":

        text = gpt_reply(
            history,
            "Notice 2 smells. If you can’t find any, that’s okay.",
            spiral_stage
        )

        return {"step": "two", "text": text}

    # =================================================
    # STEP 5 — 2 SMELLS
    # =================================================
    if step == "two":

        if user_text and user_text.lower().strip() in ["skip", "none"]:
            pass

        text = gpt_reply(
            history,
            "Finally, notice 1 taste or small pleasant sensation.",
            spiral_stage
        )

        return {"step": "one", "text": text}

    # =================================================
    # STEP 6 — CHECK STATE
    # =================================================
    if step == "one":

        text = gpt_reply(
            history,
            "Take a moment. How does your body feel now?",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # =================================================
    # ADAPTIVE CLOSE
    # =================================================
    if step == "check":

        state = classify_state_response(user_text or "")

        if state == "CALMER":
            text = gpt_reply(
                history,
                "Even a small sense of steadiness matters. Let’s pause here.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if state == "SAME":
            text = gpt_reply(
                history,
                "Sometimes grounding works quietly. That’s okay.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if state == "UNSETTLED":
            text = gpt_reply(
                history,
                "Let’s take one slow breath together before we stop.",
                spiral_stage
            )
            return {"step": "exit", "text": text}

    # =================================================
    # FALLBACK
    # =================================================
    return {"step": "exit", "text": "You’re here. That’s enough for now."}