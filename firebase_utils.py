
# import time
# import traceback
# import firebase_admin
# from firebase_admin import credentials, firestore
# from config import FIREBASE_CONFIG

# def init_firebase():
#     """
#     Initialize Firebase app and Firestore client.
#     Returns the Firestore client instance or None if initialization fails.
#     """
#     try:
#         # Initialize Firebase app with service account credentials
#         cred = credentials.Certificate(FIREBASE_CONFIG)
#         if not firebase_admin._apps:
#             firebase_admin.initialize_app(cred)
#         db = firestore.client()
#         return db
#     except Exception as e:
#         print(f"Firebase initialization failed: {e}")
#         return None

# # Initialize Firestore client at module load
# db = init_firebase()


# # ------------------------
# # Conversation memory helpers
# # ------------------------

# def save_conversation_message(user_id: str, role: str, content: str, timestamp: int = None) -> bool:
#     """
#     Save a single conversation message for a user into Firestore.
#     Collection path: conversations/{user_id}/messages/{timestamp_doc}
#     role: 'user' | 'assistant' | 'system'
#     content: message text
#     timestamp: epoch ms, optional (generated if not provided)
#     Returns True on success, False on failure.
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot save message.")
#             return False
#         if timestamp is None:
#             timestamp = int(time.time() * 1000)
#         # Use timestamp as document id to keep ordering and avoid duplicates
#         doc_ref = db.collection("conversations").document(str(user_id)).collection("messages").document(str(timestamp))
#         payload = {
#             "role": role,
#             "content": content,
#             "ts": timestamp
#         }
#         doc_ref.set(payload)
#         return True
#     except Exception as e:
#         print("Error saving conversation message:", e)
#         traceback.print_exc()
#         return False


# def get_recent_conversation(user_id: str, limit: int = 6):
#     """
#     Return a list of recent messages for a user ordered oldest->newest.
#     Each item is a dict: {"role": "...", "content": "...", "ts": ...}
#     If db not initialized or error, returns [].
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot fetch messages.")
#             return []
#         coll = db.collection("conversations").document(str(user_id)).collection("messages")
#         # Query most recent first, then reverse to get oldest->newest
#         docs = coll.order_by("ts", direction=firestore.Query.DESCENDING).limit(limit).stream()
#         msgs = []
#         for d in docs:
#             data = d.to_dict()
#             msgs.append({
#                 "role": data.get("role", "user"),
#                 "content": data.get("content", ""),
#                 "ts": data.get("ts", 0)
#             })
#         msgs.reverse()
#         return msgs
#     except Exception as e:
#         print("Error fetching recent conversation:", e)
#         traceback.print_exc()
#         return []
# import time
# import traceback
# import firebase_admin
# from firebase_admin import credentials, firestore
# from config import FIREBASE_CONFIG


# def init_firebase():
#     """
#     Initialize Firebase app and Firestore client.
#     Returns the Firestore client instance or None if initialization fails.
#     """
#     try:
#         # Initialize Firebase app with service account credentials
#         cred = credentials.Certificate(FIREBASE_CONFIG)

#         # Initialize only once
#         if not firebase_admin._apps:
#             firebase_admin.initialize_app(cred)

#             # 🔥 DEBUG: Confirm which project backend is using
#             print("🔥 BACKEND PROJECT:", firebase_admin.get_app().project_id)

#         db = firestore.client()
#         return db

#     except Exception as e:
#         print(f"Firebase initialization failed: {e}")
#         traceback.print_exc()
#         return None


# # Initialize Firestore client at module load
# db = init_firebase()


# # ------------------------
# # Conversation memory helpers
# # ------------------------

# def save_conversation_message(user_id: str, role: str, content: str, timestamp: int = None) -> bool:
#     """
#     Save a single conversation message for a user into Firestore.
#     Collection path: conversations/{user_id}/messages/{timestamp_doc}
#     role: 'user' | 'assistant' | 'system'
#     content: message text
#     timestamp: epoch ms, optional (generated if not provided)
#     Returns True on success, False on failure.
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot save message.")
#             return False

#         if timestamp is None:
#             timestamp = int(time.time() * 1000)

#         doc_ref = (
#             db.collection("conversations")
#               .document(str(user_id))
#               .collection("messages")
#               .document(str(timestamp))
#         )

#         payload = {
#             "role": role,
#             "content": content,
#             "ts": timestamp
#         }

#         doc_ref.set(payload)
#         return True

#     except Exception as e:
#         print("Error saving conversation message:", e)
#         traceback.print_exc()
#         return False


# def get_recent_conversation(user_id: str, limit: int = 6):
#     """
#     Return a list of recent messages for a user ordered oldest->newest.
#     Each item is a dict: {"role": "...", "content": "...", "ts": ...}
#     If db not initialized or error, returns [].
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot fetch messages.")
#             return []

#         coll = (
#             db.collection("conversations")
#               .document(str(user_id))
#               .collection("messages")
#         )

#         docs = (
#             coll.order_by("ts", direction=firestore.Query.DESCENDING)
#                 .limit(limit)
#                 .stream()
#         )

#         msgs = []
#         for d in docs:
#             data = d.to_dict()
#             msgs.append({
#                 "role": data.get("role", "user"),
#                 "content": data.get("content", ""),
#                 "ts": data.get("ts", 0)
#             })

#         msgs.reverse()
#         return msgs

#     except Exception as e:
#         print("Error fetching recent conversation:", e)
#         traceback.print_exc()
#         return []
# import time
# import traceback
# import firebase_admin
# from firebase_admin import credentials, firestore
# from config import FIREBASE_CONFIG


# def init_firebase():
#     """
#     Initialize Firebase app and Firestore client.
#     Returns the Firestore client instance or None if initialization fails.
#     """
#     try:
#         cred = credentials.Certificate(FIREBASE_CONFIG)

#         if not firebase_admin._apps:
#             firebase_admin.initialize_app(cred)
#             print("🔥 BACKEND PROJECT:", firebase_admin.get_app().project_id)

#         db = firestore.client()
#         return db

#     except Exception as e:
#         print(f"Firebase initialization failed: {e}")
#         traceback.print_exc()
#         return None


# # Initialize Firestore client at module load
# db = init_firebase()


# # ------------------------
# # Conversation memory helpers
# # ------------------------

# def save_conversation_message(user_id: str, role: str, content: str, tool_id: str = None, timestamp: int = None) -> bool:
#     """
#     Save a single conversation message for a user into Firestore.
#     Collection path: users/{user_id}/supportSessions/{tool_id}/messages/{timestamp_doc}
#     role: 'user' | 'assistant' | 'system'
#     content: message text
#     tool_id: tool identifier (optional, defaults to 'general')
#     timestamp: epoch ms, optional (generated if not provided)
#     Returns True on success, False on failure.
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot save message.")
#             return False

#         if timestamp is None:
#             timestamp = int(time.time() * 1000)

#         doc_ref = (
#             db.collection("users")
#               .document(str(user_id))
#               .collection("supportSessions")
#               .document(str(tool_id) if tool_id else "general")
#               .collection("messages")
#               .document(str(timestamp))
#         )

#         payload = {
#             "role": role,
#             "content": content,
#             "ts": timestamp
#         }

#         doc_ref.set(payload)
#         return True

#     except Exception as e:
#         print("Error saving conversation message:", e)
#         traceback.print_exc()
#         return False


# def get_recent_conversation(user_id: str, tool_id: str = None, limit: int = 6):
#     """
#     Return a list of recent messages for a user ordered oldest->newest.
#     Collection path: users/{user_id}/supportSessions/{tool_id}/messages
#     Each item is a dict: {"role": "...", "content": "...", "ts": ...}
#     If db not initialized or error, returns [].
#     """
#     try:
#         if db is None:
#             print("Firestore db not initialized - cannot fetch messages.")
#             return []

#         coll = (
#             db.collection("users")
#               .document(str(user_id))
#               .collection("supportSessions")
#               .document(str(tool_id) if tool_id else "general")
#               .collection("messages")
#         )

#         docs = (
#             coll.order_by("ts", direction=firestore.Query.DESCENDING)
#                 .limit(limit)
#                 .stream()
#         )

#         msgs = []
#         for d in docs:
#             data = d.to_dict()
#             msgs.append({
#                 "role": data.get("role", "user"),
#                 "content": data.get("content", ""),
#                 "ts": data.get("ts", 0)
#             })

#         msgs.reverse()
#         return msgs

#     except Exception as e:
#         print("Error fetching recent conversation:", e)
#         traceback.print_exc()
#         return []
import time
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CONFIG


def init_firebase():
    try:
        cred = credentials.Certificate(FIREBASE_CONFIG)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("🔥 BACKEND PROJECT:", firebase_admin.get_app().project_id)

        db = firestore.client()
        return db

    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        traceback.print_exc()
        return None


# Initialize Firestore client at module load
db = init_firebase()


# ------------------------
# Conversation memory helpers
# ------------------------

def save_conversation_message(user_id: str, role: str, content: str, tool_id: str, timestamp: int = None) -> bool:
    """
    Save a single conversation message for a user into Firestore.
    Path: users/{user_id}/supportSessions/{tool_id}/messages/{timestamp_doc}
    Saves with Flutter-compatible field names: type, text, timestamp
    """
    try:
        if db is None:
            print("Firestore db not initialized - cannot save message.")
            return False

        if timestamp is None:
            timestamp = int(time.time() * 1000)

        print(f"💾 Saving to: users/{user_id}/supportSessions/{tool_id}/messages/{timestamp}")

        doc_ref = (
            db.collection("users")
              .document(str(user_id))
              .collection("supportSessions")
              .document(str(tool_id))
              .collection("messages")
              .document(str(timestamp))
        )

        payload = {
            "type": role,            # ✅ Flutter reads 'type'
            "text": content,         # ✅ Flutter reads 'text'
            "timestamp": timestamp,  # ✅ Flutter orderBy('timestamp')
            "ts": timestamp          # ✅ Python ordering
        }

        doc_ref.set(payload)
        print(f"✅ Saved successfully: {role} message for tool {tool_id}")
        return True

    except Exception as e:
        print("Error saving conversation message:", e)
        traceback.print_exc()
        return False


def get_recent_conversation(user_id: str, tool_id: str, limit: int = 6):
    """
    Return a list of recent messages for AI context, ordered oldest->newest.
    Path: users/{user_id}/supportSessions/{tool_id}/messages
    Returns standard AI format: {"role": "...", "content": "...", "ts": ...}
    """
    try:
        if db is None:
            print("Firestore db not initialized - cannot fetch messages.")
            return []

        print(f"📖 Fetching from: users/{user_id}/supportSessions/{tool_id}/messages")

        coll = (
            db.collection("users")
              .document(str(user_id))
              .collection("supportSessions")
              .document(str(tool_id))
              .collection("messages")
        )

        docs = (
            coll.order_by("ts", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
        )

        msgs = []
        for d in docs:
            data = d.to_dict()
            msgs.append({
                "role": data.get("type", "user"),    # ✅ map 'type' → 'role' for AI
                "content": data.get("text", ""),     # ✅ map 'text' → 'content' for AI
                "ts": data.get("ts", 0)
            })

        msgs.reverse()
        print(f"✅ Fetched {len(msgs)} messages for tool {tool_id}")
        return msgs

    except Exception as e:
        print("Error fetching recent conversation:", e)
        traceback.print_exc()
        return []