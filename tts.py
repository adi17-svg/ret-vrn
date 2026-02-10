
# # tts.py
# import os
# from openai import OpenAI

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("Missing OPENAI_API_KEY for TTS")

# _client = OpenAI(api_key=OPENAI_API_KEY)

# def stream_tts_from_openai(text: str):
#     """
#     Generator: OpenAI TTS se PCM/MP3 bytes stream karta hai.
#     Flask Response(generator, mimetype='audio/mpeg') ke saath use karo.
#     """
#     # MP3 chahiye to response_format='mp3' ya fast streaming ke liye 'pcm'
#     with _client.audio.speech.with_streaming_response.create(
#         model="gpt-4o-mini-tts",   # ya tumhara jo TTS model ho
#         voice="alloy",             # ya koi bhi supported voice
#         input=text,
#         response_format="mp3",     # ⚠️ Yahi kaafi important change hai
#     ) as response:
#         for chunk in response.iter_bytes(chunk_size=4096):
#             if not chunk:
#                 continue
#             yield chunk

# tts.py
import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY for TTS")

_client = OpenAI(api_key=OPENAI_API_KEY)

def stream_tts_from_openai(text: str):
    """
    Generator: OpenAI TTS se PCM/MP3 bytes stream karta hai.
    Flask Response(generator, mimetype='audio/mpeg') ke saath use karo.
    """
    # MP3 chahiye to response_format='mp3' ya fast streaming ke liye 'pcm'
    with _client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",   # ya tumhara jo TTS model ho
        voice="alloy",             # ya koi bhi supported voice
        input=text,
        response_format="pcm",     # ⚠️ Yahi kaafi important change hai
    ) as response:
        for chunk in response.iter_bytes(chunk_size=4096):
            if not chunk:
                continue
            yield chunk