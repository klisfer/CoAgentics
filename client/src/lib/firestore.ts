import { 
  doc, 
  getDoc, 
  setDoc, 
  updateDoc, 
  collection, 
  query, 
  where, 
  getDocs,
  orderBy,
  deleteDoc
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
  monthlyIncome: number;
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
  insuranceCoverage: {
    healthClaimLimit: number;
    lifeClaimLimit: number;
  };
  profileCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  agent?: string;
  metadata?: any;
}

export interface ChatHistory {
  id: string; // Document ID (session_id)
  user_id: string;
  session_id: string;
  chat_data: ChatMessage[];
  title?: string; // Optional title for the conversation
  createdAt: Date;
  updatedAt: Date;
}

const USERS_COLLECTION = 'users';
const CHAT_HISTORY_COLLECTION = 'chat-history';

// Helper function to remove undefined values from objects
function removeUndefinedValues(obj: any): any {
  const cleaned: any = {};
  for (const [key, value] of Object.entries(obj)) {
    if (value !== undefined) {
      cleaned[key] = value;
    }
  }
  return cleaned;
}

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
      
      // Remove any undefined values before saving to Firestore
      const cleanedProfile = removeUndefinedValues({
        ...profile,
        createdAt: now,
        updatedAt: now,
      });
      
      await setDoc(userDoc, cleanedProfile);
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

  // Chat History Methods
  
  // Save chat session to Firestore
  static async saveChatHistory(userId: string, sessionId: string, messages: ChatMessage[], title?: string): Promise<void> {
    try {
      const chatDoc = doc(db, CHAT_HISTORY_COLLECTION, sessionId);
      const now = new Date();
      
      // Check if this session already exists
      const existingDoc = await getDoc(chatDoc);
      const isNewSession = !existingDoc.exists();
      
      console.log(`💾 Saving chat history:`, {
        userId,
        sessionId,
        title,
        messageCount: messages.length,
        isNewSession,
        documentPath: `${CHAT_HISTORY_COLLECTION}/${sessionId}`
      });
      
      const chatHistory: Omit<ChatHistory, 'id'> = {
        user_id: userId,
        session_id: sessionId,
        chat_data: messages,
        title: title || `Chat ${new Date().toLocaleDateString()}`,
        createdAt: isNewSession ? now : (existingDoc.data()?.createdAt?.toDate() || now),
        updatedAt: now,
      };

      await setDoc(chatDoc, removeUndefinedValues(chatHistory));
      console.log(`✅ Chat history ${isNewSession ? 'created' : 'updated'} for session: ${sessionId}`);
      
      // Verify the save by checking total documents for this user
      const userQuery = query(
        collection(db, CHAT_HISTORY_COLLECTION),
        where('user_id', '==', userId)
      );
      const userDocs = await getDocs(userQuery);
      console.log(`📊 Total chat sessions for user ${userId}: ${userDocs.size}`);
      
    } catch (error) {
      console.error('❌ Error saving chat history:', error);
      throw error;
    }
  }

  // Update existing chat session
  static async updateChatHistory(sessionId: string, messages: ChatMessage[]): Promise<void> {
    try {
      const chatDoc = doc(db, CHAT_HISTORY_COLLECTION, sessionId);
      const updateData = removeUndefinedValues({
        chat_data: messages,
        updatedAt: new Date(),
      });
      await updateDoc(chatDoc, updateData);
      console.log(`Chat history updated for session: ${sessionId}`);
    } catch (error) {
      console.error('Error updating chat history:', error);
      throw error;
    }
  }

  // Get all chat sessions for a user
  static async getUserChatHistory(userId: string): Promise<ChatHistory[]> {
    try {
      console.log('🔍 Fetching chat history for user:', userId);
      
      // Query to get ALL chat sessions for the user (explicitly no limit)
      const chatQuery = query(
        collection(db, CHAT_HISTORY_COLLECTION),
        where('user_id', '==', userId)
      );
      
      const querySnapshot = await getDocs(chatQuery);
      const chatHistories: ChatHistory[] = [];
      
      console.log('📊 Raw query results:', querySnapshot.size, 'documents found');
      
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        
        console.log('📄 Processing document:', doc.id, {
          title: data.title,
          messageCount: data.chat_data?.length || 0,
          updatedAt: data.updatedAt
        });
        
        // Convert message timestamps from Firestore Timestamps to Date objects
        const chat_data = (data.chat_data || []).map((message: any) => ({
          ...message,
          timestamp: message.timestamp?.toDate ? message.timestamp.toDate() : new Date(message.timestamp)
        }));
        
        chatHistories.push({
          id: doc.id,
          user_id: data.user_id,
          session_id: data.session_id,
          chat_data: chat_data,
          title: data.title,
          createdAt: data.createdAt?.toDate() || new Date(),
          updatedAt: data.updatedAt?.toDate() || new Date(),
        });
      });
      
      // Sort by updatedAt on the client side instead
      chatHistories.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
      
      console.log('✅ Final chat history results:', chatHistories.length, 'sessions');
      console.log('📋 Session titles:', chatHistories.map(h => h.title));
      
      return chatHistories;
    } catch (error) {
      console.error('❌ Error fetching user chat history:', error);
      throw error;
    }
  }

  // Get specific chat session
  static async getChatHistory(sessionId: string): Promise<ChatHistory | null> {
    try {
      const chatDoc = doc(db, CHAT_HISTORY_COLLECTION, sessionId);
      const docSnap = await getDoc(chatDoc);
      
      if (docSnap.exists()) {
        const data = docSnap.data();
        
        // Convert message timestamps from Firestore Timestamps to Date objects
        const chat_data = (data.chat_data || []).map((message: any) => ({
          ...message,
          timestamp: message.timestamp?.toDate ? message.timestamp.toDate() : new Date(message.timestamp)
        }));
        
        return {
          id: docSnap.id,
          user_id: data.user_id,
          session_id: data.session_id,
          chat_data: chat_data,
          title: data.title,
          createdAt: data.createdAt?.toDate() || new Date(),
          updatedAt: data.updatedAt?.toDate() || new Date(),
        };
      }
      
      return null;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  }

  // Delete chat session
  static async deleteChatHistory(sessionId: string): Promise<void> {
    try {
      const chatDoc = doc(db, CHAT_HISTORY_COLLECTION, sessionId);
      await deleteDoc(chatDoc);
      console.log(`Chat history deleted for session: ${sessionId}`);
    } catch (error) {
      console.error('Error deleting chat history:', error);
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