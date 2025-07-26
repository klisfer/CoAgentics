// Firebase configuration and authentication setup
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// Firebase configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
const firebaseConfig = {
  apiKey: "AIzaSyBhPaR5GHB6Eo8aWVFcJVFwnD6VDgYY1os",
  authDomain: "coagentics.firebaseapp.com",
  projectId: "coagentics",
  storageBucket: "coagentics.firebasestorage.app",
  messagingSenderId: "704299757982",
  appId: "1:704299757982:web:10742468fe30d94b88668f",
  measurementId: "G-0XLBK3JTCK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export default app; 