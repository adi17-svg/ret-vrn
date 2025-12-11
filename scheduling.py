
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from config import NOTIFICATION_TIME
# from notifications import send_all_daily_tasks  # Import function from notifications.py

# scheduler = BackgroundScheduler(daemon=True)
# JOB_ID = "daily_task_notification"

# def schedule_daily_notifications():
#     try:
#         # Remove previous job if it exists to avoid duplication
#         try:
#             scheduler.remove_job(JOB_ID)
#         except Exception:
#             pass  # No existing job to remove

#         hour, minute = map(int, NOTIFICATION_TIME.split(':'))
#         trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

#         scheduler.add_job(
#             func=send_all_daily_tasks,
#             trigger=trigger,
#             id=JOB_ID,
#             replace_existing=True,
#             misfire_grace_time=60*60  # 1 hour grace period
#         )

#         if not scheduler.running:
#             scheduler.start()
#             print(f"⏰ Scheduled daily notifications at {NOTIFICATION_TIME} UTC")

#     except Exception as e:
#         print(f"⚠ Error scheduling notifications: {e}")

#     return scheduler

# scheduling.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import NOTIFICATION_TIME_MORNING, NOTIFICATION_TIME_NIGHT  # add these to config or fallback below
from notifications import send_morning_intention_prompt, send_night_reflection_prompt
from firebase_utils import db

scheduler = BackgroundScheduler(daemon=True)

JOB_ID_MORNING = "morning_intention_notification"
JOB_ID_NIGHT = "night_reflection_notification"


def _morning_broadcast():
    """Iterate users and send morning intention prompt (writes mergedMessages and FCM if token present)."""
    try:
        users_ref = db.collection("users")
        for u in users_ref.stream():
            user_id = u.id
            token = u.to_dict().get("fcm_token") or u.to_dict().get("fcmToken") or None
            try:
                send_morning_intention_prompt(user_id, fcm_token=token)
            except Exception as e:
                # don't stop the loop on single-user errors
                print(f"[scheduling] morning send failed for {user_id}: {e}")
    except Exception as e:
        print("[scheduling] morning broadcast error:", e)


def _night_broadcast():
    """Iterate users and send night reflection prompt."""
    try:
        users_ref = db.collection("users")
        for u in users_ref.stream():
            user_id = u.id
            token = u.to_dict().get("fcm_token") or u.to_dict().get("fcmToken") or None
            try:
                send_night_reflection_prompt(user_id, fcm_token=token)
            except Exception as e:
                print(f"[scheduling] night send failed for {user_id}: {e}")
    except Exception as e:
        print("[scheduling] night broadcast error:", e)


def schedule_intention_notifications(morning_time: str = None, night_time: str = None):
    """
    Schedule two jobs:
      - morning_time (HH:MM) -> morning intention prompt
      - night_time (HH:MM)   -> night reflection prompt

    If config values NOTIFICATION_TIME_MORNING / NOTIFICATION_TIME_NIGHT exist, they are used.
    """
    try:
        # choose times: explicit args > config > defaults
        morning_time = morning_time or getattr(__import__("config", fromlist=["*"]), "NOTIFICATION_TIME_MORNING", None) or NOTIFICATION_TIME_MORNING
        night_time = night_time or getattr(__import__("config", fromlist=["*"]), "NOTIFICATION_TIME_NIGHT", None) or NOTIFICATION_TIME_NIGHT

        # Remove existing jobs if present
        try:
            scheduler.remove_job(JOB_ID_MORNING)
        except Exception:
            pass
        try:
            scheduler.remove_job(JOB_ID_NIGHT)
        except Exception:
            pass

        # Parse HH:MM
        mh, mm = map(int, (morning_time or "07:00").split(":"))
        nh, nm = map(int, (night_time or "21:00").split(":"))

        mor_trigger = CronTrigger(hour=mh, minute=mm, timezone="UTC")
        night_trigger = CronTrigger(hour=nh, minute=nm, timezone="UTC")

        scheduler.add_job(_morning_broadcast, mor_trigger, id=JOB_ID_MORNING, replace_existing=True, misfire_grace_time=60*60)
        scheduler.add_job(_night_broadcast, night_trigger, id=JOB_ID_NIGHT, replace_existing=True, misfire_grace_time=60*60)

        if not scheduler.running:
            scheduler.start()
            print(f"⏰ Scheduled intention notifications: morning {mh:02d}:{mm:02d} UTC, night {nh:02d}:{nm:02d} UTC")

    except Exception as e:
        print("⚠ Error scheduling intention notifications:", e)

    return scheduler


# ---- If this module is imported and you want auto-scheduling on import, call schedule_intention_notifications() from app startup instead.
