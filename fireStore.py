import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Specify the path to your downloaded service account key file
cred = credentials.Certificate('path/to/your/serviceAccountKey.json')

# Initialize the app
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()
print("Connected to Firestore using service account key.")
