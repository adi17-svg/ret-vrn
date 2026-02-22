"""
Low Mood Tool: Self Compassion
Clean Version – No READY gate
Context-aware (last 6 messages)
"""

from openai import OpenAI

client = OpenAI()

HISTORY_LIMIT = 6

# =====================================================
# SYSTEM PROMPT
# =====================================================

BASE_PROMPT = """
You are a calm, warm self-compassion guide.

Rules:
- Warm, human tone
- No advice
- No fixing
- No problem solving
- Keep responses short (3–5 lines)
- Validate first
- Encourage gentle inner tone
"""

# =====================================================
# GPT CALL (last 6 messages only)
# =====================================================

def gpt_reply(history, user_text):

    messages = [
        {"role": "system", "content": BASE_PROMPT},
    ]

    # Only last 6 messages for emotional continuity
    if history:
        recent = history[-HISTORY_LIMIT:]
        messages.extend(recent)

    messages.append({
        "role": "user",
        "content": f'User just said: "{user_text}"\nRespond with warmth and self-compassion.'
    })

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


# =====================================================
# HANDLE
# =====================================================

def handle(step=None, user_text=None, history=None):

    history = history or []
    user_text = (user_text or "").strip()

    # If user says nothing
    if not user_text:
        return {
            "step": "continue",
            "text": "I’m here with you. What feels heavy right now?"
        }

    # Generate warm reply based on history + input
    text = gpt_reply(history, user_text)

    return {
        "step": "continue",
        "text": text
    }