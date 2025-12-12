
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