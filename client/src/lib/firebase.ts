// Firebase configuration and authentication setup
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
const firebaseConfig = {
  apiKey: "AIzaSyA1Ea-w28Q_tjAiAZUC2eBTTq4K9YxApJo",
  authDomain: "wealthflow-ai.firebaseapp.com",
  projectId: "wealthflow-ai",
  storageBucket: "wealthflow-ai.firebasestorage.app",
  messagingSenderId: "978710537953",
  appId: "1:978710537953:web:5ba86d938be5301b98b9a0"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Initialize Firestore
export const db = getFirestore(app);

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export default app; 