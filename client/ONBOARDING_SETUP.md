# User Onboarding Flow with Firebase Firestore

This document explains the user onboarding flow implementation for the CoAgentics financial planning application.

## Overview

The onboarding flow collects comprehensive user information to personalize the financial planning experience. Users are automatically redirected to complete their profile after authentication if they haven't done so already.

## Features

### 1. Firestore Integration
- **User profiles stored in Firestore**: All user data is stored in the `users` collection
- **Real-time profile checking**: The app checks if users need onboarding on every authentication state change
- **Unique user records**: Each user has a unique document identified by their Firebase Auth UID

### 2. Multi-Step Form
The onboarding form is broken into 5 logical steps:

1. **Personal Information**
   - Full Name (required)
   - Age (required, 18-100)
   - Gender (optional)
   - Marital Status

2. **Employment Details**
   - Employment Status (salaried, self-employed, unemployed)
   - Industry Type (conditional - only for salaried employees)

3. **Family & Dependents**
   - Dependents checkboxes (wife, parents, kids)
   - Number of kids (conditional - only if kids is selected)

4. **Location**
   - State (required - dropdown with Indian states)
   - City (required - text input)

5. **Insurance**
   - Insurance types (life, health) - optional checkboxes

### 3. Form Validation
- **Step-by-step validation**: Each step is validated before proceeding
- **Conditional field validation**: Fields that depend on other selections are validated appropriately
- **Real-time error display**: Errors are shown immediately with clear messaging

### 4. User Experience
- **Progress indicator**: Visual progress bar and step indicators
- **Responsive design**: Works on all device sizes
- **Loading states**: Clear feedback during form submission
- **Navigation**: Previous/Next buttons with appropriate disabled states

## Technical Implementation

### Files Structure
```
client/src/
├── lib/
│   ├── firebase.ts          # Firebase configuration with Firestore
│   └── firestore.ts         # Firestore service and user profile interface
├── components/
│   ├── onboarding/
│   │   └── OnboardingForm.tsx # Main onboarding form component
│   └── auth/
│       ├── ProtectedRoute.tsx  # Updated to check onboarding status
│       └── AuthRedirect.tsx    # Updated to handle onboarding redirect
├── contexts/
│   └── AuthContext.tsx      # Updated with onboarding status checking
└── app/
    └── onboarding/
        └── page.tsx         # Onboarding page route
```

### Data Model
```typescript
interface UserProfile {
  uid: string;
  email: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer-not-to-say';
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed';
  employmentStatus: 'salaried' | 'self-employed' | 'unemployed';
  industryType?: string;
  dependents: {
    wife: boolean;
    parents: boolean;
    kids: boolean;
  };
  kidsCount?: number;
  location: {
    state: string;
    city: string;
  };
  insurance: {
    life: boolean;
    health: boolean;
  };
  profileCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

## Flow Logic

### 1. Authentication State Changes
- When a user signs in, `AuthContext` checks if they have a complete profile
- If no profile exists or `profileCompleted` is false, `needsOnboarding` is set to true

### 2. Route Protection
- `ProtectedRoute` checks both authentication and onboarding status
- Unauthenticated users → redirected to `/auth`
- Authenticated but incomplete profile → redirected to `/onboarding`
- Complete profile → access granted to protected routes

### 3. Form Submission
- Form data is validated step-by-step
- On final submission, data is saved to Firestore with `profileCompleted: true`
- AuthContext is refreshed to update onboarding status
- User is redirected to the main dashboard

### 4. Prevention of Skipping
- Direct navigation to protected routes automatically redirects to onboarding
- Auth pages redirect users to onboarding if they're authenticated but incomplete
- No way to bypass the onboarding flow

## Firebase Setup Requirements

### 1. Firestore Database
Create a Firestore database with the following security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 2. Firebase Configuration
Update `client/src/lib/firebase.ts` with your actual Firebase project credentials.

## Usage

1. **User signs up/logs in** → Firebase Auth
2. **AuthContext checks profile** → Firestore query
3. **If incomplete** → Redirect to `/onboarding`
4. **User completes form** → Data saved to Firestore
5. **Profile marked complete** → Access granted to main app

## Customization

### Adding Form Fields
1. Update `UserProfile` interface in `firestore.ts`
2. Add field to `FormData` interface in `OnboardingForm.tsx`
3. Add field to appropriate form step
4. Update validation logic if needed

### Modifying Form Steps
1. Update `STEPS` array in `OnboardingForm.tsx`
2. Add new case in `renderStep()` function
3. Add validation logic in `validateStep()`

### Styling
The form uses Tailwind CSS with a modern, gradient design. All styles can be customized by modifying the class names in `OnboardingForm.tsx`.

## Security Considerations

- **User data isolation**: Firestore rules ensure users can only access their own data
- **Authentication required**: All operations require valid Firebase Auth token
- **Input validation**: Both client-side and (should have) server-side validation
- **Profile completion tracking**: Prevents bypassing onboarding 