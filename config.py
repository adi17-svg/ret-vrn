# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load environment variables from .env file

# A4F_API_KEY = os.getenv("A4F_API_KEY")
# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# NOTIFICATION_TIME = os.getenv("NOTIFICATION_TIME", "09:00")

# FIREBASE_CONFIG = {
#     "type": os.getenv("FIREBASE_TYPE"),
#     "project_id": os.getenv("FIREBASE_PROJECT_ID"),
#     "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
#     "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
#     "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
#     "client_id": os.getenv("FIREBASE_CLIENT_ID"),
#     "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
#     "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
#     "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
#     "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
#     "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
# }
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

A4F_API_KEY = os.getenv("A4F_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
# Backwards compatible single time (kept but not preferred)
NOTIFICATION_TIME = os.getenv("NOTIFICATION_TIME", "09:00")

# New: explicit morning & night notification times (HH:MM)
NOTIFICATION_TIME_MORNING = os.getenv("NOTIFICATION_TIME_MORNING", os.getenv("NOTIFICATION_TIME", "07:00"))
NOTIFICATION_TIME_NIGHT = os.getenv("NOTIFICATION_TIME_NIGHT", "21:00")

# Scheduler timezone: set to your users' timezone (e.g., "Asia/Kolkata") or "UTC"
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "UTC")

# Firebase config (guard against missing env vars and handle newline safely)
# NOTE: ensure FIREBASE_PRIVATE_KEY exists in env and contains literal \n sequences if exported from env file
_firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY") or ""
if _firebase_private_key:
    # if the key is stored with escaped newlines, convert them
    FIREBASE_PRIVATE_KEY = _firebase_private_key.replace('\\n', '\n')
else:
    FIREBASE_PRIVATE_KEY = None

FIREBASE_CONFIG = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
}
