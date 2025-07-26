import { 
  doc, 
  getDoc, 
  setDoc, 
  updateDoc, 
  collection, 
  query, 
  where, 
  getDocs 
} from 'firebase/firestore';
import { db } from './firebase';

// User profile interface
export interface UserProfile {
  uid: string;
  email: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer-not-to-say';
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed';
  employmentStatus: 'salaried' | 'self-employed' | 'unemployed';
  industryType?: string; // Only for salaried employees
  dependents: {
    wife: boolean;
    parents: boolean;
    kids: boolean;
  };
  kidsCount?: number; // Only if kids is true
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

const USERS_COLLECTION = 'users';

export class FirestoreService {
  // Check if user profile exists
  static async getUserProfile(uid: string): Promise<UserProfile | null> {
    try {
      const userDoc = doc(db, USERS_COLLECTION, uid);
      const docSnap = await getDoc(userDoc);
      
      if (docSnap.exists()) {
        const data = docSnap.data();
        return {
          ...data,
          createdAt: data.createdAt?.toDate() || new Date(),
          updatedAt: data.updatedAt?.toDate() || new Date(),
        } as UserProfile;
      }
      return null;
    } catch (error) {
      console.error('Error getting user profile:', error);
      throw error;
    }
  }

  // Create new user profile
  static async createUserProfile(profile: Omit<UserProfile, 'createdAt' | 'updatedAt'>): Promise<void> {
    try {
      const userDoc = doc(db, USERS_COLLECTION, profile.uid);
      const now = new Date();
      
      await setDoc(userDoc, {
        ...profile,
        createdAt: now,
        updatedAt: now,
      });
    } catch (error) {
      console.error('Error creating user profile:', error);
      throw error;
    }
  }

  // Update existing user profile
  static async updateUserProfile(uid: string, updates: Partial<UserProfile>): Promise<void> {
    try {
      const userDoc = doc(db, USERS_COLLECTION, uid);
      await updateDoc(userDoc, {
        ...updates,
        updatedAt: new Date(),
      });
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  }

  // Check if user needs onboarding (profile not completed)
  static async needsOnboarding(uid: string): Promise<boolean> {
    try {
      const profile = await this.getUserProfile(uid);
      return !profile || !profile.profileCompleted;
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      return true; // Default to showing onboarding if there's an error
    }
  }

  // Mark profile as completed
  static async completeProfile(uid: string): Promise<void> {
    try {
      await this.updateUserProfile(uid, { 
        profileCompleted: true,
        updatedAt: new Date() 
      });
    } catch (error) {
      console.error('Error completing profile:', error);
      throw error;
    }
  }
}

// Industry types for the form
export const INDUSTRY_TYPES = [
  'Technology',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Real Estate',
  'Consulting',
  'Media & Entertainment',
  'Government',
  'Non-profit',
  'Other'
];

// Indian states for location
export const INDIAN_STATES = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Delhi',
  'Chandigarh',
  'Puducherry'
]; 