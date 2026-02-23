"""
Low Mood Tool: It Makes Sense
Conversational Version
- History aware (last 6 messages)
- Spiral-toned validation
- Shame softening
- No abrupt exit
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6


# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT_BASE = """
You are a calm, validating mental health guide.

Rules:
- Keep responses short (2–4 lines)
- Warm and natural tone
- Validate emotions, not harmful behavior
- Never justify harmful actions
- No advice unless user clearly asks
- Create safety first
- Gently invite reflection
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
        "Classify emotional tone into one word: BLUE, RED, ORANGE, GREEN, or NEUTRAL.",
        user_text,
        ["BLUE", "RED", "ORANGE", "GREEN", "NEUTRAL"],
        "GREEN"
    )


# =====================================================
# SHAME DETECTION
# =====================================================

def detect_shame(user_text):

    if not user_text:
        return False

    shame_keywords = [
        "i'm stupid",
        "i am stupid",
        "i'm weak",
        "i am weak",
        "it's my fault",
        "i shouldn't feel",
        "i'm broken",
        "i am broken",
        "i'm too sensitive"
    ]

    lower = user_text.lower()
    return any(k in lower for k in shame_keywords)


# =====================================================
# SPIRAL-TONED LANGUAGE HELPERS
# =====================================================

def spiral_validation_line(stage):

    if stage == "BLUE":
        return "When doing the right thing matters to you, moments like this can sting."

    if stage == "ORANGE":
        return "When you hold yourself to high standards, setbacks can feel heavy."

    if stage == "RED":
        return "When emotions run intense, reactions can come fast."

    if stage == "GREEN":
        return "When connection and meaning matter deeply, moments like this can hurt."

    return "Given what you’ve been carrying, this reaction makes sense."


def spiral_curiosity(stage):

    if stage == "BLUE":
        return "What part of this feels most misaligned for you?"

    if stage == "ORANGE":
        return "What part of this feels most frustrating right now?"

    if stage == "RED":
        return "What felt most intense in that moment?"

    if stage == "GREEN":
        return "What part of this still feels tender?"

    return "What feels most present right now?"


def spiral_micro_shift(stage):

    if stage == "BLUE":
        return "If you'd like, we can look at one small corrective step."

    if stage == "ORANGE":
        return "If you'd like, we can look at one very small next step."

    if stage == "RED":
        return "If you'd like, we can slow this down just a little."

    if stage == "GREEN":
        return "If you'd like, we can stay with this gently for a moment."

    return "If you'd like, we can take a small step next."


# =====================================================
# GPT REPLY (History Aware)
# =====================================================

def gpt_reply(history, instruction):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_BASE},
    ]

    if history:
        recent = history[-HISTORY_LIMIT:]

        for msg in recent:
            role = "assistant" if msg.get("type") == "assistant" else "user"
            content = msg.get("text", "")
            if content:
                messages.append({
                    "role": role,
                    "content": content
                })

    messages.append({
        "role": "user",
        "content": instruction
    })

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

    spiral_stage = classify_spiral(user_text)
    shame_detected = detect_shame(user_text)

    # Always conversational mode
    if not user_text:
        return {
            "step": "continue",
            "text": "I'm here with you. What feels heavy right now?"
        }

    # Build layered validation instruction
    instruction = f"""
User said: "{user_text}"

1. Briefly validate the emotional experience.
2. Use this tone framing if helpful: "{spiral_validation_line(spiral_stage)}"
3. If self-judgment is present, gently soften it.
4. Add one safety-oriented line.
5. Ask this reflective question: "{spiral_curiosity(spiral_stage)}"
6. Optionally add: "{spiral_micro_shift(spiral_stage)}"
Keep it natural and human.
Do NOT justify harmful behavior.
"""

    text = gpt_reply(history, instruction)

    return {
        "step": "continue",
        "text": text
    }