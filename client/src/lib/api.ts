import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://localhost:8002'; // Force port 8002 for main2.py
const API_PREFIX = '/api/v1';

const api = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface ChatMessage {
  message: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  agent_used: string;
  metadata?: Record<string, any>;
  conversation_id: string;
  session_id: string;
}

export interface AgentStatus {
  agent_id: string;
  name: string;
  status: string;
  current_iteration: number;
  max_iterations: number;
  execution_time?: number;
  capabilities: string[];
  enabled: boolean;
  priority: number;
  tools_available?: number;
}

export interface ToolStatus {
  name: string;
  id: string;
  status: string;
  description: string;
}

export interface SystemHealth {
  status: string;
  version: string;
  environment: string;
  agent_manager: string;
  agents: Record<string, any>;
  tools: Record<string, any>;
  master_planner: string;
  total_agents: number;
  enabled_agents: number;
  total_tools: number;
}

export interface FinancialCalculation {
  calculation_type: string;
  parameters: Record<string, any>;
}

export interface ToolResponse {
  success: boolean;
  data?: any;
  error?: string;
  execution_time?: number;
  tool_name: string;
}

// API functions
export const chatAPI = {
  // Send message to AI agents (v1 - original system)
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post('/chat/message', message);
    return response.data;
  },

  // Send message to AI agents (v2 - main2.py Financial Assistant)
  sendMessageV2: async (message: { message: string, user_id: string, session_id?: string }): Promise<{ response: string, session_id: string, agent_used?: string }> => {
    const url = `${API_BASE_URL}/chat`;
    console.log('Making API call to:', url);
    const response = await axios.post(url, {
      user_id: message.user_id,
      session_id: message.session_id || null,
      new_message: message.message
    }, {
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    // Transform response to match expected format
    return {
      response: response.data.response_text,
      session_id: response.data.session_id,
      agent_used: 'financial_assistant'
    };
  },

  // Get conversation history
  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get(`/chat/history?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  // Clear conversation history
  clearHistory: async () => {
    const response = await api.post('/chat/clear-history');
    return response.data;
  },

  // Get agent status
  getAgentStatus: async () => {
    const response = await api.get('/chat/agents/status');
    return response.data;
  },
};

export const toolsAPI = {
  // Perform financial calculation
  calculate: async (calculation: FinancialCalculation): Promise<ToolResponse> => {
    const response = await api.post('/tools/calculate', calculation);
    return response.data;
  },

  // Quick compound interest calculation
  calculateCompoundInterest: async (params: {
    principal: number;
    annual_rate: number;
    years: number;
    compounds_per_year?: number;
  }) => {
    const response = await api.post('/tools/calculate/compound-interest', null, { params });
    return response.data;
  },

  // Quick retirement calculation
  calculateRetirement: async (params: {
    current_age: number;
    retirement_age: number;
    current_savings: number;
    monthly_contribution: number;
    annual_return: number;
    desired_monthly_income?: number;
  }) => {
    const response = await api.post('/tools/calculate/retirement', null, { params });
    return response.data;
  },

  // Web search
  webSearch: async (query: string, max_results = 5): Promise<ToolResponse> => {
    const response = await api.post('/tools/web-search', { query, max_results });
    return response.data;
  },

  // Financial search
  financialSearch: async (query: string, max_results = 5): Promise<ToolResponse> => {
    const response = await api.post('/tools/financial-search', { query, max_results });
    return response.data;
  },

  // Get available calculation types
  getCalculationTypes: async () => {
    const response = await api.get('/tools/calculate/types');
    return response.data;
  },

  // Get tools status
  getToolsStatus: async () => {
    const response = await api.get('/tools/tools/status');
    return response.data;
  },

  // Search market data
  searchMarketData: async (symbol: string, max_results = 3) => {
    const response = await api.get(`/tools/search/market/${symbol}?max_results=${max_results}`);
    return response.data;
  },
};

export const systemAPI = {
  // Get system health
  getHealth: async (): Promise<SystemHealth> => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  // Get system agent status
  getSystemStatus: async () => {
    const response = await axios.get(`${API_BASE_URL}/agents/status`);
    return response.data;
  },

  // Get API info
  getApiInfo: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/info`);
    return response.data;
  },

  // Demo chat (no auth required)
  demoChat: async (message: string) => {
    const response = await axios.post(`${API_BASE_URL}/demo/quick-chat?message=${encodeURIComponent(message)}`);
    return response.data;
  },
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export default api; 