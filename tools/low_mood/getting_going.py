"""
Low Mood Tool: Getting Going With Action (FINAL CLEAN)

Features:
- Spiral-aware activation framing (internal only)
- Energy-level adaptive micro-actions
- Action success reinforcement layer
- Smart start detection (no repeated question)
- Strict flow control
- Independent GPT usage
"""

from openai import OpenAI

client = OpenAI()

# =====================================================
# BASE SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, supportive mental health coach.

Rules:
- Keep responses short (2–4 lines)
- Sound natural and human
- Never command harshly
- Use permission before action
- Once user agrees, STOP asking questions
- Guide action clearly and simply
- Respect resistance
"""

# =====================================================
# CLASSIFIERS
# =====================================================

def classify_spiral(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Classify into one word: BEIGE, PURPLE, RED, BLUE, ORANGE, GREEN, or YELLOW."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def classify_energy(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Classify into one word: LOW, MEDIUM, or HIGH."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def classify_yes_no(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Classify into one word: YES, NO, or UNCLEAR."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def classify_shift(user_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Classify into one word: BETTER, SAME, or WORSE."},
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()


# =====================================================
# GPT REPLY
# =====================================================

def gpt_reply(history, instruction, spiral_stage=None):

    system_prompt = SYSTEM_PROMPT_BASE

    if spiral_stage:
        system_prompt += f"""

User tendency appears closer to {spiral_stage}.
Adjust activation framing subtly.
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

    spiral_stage = classify_spiral(user_text) if user_text else None
    energy_level = classify_energy(user_text) if user_text else "LOW"

    # -------------------------------------------------
    # STEP 0 — SMART START (NO REPEAT QUESTION)
    # -------------------------------------------------
    if step is None or step == "start":

        if user_text:
            # User already shared difficulty → acknowledge directly
            text = gpt_reply(
                history,
                f"""
User said: "{user_text}"

Normalize low energy.
Acknowledge the difficulty briefly.
Do not ask another question.
""",
                spiral_stage
            )
            return {"step": "offer", "text": text}

        # If no context yet → ask
        text = gpt_reply(
            history,
            """
Normalize low energy.
Explain we’ll take one very small step.
Ask what feels hardest to start right now.
""",
            spiral_stage
        )
        return {"step": "ack", "text": text}

    # -------------------------------------------------
    # STEP 1 — OFFER MICRO ACTION
    # -------------------------------------------------
    if step == "offer":

        if energy_level == "LOW":
            action_prompt = "Offer a 10–20 second ultra-small action."
        elif energy_level == "MEDIUM":
            action_prompt = "Offer a 30-second small action."
        else:
            action_prompt = "Offer a simple 1-minute action."

        text = gpt_reply(
            history,
            f"""
{action_prompt}
Ask permission gently.
Once user agrees, do not ask further questions.
""",
            spiral_stage
        )

        return {"step": "consent", "text": text}

    # -------------------------------------------------
    # STEP 2 — CONSENT
    # -------------------------------------------------
    if step == "consent":

        decision = classify_yes_no(user_text or "")

        if decision == "YES":
            text = gpt_reply(
                history,
                """
Acknowledge agreement.
Say we’ll start now.
Transition directly into doing.
No questions.
""",
                spiral_stage
            )
            return {"step": "do", "text": text}

        text = gpt_reply(
            history,
            """
Normalize hesitation.
Reinforce stopping is okay.
Close gently.
""",
            spiral_stage
        )
        return {"step": "exit", "text": text}

    # -------------------------------------------------
    # STEP 3 — DO ACTION
    # -------------------------------------------------
    if step == "do":

        text = gpt_reply(
            history,
            """
Guide the small action clearly.
Simple steps.
Keep it short.
No questions.
""",
            spiral_stage
        )

        return {"step": "check", "text": text}

    # -------------------------------------------------
    # STEP 4 — CHECK RESULT
    # -------------------------------------------------
    if step == "check":

        text = gpt_reply(
            history,
            """
Gently ask:
"How did that feel?"
Keep it simple.
""",
            spiral_stage
        )

        return {"step": "reinforce", "text": text}

    # -------------------------------------------------
    # STEP 5 — REINFORCE
    # -------------------------------------------------
    if step == "reinforce":

        result = classify_shift(user_text or "")

        if result == "BETTER":
            text = gpt_reply(
                history,
                """
Acknowledge the shift.
Reinforce that small actions build momentum.
Close warmly.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if result == "SAME":
            text = gpt_reply(
                history,
                """
Normalize subtle change.
Reinforce that taking action still counts.
Close gently.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

        if result == "WORSE":
            text = gpt_reply(
                history,
                """
Acknowledge gently.
Suggest stopping and taking one slow breath instead.
Close softly.
""",
                spiral_stage
            )
            return {"step": "exit", "text": text}

    return {"step": "exit", "text": "We can pause here. You're in control."}
