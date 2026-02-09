
# from flask import Blueprint, request, jsonify
# from datetime import datetime, timezone
# import traceback
# import hashlib
# from firebase_admin import messaging
# from firebase_utils import db  # Your Firestore client instance
# from tasks import generate_daily_task  # Adjust path as needed

# bp = Blueprint('notifications', __name__)

# # You need to define and manage these globally or in app context appropriately
# NOTIFICATION_TIME = "19:30"  # example initial notification time placeholder
# scheduler = None  # reference to your APScheduler instance
# def schedule_notifications():
#     # Implement your scheduler job registration here
#     pass

# @bp.route('/set_notification_time', methods=['POST'])
# def set_notification_time():
#     global NOTIFICATION_TIME
#     try:
#         data = request.get_json()
#         new_time = data.get('time')
#         # Validate time format HH:MM
#         try:
#             hour, minute = map(int, new_time.split(':'))
#             if not (0 <= hour <= 23 and 0 <= minute <= 59):
#                 raise ValueError
#         except Exception:
#             return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

#         NOTIFICATION_TIME = new_time
#         if scheduler:
#             try:
#                 scheduler.remove_job("daily_task")
#             except Exception:
#                 pass
#             schedule_notifications()
#         return jsonify({'status': 'success', 'new_time': NOTIFICATION_TIME})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @bp.route('/send_welcome', methods=['POST'])
# def send_welcome():
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')
#         fcm_token = data.get('fcm_token')
#         if not user_id or not fcm_token:
#             return jsonify({'error': 'Missing user_id or fcm_token'}), 400

#         response = send_welcome_notification(fcm_token)

#         db.collection('users').document(user_id).collection('mergedMessages').add({
#             'type': 'welcome',
#             'message': 'What’s on your mind right now? Write or speak freely—no filters.',
#             'timestamp': datetime.now(timezone.utc),
#             'from': 'system',
#             'is_notification': True
#         })

#         return jsonify({'status': 'success', 'message': 'Welcome notification sent'})
#     except Exception:
#         traceback.print_exc()
#         return jsonify({'error': 'Failed to send welcome notification'}), 500

# def send_welcome_notification(token):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title='Welcome to Spiral Dynamics',
#                 body='What’s on your mind right now? Write or speak freely—no filters.'
#             ),
#             token=token,
#         )
#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f'Error sending welcome notification: {e}')
#         return None

# def send_daily_task_notification(fcm_token, task_text):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()
#         notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat",
#                 "notification_id": notification_id
#             },
#             token=fcm_token,
#             android=messaging.AndroidConfig(collapse_key=notification_id),
#             apns=messaging.APNSConfig(headers={"apns-collapse-id": notification_id})
#         )

#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f"Error sending notification: {e}")
#         return None

# def has_received_today(user_id):
#     today = datetime.now(timezone.utc).date().isoformat()
#     messages_ref = db.collection('users').document(user_id).collection('mergedMessages')
#     query = messages_ref.where('is_notification', '==', True).where('date', '==', today).limit(1)
#     docs = query.stream()
#     return any(True for _ in docs)

# def send_daily_task_to_all():
#     try:
#         task_data = generate_daily_task()
#         task_text = task_data['task']
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat"
#             },
#             topic="daily_task"
#         )
#         response = messaging.send(message)
#         print(f"✅ Topic notification sent: {response}")

#         users_ref = db.collection('users')
#         batch = db.batch()
#         for user_doc in users_ref.stream():
#             user_id = user_doc.id
#             if has_received_today(user_id):
#                 continue
#             notification_ref = db.collection('users').document(user_id).collection('mergedMessages').document()
#             batch.set(notification_ref, {
#                 'type': 'daily_task',
#                 'message': task_text,
#                 'timestamp': datetime.now(timezone.utc),
#                 'from': 'system',
#                 'is_notification': True,
#                 'date': today
#             })
#         batch.commit()
#     except Exception as e:
#         print(f"Error in sending daily task notifications: {e}")

# def send_all_daily_tasks():
#     try:
#         # Generate or fetch today's shared task
#         task_data = generate_daily_task()
#         task_text = task_data["task"]
#         today = datetime.now(timezone.utc).date().isoformat()

#         # ✅ Send one message to the topic
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 Your Daily Spiral Task",
#                 body=task_text
#             ),
#             data={
#                 "type": "daily_task",
#                 "task": task_text,
#                 "screen": "chat"
#             },
#             topic="daily_task"
#         )

#         response = messaging.send(message)
#         print(f"✅ Topic notification sent: {response}")

#         # ✅ Log one bot-message per user in Firestore
#         users_ref = db.collection("users")
#         batch = db.batch()
#         for user_doc in users_ref.stream():
#             user_id = user_doc.id
#             if has_received_today(user_id):
#                 continue
#             notification_ref = db.collection("users").document(user_id)\
#                 .collection("mergedMessages").document()
#             batch.set(notification_ref, {
#                 "type": "daily_task",
#                 "message": task_text,
#                 "timestamp": datetime.now(timezone.utc),
#                 "from": "system",
#                 "is_notification": True,
#                 "date": today
#             })
#         batch.commit()

#     except Exception as e:
#         print(f"Error in send_all_daily_tasks: {e}")

# from flask import Blueprint, request, jsonify
# from datetime import datetime, timezone
# import traceback
# from firebase_admin import messaging
# from firebase_utils import db

# bp = Blueprint("notifications", __name__)

# # ============================================================
# # 1️⃣ SEND MORNING INTENTION NOTIFICATION (SAME WAY AS BEFORE)
# # ============================================================

# def send_morning_intention_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌅 A gentle start to your day",
#                 body="Would you like to set a small intention for today?"
#             ),
#             data={
#                 "type": "morning_intention",
#                 "screen": "intention",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         response = messaging.send(message)
#         return response

#     except Exception as e:
#         print(f"❌ Error sending morning intention notification: {e}")
#         return None


# # ============================================================
# # 2️⃣ STORE USER SELECTED INTENTION
# # ============================================================

# @bp.route("/set_intention", methods=["POST"])
# def set_intention():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         intention = data.get("intention")

#         if not user_id or not intention:
#             return jsonify({"error": "Missing user_id or intention"}), 400

#         today = datetime.now(timezone.utc).date().isoformat()

#         # 🔹 Save intention in user document
#         db.collection("users").document(user_id).set(
#             {
#                 "today_intention": intention,
#                 "intention_date": today,
#                 "intention_set_at": datetime.now(timezone.utc),
#             },
#             merge=True
#         )

#         # 🔹 Log system message (same pattern as before)
#         db.collection("users") \
#             .document(user_id) \
#             .collection("mergedMessages") \
#             .add({
#                 "type": "intention",
#                 "message": f"🎯 Today’s intention: {intention}",
#                 "timestamp": datetime.now(timezone.utc),
#                 "from": "system",
#                 "is_notification": False,
#                 "date": today,
#             })

#         return jsonify({"status": "success", "intention": intention})

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to store intention"}), 500


# # ============================================================
# # 3️⃣ OPTIONAL: WELCOME NOTIFICATION (UNCHANGED)
# # ============================================================

# def send_welcome_notification(token):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="Welcome to RETVRN",
#                 body="What’s on your mind right now? Write or speak freely."
#             ),
#             token=token,
#         )
#         return messaging.send(message)
#     except Exception as e:
#         print(f"Error sending welcome notification: {e}")
# #         return None
# from flask import Blueprint, request, jsonify
# from datetime import datetime, timezone
# import traceback
# from firebase_admin import messaging

# from firebase_utils import db

# bp = Blueprint("notifications", __name__)

# # ============================================================
# # 🌅 MORNING INTENTION NOTIFICATION
# # ============================================================

# def send_morning_intention_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌅 A gentle start to your day",
#                 body="Would you like to set a small intention for today?"
#             ),
#             data={
#                 "type": "morning_intention",
#                 "screen": "intention",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Error sending morning notification: {e}")
#         return None


# # ============================================================
# # 🌙 NIGHT REFLECTION NOTIFICATION (ROTATING)
# # ============================================================

# NIGHT_PROMPTS = [
#     {
#         "title": "🌙 Before you rest",
#         "body": "How did today feel for you — not good or bad, just honestly?"
#     },
#     {
#         "title": "🌙 A quiet moment",
#         "body": "Was there one small moment today that stayed with you?"
#     },
#     {
#         "title": "🌙 End of the day",
#         "body": "Is there anything you’d like to leave behind before sleeping?"
#     },
#     {
#         "title": "🌙 Just check in",
#         "body": "What’s sitting with you right now?"
#     }
# ]


# def send_night_reflection_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date()
#         index = today.toordinal() % len(NIGHT_PROMPTS)
#         prompt = NIGHT_PROMPTS[index]

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title=prompt["title"],
#                 body=prompt["body"]
#             ),
#             data={
#                 "type": "night_reflection",
#                 "screen": "chat",
#                 "date": today.isoformat()
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Error sending night notification: {e}")
#         return None


# # ============================================================
# # 🎯 STORE USER SELECTED INTENTION
# # ============================================================

# @bp.route("/set_intention", methods=["POST"])
# def set_intention():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         intention = data.get("intention")

#         if not user_id or not intention:
#             return jsonify({"error": "Missing user_id or intention"}), 400

#         today = datetime.now(timezone.utc).date().isoformat()

#         db.collection("users").document(user_id).set(
#             {
#                 "today_intention": intention,
#                 "intention_date": today,
#                 "intention_set_at": datetime.now(timezone.utc),
#             },
#             merge=True
#         )

#         db.collection("users") \
#             .document(user_id) \
#             .collection("mergedMessages") \
#             .add({
#                 "type": "intention",
#                 "message": f"🎯 Today’s intention: {intention}",
#                 "timestamp": datetime.now(timezone.utc),
#                 "from": "system",
#                 "is_notification": False,
#                 "date": today,
#             })

#         return jsonify({"status": "success"})

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to store intention"}), 500


# # ============================================================
# # 🌱 GRATITUDE JOURNAL NOTIFICATION
# # ============================================================

# def send_gratitude_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 A small pause",
#                 body="Is there one thing today that felt quietly supportive or meaningful?"
#             ),
#             data={
#                 "type": "gratitude_journal",
#                 "screen": "chat",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Gratitude notification error: {e}")
#         return None


# # ============================================================
# # 🧩 CBT REFLECTION NOTIFICATION
# # ============================================================

# def send_cbt_reflection_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🧩 Let’s unpack this gently",
#                 body="Something may have stayed with you today. What happened — and what did it bring up for you?"
#             ),
#             data={
#                 "type": "cbt_reflection",
#                 "screen": "chat",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ CBT notification error: {e}")
#         return None



# # ============================================================
# # 🌬️ AWARENESS CHECK-IN NOTIFICATION
# # ============================================================

# def send_awareness_checkin_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌬️ A moment to arrive",
#                 body="Before anything else — how does your body feel right now?"
#             ),
#             data={
#                 "type": "awareness_checkin",
#                 "screen": "chat",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Awareness notification error: {e}")
#         return None

# # ============================================================
# # 👋 OPTIONAL WELCOME NOTIFICATION
# # ============================================================

# def send_welcome_notification(token):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="Welcome to RETVRN",
#                 body="What’s on your mind right now? Write or speak freely."
#             ),
#             token=token,
#         )
#         return messaging.send(message)
#     except Exception as e:
#         print(f"❌ Welcome notification error: {e}")
# # #         return None
# from flask import Blueprint, request, jsonify
# from datetime import datetime, timezone
# import traceback
# from firebase_admin import messaging

# from firebase_utils import db

# bp = Blueprint("notifications", __name__)

# # ============================================================
# # 🌅 MORNING INTENTION NOTIFICATION (❌ NO CHANGE)
# # ============================================================

# def send_morning_intention_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌅 A gentle start to your day",
#                 body="Would you like to set a small intention for today?"
#             ),
#             data={
#                 "type": "morning_intention",
#                 "screen": "intention",
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Error sending morning notification: {e}")
#         return None


# # ============================================================
# # 🌙 NIGHT REFLECTION NOTIFICATION (ROTATING) ✅ FIXED
# # ============================================================

# NIGHT_PROMPTS = [
#     {
#         "title": "🌙 Before you rest",
#         "body": "How did today feel for you — not good or bad, just honestly?"
#     },
#     {
#         "title": "🌙 A quiet moment",
#         "body": "Was there one small moment today that stayed with you?"
#     },
#     {
#         "title": "🌙 End of the day",
#         "body": "Is there anything you’d like to leave behind before sleeping?"
#     },
#     {
#         "title": "🌙 Just check in",
#         "body": "What’s sitting with you right now?"
#     }
# ]


# def send_night_reflection_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date()
#         index = today.toordinal() % len(NIGHT_PROMPTS)
#         prompt = NIGHT_PROMPTS[index]

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title=prompt["title"],
#                 body=prompt["body"]
#             ),
#             data={
#                 "type": "night_reflection",
#                 "screen": "chat",
#                 "body": prompt["body"],   # ✅ IMPORTANT
#                 "date": today.isoformat()
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Error sending night notification: {e}")
#         return None


# # ============================================================
# # 🎯 STORE USER SELECTED INTENTION (NO CHANGE)
# # ============================================================

# @bp.route("/set_intention", methods=["POST"])
# def set_intention():
#     try:
#         data = request.get_json()
#         user_id = data.get("user_id")
#         intention = data.get("intention")

#         if not user_id or not intention:
#             return jsonify({"error": "Missing user_id or intention"}), 400

#         today = datetime.now(timezone.utc).date().isoformat()

#         db.collection("users").document(user_id).set(
#             {
#                 "today_intention": intention,
#                 "intention_date": today,
#                 "intention_set_at": datetime.now(timezone.utc),
#             },
#             merge=True
#         )

#         db.collection("users") \
#             .document(user_id) \
#             .collection("mergedMessages") \
#             .add({
#                 "type": "intention",
#                 "message": f"🎯 Today’s intention: {intention}",
#                 "timestamp": datetime.now(timezone.utc),
#                 "from": "system",
#                 "is_notification": False,
#                 "date": today,
#             })

#         return jsonify({"status": "success"})

#     except Exception:
#         traceback.print_exc()
#         return jsonify({"error": "Failed to store intention"}), 500


# # ============================================================
# # 🌱 GRATITUDE JOURNAL NOTIFICATION ✅ FIXED
# # ============================================================

# def send_gratitude_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()
#         body = "Is there one thing today that felt quietly supportive or meaningful?"

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌱 A small pause",
#                 body=body
#             ),
#             data={
#                 "type": "gratitude_journal",
#                 "screen": "chat",
#                 "body": body,            # ✅ IMPORTANT
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Gratitude notification error: {e}")
#         return None


# # ============================================================
# # 🧩 CBT REFLECTION NOTIFICATION ✅ FIXED
# # ============================================================

# def send_cbt_reflection_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()
#         body = (
#             "Something may have stayed with you today. "
#             "What happened — and what did it bring up for you?"
#         )

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🧩 Let’s unpack this gently",
#                 body=body
#             ),
#             data={
#                 "type": "cbt_reflection",
#                 "screen": "chat",
#                 "body": body,            # ✅ IMPORTANT
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ CBT notification error: {e}")
#         return None


# # ============================================================
# # 🌬️ AWARENESS CHECK-IN NOTIFICATION ✅ FIXED
# # ============================================================

# def send_awareness_checkin_notification(fcm_token: str):
#     try:
#         today = datetime.now(timezone.utc).date().isoformat()
#         body = "Before anything else — how does your body feel right now?"

#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="🌬️ A moment to arrive",
#                 body=body
#             ),
#             data={
#                 "type": "awareness_checkin",
#                 "screen": "chat",
#                 "body": body,            # ✅ IMPORTANT
#                 "date": today
#             },
#             token=fcm_token,
#         )

#         return messaging.send(message)

#     except Exception as e:
#         print(f"❌ Awareness notification error: {e}")
#         return None


# # ============================================================
# # 👋 OPTIONAL WELCOME NOTIFICATION (UNCHANGED)
# # ============================================================

# def send_welcome_notification(token):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#                 title="Welcome to RETVRN",
#                 body="What’s on your mind right now? Write or speak freely."
#             ),
#             token=token,
#         )
#         return messaging.send(message)
#     except Exception as e:
#         print(f"❌ Welcome notification error: {e}")
#         return None
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import traceback
from firebase_admin import messaging
from firebase_utils import db

bp = Blueprint("notifications", __name__)

# ============================================================
# 🔔 COMMON LOGGER
# ============================================================

def log(notification_type: str, message: str):
    print(f"[{datetime.now(timezone.utc)}] [{notification_type}] {message}")


# ============================================================
# 🌅 MORNING INTENTION NOTIFICATION
# ============================================================
# ============================================================
# 🌞 MORNING CHAT MESSAGE (Separate from popup)
# ============================================================

def send_morning_chat_notification(fcm_token: str):
    try:
        log("MORNING_CHAT", "Triggered")
        log("MORNING_CHAT", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date().isoformat()
        body = "🌞 How’s the emotional weather inside this morning?"

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌞 Morning Check-In",
                body=body
            ),
            data={
                "type": "morning_chat",
                "screen": "chat",
                "body": body,
                "date": today
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("MORNING_CHAT", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("MORNING_CHAT ERROR", str(e))
        traceback.print_exc()
        return None

def send_morning_intention_notification(fcm_token: str):
    try:
        log("MORNING", "Triggered")
        log("MORNING", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date().isoformat()

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌅 A gentle start to your day",
                body="Would you like to set a small intention for today?"
            ),
            data={
                "type": "morning_intention",
                "screen": "intention",
                "date": today
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("MORNING", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("MORNING ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 🌙 NIGHT REFLECTION NOTIFICATION (ROTATING)
# ============================================================

NIGHT_PROMPTS = [
    {
        "title": "🌙 Before you rest",
        "body": "How did today feel for you — not good or bad, just honestly?"
    },
    {
        "title": "🌙 A quiet moment",
        "body": "Was there one small moment today that stayed with you?"
    },
    {
        "title": "🌙 End of the day",
        "body": "Is there anything you’d like to leave behind before sleeping?"
    },
    {
        "title": "🌙 Just check in",
        "body": "What’s sitting with you right now?"
    }
]


def send_night_reflection_notification(fcm_token: str):
    try:
        log("NIGHT", "Triggered")
        log("NIGHT", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date()
        index = today.toordinal() % len(NIGHT_PROMPTS)
        prompt = NIGHT_PROMPTS[index]

        message = messaging.Message(
            notification=messaging.Notification(
                title=prompt["title"],
                body=prompt["body"]
            ),
            data={
                "type": "night_reflection",
                "screen": "chat",
                "body": prompt["body"],
                "date": today.isoformat()
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("NIGHT", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("NIGHT ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 🌱 GRATITUDE JOURNAL NOTIFICATION
# ============================================================

def send_gratitude_notification(fcm_token: str):
    try:
        log("GRATITUDE", "Triggered")
        log("GRATITUDE", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date().isoformat()
        body = "Is there one thing today that felt quietly supportive or meaningful?"

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 A small pause",
                body=body
            ),
            data={
                "type": "gratitude_journal",
                "screen": "chat",
                "body": body,
                "date": today
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("GRATITUDE", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("GRATITUDE ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 🧩 CBT REFLECTION NOTIFICATION
# ============================================================

def send_cbt_reflection_notification(fcm_token: str):
    try:
        log("CBT", "Triggered")
        log("CBT", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date().isoformat()
        body = (
            "Something may have stayed with you today. "
            "What happened — and what did it bring up for you?"
        )

        message = messaging.Message(
            notification=messaging.Notification(
                title="🧩 Let’s unpack this gently",
                body=body
            ),
            data={
                "type": "cbt_reflection",
                "screen": "chat",
                "body": body,
                "date": today
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("CBT", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("CBT ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 🌬️ AWARENESS CHECK-IN NOTIFICATION
# ============================================================

def send_awareness_checkin_notification(fcm_token: str):
    try:
        log("AWARENESS", "Triggered")
        log("AWARENESS", f"Token → {fcm_token}")

        today = datetime.now(timezone.utc).date().isoformat()
        body = "Before anything else — how does your body feel right now?"

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌬️ A moment to arrive",
                body=body
            ),
            data={
                "type": "awareness_checkin",
                "screen": "chat",
                "body": body,
                "date": today
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        log("AWARENESS", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("AWARENESS ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 👋 WELCOME NOTIFICATION
# ============================================================

def send_welcome_notification(token):
    try:
        log("WELCOME", "Triggered")
        log("WELCOME", f"Token → {token}")

        message = messaging.Message(
            notification=messaging.Notification(
                title="Welcome to RETVRN",
                body="What’s on your mind right now? Write or speak freely."
            ),
            token=token,
        )

        response = messaging.send(message)
        log("WELCOME", f"Sent successfully → {response}")
        return response

    except Exception as e:
        log("WELCOME ERROR", str(e))
        traceback.print_exc()
        return None


# ============================================================
# 🎯 STORE USER SELECTED INTENTION
# ============================================================

@bp.route("/set_intention", methods=["POST"])
def set_intention():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        intention = data.get("intention")

        if not user_id or not intention:
            return jsonify({"error": "Missing user_id or intention"}), 400

        today = datetime.now(timezone.utc).date().isoformat()

        db.collection("users").document(user_id).set(
            {
                "today_intention": intention,
                "intention_date": today,
                "intention_set_at": datetime.now(timezone.utc),
            },
            merge=True
        )

        log("INTENTION", f"Stored intention for user {user_id}")

        return jsonify({"status": "success"})

    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Failed to store intention"}), 500
