import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.

    It looks for the service account key file in the parent directory
    and uses it to authenticate. It also ensures that the app is not
    initialized more than once.
    """
    # Check if the app is already initialized
    if not firebase_admin._apps:
        try:
            # Path to the service account key file
            # Assumes this script is in backend/services and the key is in backend/
            key_path = os.path.join(os.path.dirname(__file__), '..', 'serviceAccountKey.json')

            cred = credentials.Certificate(key_path)
            
            # Initialize the app with your project's details
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://your-project-id.firebaseio.com'
            })
            print("Firebase initialized successfully.")
        except FileNotFoundError:
            print("Error: serviceAccountKey.json not found. Make sure it's in the 'backend' directory.")
        except Exception as e:
            print(f"An error occurred during Firebase initialization: {e}")

def get_firestore_client():
    """
    Returns a Firestore client instance.

    Initializes Firebase if it hasn't been already.
    """
    initialize_firebase()
    return firestore.client()

def verify_id_token(token: str) -> dict:
    """
    Verifies the Firebase ID token.

    Args:
        token: The ID token to verify.

    Returns:
        A dictionary containing the decoded user data, or None if verification fails.
    """
    try:
        # Make sure Firebase is initialized
        initialize_firebase()
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        # In a real app, you'd want to log this error
        print(f"Error verifying Firebase ID token: {e}")
        return None

# Example of how to use the client:
# db = get_firestore_client()
# doc_ref = db.collection(u'users').document(u'alovelace')
# doc_ref.set({
#     u'first': u'Ada',
#     u'last': u'Lovelace',
#     u'born': 1815
# }) 