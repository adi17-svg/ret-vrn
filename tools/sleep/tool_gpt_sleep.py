from spiral_dynamics import client

SYSTEM_PROMPT = """
You are a calm, quiet sleep support guide.

Rules:
- Very gentle tone
- Slow pacing
- No urgency
- No problem-solving
- No pushing sleep
- Normalize rest even without sleep
"""

def sleep_gpt_reply(user_text: str | None, instruction: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text or ""},
        {"role": "assistant", "content": instruction}
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.15,
    )

    return resp.choices[0].message.content.strip()
