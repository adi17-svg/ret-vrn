# from datetime import datetime, timezone
# from firebase_admin import messaging
# import hashlib
# from tasks import generate_daily_task

# def send_daily_task_notification(fcm_token: str, task_text: str) -> str:
#     """
#     Send a single daily task notification via Firebase Cloud Messaging (FCM).
    
#     Args:
#         fcm_token (str): The device FCM token.
#         task_text (str): The notification body text.

#     Returns:
#         str: The Firebase message ID if sent successfully.
#     """
#     today = datetime.now(timezone.utc).date().isoformat()
#     notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()

#     message = messaging.Message(
#         notification=messaging.Notification(
#             title="🌱 Your Daily Spiral Task",
#             body=task_text
#         ),
#         data={
#             "type": "daily_task",
#             "task": task_text,
#             "screen": "chat",
#             "notification_id": notification_id
#         },
#         token=fcm_token,
#         android=messaging.AndroidConfig(
#             collapse_key=notification_id
#         ),
#         apns=messaging.APNSConfig(
#             headers={
#                 "apns-collapse-id": notification_id
#             }
#         )
#     )

#     response = messaging.send(message)
#     return response  # Message ID string

# def send_all_daily_notifications():
#     """
#     Example function to send daily task notifications to all users.
#     You must implement custom logic to retrieve user tokens and handle errors.
#     """
#     # Example: get daily task
#     daily_task = generate_daily_task()

#     # Example: fetch users and FCM tokens from Firestore or database here
#     # This is placeholder logic and must be implemented to fit your data source
#     try:
#         users_ref = None  # Replace with your Firestore users collection ref
#         users = []       # Replace with actual fetch of user list with fcm_token attribute

#         # For example, if using Firestore:
#         # users_ref = db.collection("users")
#         # users_docs = users_ref.stream()
#         # users = [{"fcm_token": doc.get("fcm_token")} for doc in users_docs]

#         for user in users:
#             fcm_token = user.get("fcm_token")
#             if fcm_token:
#                 try:
#                     send_daily_task_notification(fcm_token, daily_task["task"])
#                 except Exception as e:
#                     print(f"Failed to send notification to user {user}: {e}")
#     except Exception as main_e:
# #         print(f"Error in sending all daily notifications: {main_e}")
# from datetime import datetime, timezone
# from firebase_admin import messaging
# import hashlib
# from tasks import generate_daily_task
# from firebase_utils import db  # Assuming you have Firebase Firestore client here

# def send_daily_task_notification(fcm_token: str, task_text: str) -> str:
#     """
#     Send a single daily task notification via Firebase Cloud Messaging (FCM).
    
#     Args:
#         fcm_token (str): The device FCM token.
#         task_text (str): The notification body text.

#     Returns:
#         str: The Firebase message ID if sent successfully.
#     """
#     today = datetime.now(timezone.utc).date().isoformat()
#     notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()

#     message = messaging.Message(
#         notification=messaging.Notification(
#             title="🌱 Your Daily Spiral Task",
#             body=task_text
#         ),
#         data={
#             "type": "daily_task",
#             "task": task_text,
#             "screen": "chat",
#             "notification_id": notification_id
#         },
#         token=fcm_token,
#         android=messaging.AndroidConfig(
#             collapse_key=notification_id
#         ),
#         apns=messaging.APNSConfig(
#             headers={
#                 "apns-collapse-id": notification_id
#             }
#         )
#     )

#     response = messaging.send(message)
#     return response  # Message ID string

# def send_all_daily_notifications():
#     """
#     Example function to send daily task notifications to all users.
#     Replace placeholder code to fetch users with your actual Firestore or database logic.
#     """
#     daily_task = generate_daily_task()

#     try:
#         users_ref = db.collection("users")
#         users = []
#         for doc in users_ref.stream():
#             data = doc.to_dict()
#             fcm_token = data.get("fcmToken")  # Correct field name
#             if not fcm_token:
#                 print(f"Warning: User document {doc.id} missing 'fcmToken'. Skipping.")
#                 continue
#             users.append({"fcm_token": fcm_token})

#         for user in users:
#             try:
#                 send_daily_task_notification(user["fcm_token"], daily_task["task"])
#                 print(f"Notification sent to token: {user['fcm_token']}")
#             except Exception as e:
#                 print(f"Failed to send notification to token {user['fcm_token']}: {e}")
#     except Exception as main_e:
#         print(f"Error in sending all daily notifications: {main_e}")
# from datetime import datetime, timezone
# from firebase_admin import messaging
# import hashlib
# from tasks import generate_daily_task  # Adjust import path as needed
# from firebase_utils import db  # Your Firestore client instance

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
#             android=messaging.AndroidConfig(
#                 collapse_key=notification_id
#             ),
#             apns=messaging.APNSConfig(
#                 headers={
#                     "apns-collapse-id": notification_id
#                 }
#             )
#         )

#         response = messaging.send(message)
#         return response
#     except Exception as e:
#         print(f"Error sending notification: {e}")
#         return None

# def has_received_today(user_id):
#     today = datetime.now(timezone.utc).date().isoformat()
#     messages_ref = db.collection("users").document(user_id).collection("mergedMessages")

#     query = messages_ref.where("is_notification", "==", True) \
#                         .where("date", "==", today) \
#                         .limit(1)

#     docs = query.stream()
#     return any(True for _ in docs)

# def send_all_daily_tasks():
#     try:
#         task_data = generate_daily_task()
#         task_text = task_data["task"]
#         today = datetime.now(timezone.utc).date().isoformat()

#         # Send a topic message (optional)
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

#         # Log notification message for each user (if not already received today)
#         users_ref = db.collection("users")
#         batch = db.batch()
#         for user_doc in users_ref.stream():
#             user_id = user_doc.id
#             if has_received_today(user_id):
#                 continue

#             notification_ref = db.collection("users").document(user_id) \
#                                 .collection("mergedMessages").document()

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

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import traceback
import hashlib
from firebase_admin import messaging
from firebase_utils import db  # Your Firestore client instance
from tasks import generate_daily_task  # Adjust path as needed

bp = Blueprint('notifications', __name__)

# You need to define and manage these globally or in app context appropriately
NOTIFICATION_TIME = "19:30"  # example initial notification time placeholder
scheduler = None  # reference to your APScheduler instance
def schedule_notifications():
    # Implement your scheduler job registration here
    pass

@bp.route('/set_notification_time', methods=['POST'])
def set_notification_time():
    global NOTIFICATION_TIME
    try:
        data = request.get_json()
        new_time = data.get('time')
        # Validate time format HH:MM
        try:
            hour, minute = map(int, new_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except Exception:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400

        NOTIFICATION_TIME = new_time
        if scheduler:
            try:
                scheduler.remove_job("daily_task")
            except Exception:
                pass
            schedule_notifications()
        return jsonify({'status': 'success', 'new_time': NOTIFICATION_TIME})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send_welcome', methods=['POST'])
def send_welcome():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        fcm_token = data.get('fcm_token')
        if not user_id or not fcm_token:
            return jsonify({'error': 'Missing user_id or fcm_token'}), 400

        response = send_welcome_notification(fcm_token)

        db.collection('users').document(user_id).collection('mergedMessages').add({
            'type': 'welcome',
            'message': 'What’s on your mind right now? Write or speak freely—no filters.',
            'timestamp': datetime.now(timezone.utc),
            'from': 'system',
            'is_notification': True
        })

        return jsonify({'status': 'success', 'message': 'Welcome notification sent'})
    except Exception:
        traceback.print_exc()
        return jsonify({'error': 'Failed to send welcome notification'}), 500

def send_welcome_notification(token):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title='Welcome to Spiral Dynamics',
                body='What’s on your mind right now? Write or speak freely—no filters.'
            ),
            token=token,
        )
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f'Error sending welcome notification: {e}')
        return None

def send_daily_task_notification(fcm_token, task_text):
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        notification_id = hashlib.md5(f"{today}_{task_text}".encode()).hexdigest()

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 Your Daily Spiral Task",
                body=task_text
            ),
            data={
                "type": "daily_task",
                "task": task_text,
                "screen": "chat",
                "notification_id": notification_id
            },
            token=fcm_token,
            android=messaging.AndroidConfig(collapse_key=notification_id),
            apns=messaging.APNSConfig(headers={"apns-collapse-id": notification_id})
        )

        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Error sending notification: {e}")
        return None

def has_received_today(user_id):
    today = datetime.now(timezone.utc).date().isoformat()
    messages_ref = db.collection('users').document(user_id).collection('mergedMessages')
    query = messages_ref.where('is_notification', '==', True).where('date', '==', today).limit(1)
    docs = query.stream()
    return any(True for _ in docs)

def send_daily_task_to_all():
    try:
        task_data = generate_daily_task()
        task_text = task_data['task']
        today = datetime.now(timezone.utc).date().isoformat()

        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 Your Daily Spiral Task",
                body=task_text
            ),
            data={
                "type": "daily_task",
                "task": task_text,
                "screen": "chat"
            },
            topic="daily_task"
        )
        response = messaging.send(message)
        print(f"✅ Topic notification sent: {response}")

        users_ref = db.collection('users')
        batch = db.batch()
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            if has_received_today(user_id):
                continue
            notification_ref = db.collection('users').document(user_id).collection('mergedMessages').document()
            batch.set(notification_ref, {
                'type': 'daily_task',
                'message': task_text,
                'timestamp': datetime.now(timezone.utc),
                'from': 'system',
                'is_notification': True,
                'date': today
            })
        batch.commit()
    except Exception as e:
        print(f"Error in sending daily task notifications: {e}")

def send_all_daily_tasks():
    try:
        # Generate or fetch today's shared task
        task_data = generate_daily_task()
        task_text = task_data["task"]
        today = datetime.now(timezone.utc).date().isoformat()

        # ✅ Send one message to the topic
        message = messaging.Message(
            notification=messaging.Notification(
                title="🌱 Your Daily Spiral Task",
                body=task_text
            ),
            data={
                "type": "daily_task",
                "task": task_text,
                "screen": "chat"
            },
            topic="daily_task"
        )

        response = messaging.send(message)
        print(f"✅ Topic notification sent: {response}")

        # ✅ Log one bot-message per user in Firestore
        users_ref = db.collection("users")
        batch = db.batch()
        for user_doc in users_ref.stream():
            user_id = user_doc.id
            if has_received_today(user_id):
                continue
            notification_ref = db.collection("users").document(user_id)\
                .collection("mergedMessages").document()
            batch.set(notification_ref, {
                "type": "daily_task",
                "message": task_text,
                "timestamp": datetime.now(timezone.utc),
                "from": "system",
                "is_notification": True,
                "date": today
            })
        batch.commit()

    except Exception as e:
        print(f"Error in send_all_daily_tasks: {e}")