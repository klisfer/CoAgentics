# Firebase Authentication Setup Guide

## Overview
Firebase Authentication has been integrated into the CoAgentics frontend with support for:
- Email/Password authentication
- Google OAuth authentication  
- Protected routes
- User profile management

## Configuration Required

### 1. Update Firebase Config
Edit `src/lib/firebase.ts` and replace the dummy credentials with your actual Firebase project credentials:

```typescript
const firebaseConfig = {
  apiKey: "YOUR_ACTUAL_API_KEY",
  authDomain: "your-actual-project-id.firebaseapp.com", 
  projectId: "your-actual-project-id",
  storageBucket: "your-actual-project-id.appspot.com",
  messagingSenderId: "YOUR_ACTUAL_SENDER_ID",
  appId: "YOUR_ACTUAL_APP_ID"
};
```

### 2. Firebase Console Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Enable Authentication:
   - Go to Authentication > Sign-in method
   - Enable "Email/Password" provider
   - Enable "Google" provider (add your OAuth client details)
4. Get your config from Project Settings > General > Your apps

### 3. Google OAuth Setup
1. In Firebase Console, under Authentication > Sign-in method > Google
2. Add your domain to authorized domains
3. For development: add `localhost` to authorized domains
4. For production: add your production domain

## Authentication Flow

### Protected Routes
- Main dashboard (`/`) is protected and requires authentication
- Users are redirected to `/auth` if not logged in
- Authenticated users visiting `/auth` are redirected to dashboard

### User Management  
- User profile displays in sidebar with name/email
- Logout functionality available in sidebar
- Authentication state managed via React Context

## Usage

### Login/Signup
- Visit `/auth` for login/signup page
- Switch between Login/Signup tabs
- Support for email/password and Google OAuth

### Testing (Current State)
- Currently using dummy Firebase config
- Authentication will fail until real credentials are added
- All UI components are ready and functional

## File Structure
```
src/
├── lib/firebase.ts              # Firebase configuration
├── contexts/AuthContext.tsx    # Authentication state management
├── components/auth/
│   ├── ProtectedRoute.tsx      # Route protection
│   └── AuthRedirect.tsx        # Redirect authenticated users
├── app/
│   ├── auth/page.tsx           # Login/Signup page
│   ├── layout.tsx              # Root layout with AuthProvider
│   └── page.tsx                # Protected main dashboard
└── components/layout/
    └── Sidebar.tsx             # Updated with user profile
```

## Next Steps
1. Replace dummy Firebase config with real credentials
2. Test authentication flow
3. Verify Google OAuth setup
4. Add any additional authentication providers if needed 