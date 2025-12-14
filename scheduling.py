
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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from firebase_utils import db
from notifications import send_morning_intention_notification

scheduler = BackgroundScheduler(daemon=True)
JOB_ID = "morning_intention_notification"


def schedule_morning_intention():
    """
    Schedules ONLY the morning intention notification.
    """

    try:
        # Remove old job if exists
        try:
            scheduler.remove_job(JOB_ID)
        except Exception:
            pass

        # ⏰ Morning time (UTC)
        trigger = CronTrigger(hour=7, minute=30, timezone="UTC")

        def notify_all_users():
            users_ref = db.collection("users").stream()

            for user_doc in users_ref:
                user_data = user_doc.to_dict()
                fcm_token = user_data.get("fcm_token")

                if not fcm_token:
                    continue

                send_morning_intention_notification(fcm_token)

        scheduler.add_job(
            func=notify_all_users,
            trigger=trigger,
            id=JOB_ID,
            replace_existing=True,
            misfire_grace_time=60 * 60
        )

        if not scheduler.running:
            scheduler.start()

        print("🌅 Morning intention scheduler started")

    except Exception as e:
        print(f"⚠ Error scheduling morning intention: {e}")

    return scheduler
