# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from config import NOTIFICATION_TIME
# from notifications import send_all_daily_notifications  # Your custom function to send notifications
# import logging


# def send_all_daily_tasks():
#     """
#     Job function that runs daily at the scheduled time, triggers sending notifications to users.
#     This function should implement the logic to fetch tasks and send notifications using Firebase or other services.
#     """
#     try:
#         # Example: Call your notifications module function here that sends daily task notifications
#         send_all_daily_notifications()
#         logging.info("Daily task notifications sent successfully.")
#     except Exception as e:
#         logging.error(f"Failed to send daily task notifications: {e}")


# def schedule_daily_notifications():
#     """
#     Setup APScheduler to schedule the daily notification job according to NOTIFICATION_TIME configured.
#     """
#     scheduler = BackgroundScheduler(daemon=True)

#     # Parse hour and minute from NOTIFICATION_TIME - assuming 'HH:MM' format, UTC timezone
#     hour, minute = map(int, NOTIFICATION_TIME.split(':'))
#     trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

#     scheduler.add_job(
#         func=send_all_daily_tasks,
#         trigger=trigger,
#         name="daily_task_notification",
#         misfire_grace_time=60 * 60  # 1 hour grace period to run missed jobs
#     )

#     scheduler.start()
#     logging.info(f"Scheduled daily notifications at {NOTIFICATION_TIME} UTC")

# #     return scheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from config import NOTIFICATION_TIME
# from notifications import send_all_daily_notifications  # Your custom function to send notifications

# def send_all_daily_tasks():
#     """
#     Job function that runs daily at the scheduled time,
#     triggers sending notifications to users.
#     """
#     try:
#         send_all_daily_notifications()
#         print("Daily task notifications sent successfully.")
#     except Exception as e:
#         print(f"Failed to send daily task notifications: {e}")

# def schedule_daily_notifications():
#     """
#     Setup APScheduler to schedule the daily notification job
#     according to NOTIFICATION_TIME configured.
#     """
#     scheduler = BackgroundScheduler(daemon=True)

#     # Parse hour and minute from NOTIFICATION_TIME (expected format HH:MM)
#     hour, minute = map(int, NOTIFICATION_TIME.split(':'))
#     trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

#     scheduler.add_job(
#         func=send_all_daily_tasks,
#         trigger=trigger,
#         name="daily_task_notification",
#         misfire_grace_time=60 * 60  # 1 hour grace period
#     )

#     scheduler.start()
#     print(f"Scheduled daily notifications at {NOTIFICATION_TIME} UTC")

#     return scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import NOTIFICATION_TIME
from notifications import send_all_daily_tasks  # Import function from notifications.py

scheduler = BackgroundScheduler(daemon=True)
JOB_ID = "daily_task_notification"

def schedule_daily_notifications():
    try:
        # Remove previous job if it exists to avoid duplication
        try:
            scheduler.remove_job(JOB_ID)
        except Exception:
            pass  # No existing job to remove

        hour, minute = map(int, NOTIFICATION_TIME.split(':'))
        trigger = CronTrigger(hour=hour, minute=minute, timezone="UTC")

        scheduler.add_job(
            func=send_all_daily_tasks,
            trigger=trigger,
            id=JOB_ID,
            replace_existing=True,
            misfire_grace_time=60*60  # 1 hour grace period
        )

        if not scheduler.running:
            scheduler.start()
            print(f"⏰ Scheduled daily notifications at {NOTIFICATION_TIME} UTC")

    except Exception as e:
        print(f"⚠ Error scheduling notifications: {e}")

    return scheduler