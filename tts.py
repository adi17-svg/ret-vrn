# # /backend/tts.py
# import os
# import requests
# from typing import Iterator

# ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")
# VOICE_ID = os.getenv("VOICE_ID", "RILOU7YmBhvwJGDGjNmP")

# def stream_tts_from_elevenlabs(text: str, chunk_size: int = 4096) -> Iterator[bytes]:
#     """
#     Generator that proxies ElevenLabs streaming TTS and yields raw audio chunks (MP3).
#     Does NOT save files.
#     """
#     if not text:
#         yield b""
#         return

#     url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
#     headers = {
#         "xi-api-key": ELEVEN_API_KEY,
#         "Content-Type": "application/json"
#     }
#     payload = {"text": text, "model_id": "eleven_multilingual_v2"}

#     try:
#         resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
#         resp.raise_for_status()
#         for chunk in resp.iter_content(chunk_size=chunk_size):
#             if chunk:
#                 yield chunk
#     except Exception:
#         # On error yield a single empty chunk so caller doesn't hang
#         yield b""
# /backend/tts.py
import os
import requests
import logging
from typing import Iterator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")
VOICE_ID = os.getenv("VOICE_ID", "RILOU7YmBhvwJGDGjNmP")

def stream_tts_from_elevenlabs(text: str, chunk_size: int = 4096) -> Iterator[bytes]:
    """
    Generator that proxies ElevenLabs streaming TTS and yields raw audio chunks (MP3).
    """
    if not text:
        logger.warning("TTS called with empty text")
        yield b""
        return

    if not ELEVEN_API_KEY:
        logger.error("ELEVEN_API_KEY is empty at runtime")
        yield b""
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}

    try:
        logger.info("Requesting ElevenLabs TTS: voice=%s text_len=%d", VOICE_ID, len(text))
        resp = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
        logger.info("ElevenLabs responded: %s %s", resp.status_code, resp.reason)
        resp.raise_for_status()
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
    except requests.HTTPError as he:
        # log server error body if any
        try:
            logger.exception("ElevenLabs HTTP error: %s body: %s", he, resp.text[:1000])
        except Exception:
            logger.exception("ElevenLabs HTTP error: %s (no body available)", he)
        # yield a small empty chunk to avoid client hanging
        yield b""
    except Exception as e:
        logger.exception("Unexpected error streaming TTS: %s", e)
        yield b""
