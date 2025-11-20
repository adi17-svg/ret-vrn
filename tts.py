# /backend/tts.py
import os
import requests
from typing import Iterator

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")
VOICE_ID = os.getenv("VOICE_ID", "RILOU7YmBhvwJGDGjNmP")

def stream_tts_from_elevenlabs(text: str, chunk_size: int = 4096) -> Iterator[bytes]:
    """
    Generator that proxies ElevenLabs streaming TTS and yields raw audio chunks (MP3).
    Does NOT save files.
    """
    if not text:
        yield b""
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}

    try:
        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        resp.raise_for_status()
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
    except Exception:
        # On error yield a single empty chunk so caller doesn't hang
        yield b""
