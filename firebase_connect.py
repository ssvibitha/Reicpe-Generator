import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key
cred = credentials.Certificate("firebase/serviceAccountKey.json")

# Initialize app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore DB
db = firestore.client()
