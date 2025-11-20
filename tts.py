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
# # /backend/tts.py
# import os
# import logging
# from typing import Iterator
# from openai import OpenAI

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# if not OPENAI_API_KEY:
#     raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

# client = OpenAI(api_key=OPENAI_API_KEY)

# def stream_tts_from_openai(text: str, chunk_size: int = 4096) -> Iterator[bytes]:
#     """
#     Generator that streams OpenAI TTS audio chunks (MP3 format).
#     Replaces ElevenLabs with OpenAI TTS API.
#     """
#     if not text:
#         logger.warning("TTS called with empty text")
#         yield b""
#         return

#     if not OPENAI_API_KEY:
#         logger.error("OPENAI_API_KEY is empty at runtime")
#         yield b""
#         return

#     try:
#         logger.info("Requesting OpenAI TTS: text_len=%d", len(text))
        
#         # OpenAI TTS streaming
#         response = client.audio.speech.create(
#             model="tts-1",  # Use "tts-1-hd" for higher quality
#             voice="alloy",  # Options: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
#             input=text,
#             response_format="mp3"
#         )
        
#         logger.info("OpenAI TTS response received successfully")
        
#         # Stream the audio content
#         for chunk in response.iter_bytes(chunk_size=chunk_size):
#             if chunk:
#                 yield chunk
                
#     except Exception as e:
#         logger.exception("Unexpected error streaming OpenAI TTS: %s", e)
#         yield b""
import os
import logging
from flask import Blueprint, request, jsonify
from openai import OpenAI

bp = Blueprint('tts', __name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=OPENAI_API_KEY)

@bp.route('/tts', methods=['POST'])
def generate_tts_audio():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="url"  # Return URL to audio
        )
        audio_url = response.get("audio_url")
        if not audio_url:
            return jsonify({"error": "No audio URL returned"}), 500
        return jsonify({"audio_url": audio_url})
    except Exception as e:
        logging.exception("TTS generation failed")
        return jsonify({"error": str(e)}), 500