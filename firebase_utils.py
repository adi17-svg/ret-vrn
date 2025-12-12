
import time
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CONFIG

def init_firebase():
    """
    Initialize Firebase app and Firestore client.
    Returns the Firestore client instance or None if initialization fails.
    """
    try:
        # Initialize Firebase app with service account credentials
        cred = credentials.Certificate(FIREBASE_CONFIG)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        return None

# Initialize Firestore client at module load
db = init_firebase()


# ------------------------
# Conversation memory helpers
# ------------------------

def save_conversation_message(user_id: str, role: str, content: str, timestamp: int = None) -> bool:
    """
    Save a single conversation message for a user into Firestore.
    Collection path: conversations/{user_id}/messages/{timestamp_doc}
    role: 'user' | 'assistant' | 'system'
    content: message text
    timestamp: epoch ms, optional (generated if not provided)
    Returns True on success, False on failure.
    """
    try:
        if db is None:
            print("Firestore db not initialized - cannot save message.")
            return False
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        # Use timestamp as document id to keep ordering and avoid duplicates
        doc_ref = db.collection("conversations").document(str(user_id)).collection("messages").document(str(timestamp))
        payload = {
            "role": role,
            "content": content,
            "ts": timestamp
        }
        doc_ref.set(payload)
        return True
    except Exception as e:
        print("Error saving conversation message:", e)
        traceback.print_exc()
        return False


def get_recent_conversation(user_id: str, limit: int = 6):
    """
    Return a list of recent messages for a user ordered oldest->newest.
    Each item is a dict: {"role": "...", "content": "...", "ts": ...}
    If db not initialized or error, returns [].
    """
    try:
        if db is None:
            print("Firestore db not initialized - cannot fetch messages.")
            return []
        coll = db.collection("conversations").document(str(user_id)).collection("messages")
        # Query most recent first, then reverse to get oldest->newest
        docs = coll.order_by("ts", direction=firestore.Query.DESCENDING).limit(limit).stream()
        msgs = []
        for d in docs:
            data = d.to_dict()
            msgs.append({
                "role": data.get("role", "user"),
                "content": data.get("content", ""),
                "ts": data.get("ts", 0)
            })
        msgs.reverse()
        return msgs
    except Exception as e:
        print("Error fetching recent conversation:", e)
        traceback.print_exc()
        return []