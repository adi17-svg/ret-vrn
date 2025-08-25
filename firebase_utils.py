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