# from flask import Flask
# from flask_cors import CORS
# from routes import bp  # Import your routes blueprint from routes.py

# def create_app():
#     """
#     Application factory function to create and configure the Flask app.
#     """
#     app = Flask(__name__)

#     # Enable CORS for cross-origin requests
#     CORS(app)

#     # Register blueprints (routes)
#     app.register_blueprint(bp)

#     # Start any schedulers or background jobs (e.g., daily notifications)
#     from scheduling import schedule_daily_notifications
#     schedule_daily_notifications()

# #     return app
# from flask import Flask
# from flask_cors import CORS
# from routes import bp  # Import the routes blueprint from routes.py

# def create_app():
#     """
#     Application factory function to create and configure the Flask app.
#     """
#     app = Flask(__name__)  # Use __name__, not _name_
#     app.config.from_object("config")  # Load config from config.py

#     # Enable CORS to allow cross-origin requests
#     CORS(app)

#     # Register the routes blueprint
#     app.register_blueprint(bp)

#     # Start scheduling any background tasks like daily notifications
#     from scheduling import schedule_daily_notifications
#     schedule_daily_notifications()

#     return app
from flask import Flask
from flask_cors import CORS
from routes import bp  # Import the routes blueprint from routes.py
import logging

def create_app():
    """
    Application factory function to create and configure the Flask app.
    Safe scheduler import: will not crash app if scheduler is missing.
    """
    app = Flask(__name__)
    app.config.from_object("config")

    CORS(app)
    app.register_blueprint(bp)

    # Try to import and start the scheduler. If the exact name changed,
    # attempt the likely alternatives and never let scheduler import kill the app.
    start_scheduler = None
    try:
        # preferred: new function name (adjust if your scheduling.py uses a different name)
        from scheduling import schedule_intention_notifications
        start_scheduler = schedule_intention_notifications
    except Exception:
        # try the older name for backwards compatibility
        try:
            from scheduling import schedule_daily_notifications
            start_scheduler = schedule_daily_notifications
        except Exception:
            logging.exception("No scheduler function found in scheduling.py — continuing without scheduler")

    # Start the scheduler if we found one (guarded call)
    if start_scheduler:
        try:
            start_scheduler()
        except Exception:
            logging.exception("Scheduler failed to start — continuing without scheduler")

    return app
