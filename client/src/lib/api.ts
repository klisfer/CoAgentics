import axios from 'axios';

// Base configuration
const API_BASE_URL_V1 = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE_URL_V2 = process.env.NEXT_PUBLIC_API_URL_V2 || 'http://localhost:8002';
const API_PREFIX = '/api/v1';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: `${API_BASE_URL_V1}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - could redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Types
export interface ChatMessage {
  message: string;
}

export interface ChatResponse {
  response: string;
  agent_used: string;
  metadata: any;
  conversation_id: string;
  session_id: string;
}

export interface AgentStatus {
  name: string;
  status: 'active' | 'inactive' | 'error';
  lastActivity?: string;
}

export interface ToolStatus {
  name: string;
  status: 'available' | 'unavailable' | 'error';
  lastUsed?: string;
}

export interface SystemInfo {
  version: string;
  uptime: string;
  agents: AgentStatus[];
  tools: ToolStatus[];
}

// Enhanced interfaces for comprehensive system status
export interface AgentInfo {
  agent_id: string;
  name: string;
  status: string;
  current_iteration: number;
  max_iterations: number;
  execution_time?: number;
  capabilities: string[];
  enabled: boolean;
  priority: number;
  tools_available: number;
}

export interface ToolInfo {
  name: string;
  description: string;
  initialized: boolean;
  version: string;
}

export interface SystemSummary {
  total_agents: number;
  active_agents: number;
  total_tools: number;
  system_status: string;
}

export interface SystemStatusResponse {
  agents: AgentInfo[];
  tools: Record<string, ToolInfo>;
  summary: SystemSummary;
}

// API functions
export const chatAPI = {
  // Send message to AI agents (v1 - original system)
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post('/chat/message', message);
    return response.data;
  },

  // Send message to AI agents (v2 - main2.py Financial Assistant)
  sendMessageV2: async (message: { message: string, user_id: string, session_id?: string, user_profile?: any }): Promise<{ response: string, session_id: string, agent_used?: string, timing_info?: any, requires_auth?: boolean, auth_url?: string, auth_message?: string }> => {
    const url = `${API_BASE_URL_V2}/chat`;
    console.log('Making API call to:', url);
    console.log('User profile being sent:', message.user_profile);
    
    const response = await axios.post(url, {
      user_id: message.user_id,
      session_id: message.session_id || null,
      user_message: message.message,
      user_profile: message.user_profile || null
    }, {
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    // Transform response to match expected format
    return {
      response: response.data.response_text,
      session_id: response.data.session_id,
      agent_used: 'financial_assistant',
      timing_info: response.data.timing_info,
      requires_auth: response.data.requires_auth,
      auth_url: response.data.auth_url,
      auth_message: response.data.auth_message
    };
  },

  // Get conversation history
  getHistory: async (sessionId?: string) => {
    const params = sessionId ? { session_id: sessionId } : {};
    const response = await api.get('/chat/history', { params });
    return response.data;
  },
};

export const toolsAPI = {
  // Web search
  webSearch: async (query: string) => {
    const response = await api.post('/tools/web-search', { query });
    return response.data;
  },

  // Financial calculator
  calculateFinance: async (calculation: any) => {
    const response = await api.post('/tools/financial-calculator', calculation);
    return response.data;
  },
};

export const systemAPI = {
  // Get system health and status
  getStatus: async (): Promise<SystemInfo> => {
    const response = await api.get('/system/status');
    return response.data;
  },

  // Get comprehensive system status (for AgentStatus component)
  getSystemStatus: async (): Promise<SystemStatusResponse> => {
    const url = `${API_BASE_URL_V2}/system/status`;
    console.log('Fetching system status from:', url);
    const response = await axios.get(url, {
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return response.data;
  },

  // Get API info
  getInfo: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Demo chat endpoint
  demoChat: async (message: string) => {
    const response = await api.post('/demo/chat', { message });
    return response.data;
  },
};

export const authAPI = {
  // Login with email/password
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token);
    }
    return response.data;
  },

  // Register new user
  register: async (email: string, password: string, name: string) => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },

  // Logout
  logout: async () => {
    localStorage.removeItem('auth_token');
    const response = await api.post('/auth/logout');
    return response.data;
  },

  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },
};

export default api; 