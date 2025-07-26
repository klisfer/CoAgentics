'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Settings } from 'lucide-react'
import { systemAPI, chatAPI } from '@/lib/api'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'
import MessageBubble from './MessageBubble'
import AgentTyping from './AgentTyping'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent?: string
  metadata?: any
}

export default function ChatInterface() {
  const { currentUser } = useAuth()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your CoAgentics AI Financial Assistant. I can help you with financial planning, investment advice, calculations, and market research. What would you like to know?",
      role: 'assistant',
      timestamp: new Date(),
      agent: 'financial_assistant'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [apiVersion, setApiVersion] = useState<'v1' | 'v2' | 'demo'>('v2') // Default to v2
  const [showSettings, setShowSettings] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null) // Track session ID
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load session ID from localStorage on component mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('coagentics_session_id')
    if (savedSessionId && !sessionId) {
      setSessionId(savedSessionId)
      console.log('Restored session ID from localStorage:', savedSessionId)
    }
  }, [])

  // Save session ID to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('coagentics_session_id', sessionId)
      console.log('Saved session ID to localStorage:', sessionId)
    }
  }, [sessionId])

  // Clear chat and start new session
  const clearChat = () => {
    setMessages([
      {
        id: '1',
        content: "Hello! I'm your CoAgentics AI Financial Assistant. I can help you with financial planning, investment advice, calculations, and market research. What would you like to know?",
        role: 'assistant',
        timestamp: new Date(),
        agent: 'financial_assistant'
      }
    ])
    setSessionId(null) // Reset session ID to start fresh
    localStorage.removeItem('coagentics_session_id') // Clear from localStorage
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      let response: any

      // Choose API based on selected version
      switch (apiVersion) {
        case 'v2':
          // Use v2 endpoint (main2.py Financial Assistant)
          console.log('Sending message with user ID:', currentUser?.uid || 'anonymous_user', 'session ID:', sessionId || 'none (first request)')
          response = await chatAPI.sendMessageV2({ 
            message: input.trim(),
            user_id: currentUser?.uid || 'anonymous_user', // Use actual Firebase user ID
            session_id: sessionId || undefined // Pass current session ID (undefined for first request)
          })
          // Store session ID from response for future requests
          if (response.session_id && response.session_id !== sessionId) {
            console.log('Received new session ID:', response.session_id)
            setSessionId(response.session_id)
          }
          break
        case 'v1':
          // Use v1 endpoint (original agent system)
          response = await chatAPI.sendMessage({ message: input.trim() })
          break
        case 'demo':
        default:
          // Use demo API (no auth required)
          response = await systemAPI.demoChat(input.trim())
          break
      }
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
        agent: response.agent_used,
        metadata: response.metadata
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Chat error:', error)
      
      // Provide specific error messages based on the API version
      let errorContent = "I apologize, but I'm having trouble connecting to the AI service. Please try again in a moment."
      
      if (apiVersion === 'v2' && error?.response?.status === 503) {
        errorContent = "The advanced financial advisor (v2) is currently unavailable. Please try switching to v1 or demo mode."
      } else if (apiVersion !== 'demo' && error?.response?.status === 401) {
        errorContent = "Authentication required. Please try using demo mode for now."
      }
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorContent,
        role: 'assistant',
        timestamp: new Date(),
        agent: 'error'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-full">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">CoAgentics AI Assistant</h1>
              <p className="text-sm text-gray-500">
                Financial Intelligence & Advisory 
                <span className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                  {apiVersion.toUpperCase()}
                </span>
                {currentUser && (
                  <span className="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
                    {currentUser.displayName || currentUser.email || 'User'}
                  </span>
                )}
                {sessionId && (
                  <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                    Session: {sessionId.slice(-8)}
                  </span>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={clearChat}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Start New Conversation"
            >
              New Chat
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
            <h3 className="text-sm font-medium text-gray-900 mb-3">AI Assistant Version</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="apiVersion"
                  value="v2"
                  checked={apiVersion === 'v2'}
                  onChange={(e) => setApiVersion(e.target.value as 'v1' | 'v2' | 'demo')}
                  className="mr-2"
                />
                <span className="text-sm">
                  <strong>V2 - Advanced Financial Advisor</strong>
                  <br />
                  <span className="text-gray-600">Multi-agent system with specialized financial planning (requires auth)</span>
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="apiVersion"
                  value="v1"
                  checked={apiVersion === 'v1'}
                  onChange={(e) => setApiVersion(e.target.value as 'v1' | 'v2' | 'demo')}
                  className="mr-2"
                />
                <span className="text-sm">
                  <strong>V1 - Standard Assistant</strong>
                  <br />
                  <span className="text-gray-600">Original agent system with basic financial capabilities (requires auth)</span>
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="apiVersion"
                  value="demo"
                  checked={apiVersion === 'demo'}
                  onChange={(e) => setApiVersion(e.target.value as 'v1' | 'v2' | 'demo')}
                  className="mr-2"
                />
                <span className="text-sm">
                  <strong>Demo Mode</strong>
                  <br />
                  <span className="text-gray-600">Basic functionality without authentication required</span>
                </span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <AgentTyping />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about investments, retirement planning, or any financial topic..."
              className="w-full text-black px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[50px] max-h-32"
              rows={1}
              style={{
                height: 'auto',
                minHeight: '50px',
                maxHeight: '128px'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = Math.min(target.scrollHeight, 128) + 'px'
              }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={cn(
              "flex items-center justify-center w-12 h-12 rounded-lg transition-colors",
              input.trim() && !isLoading
                ? "bg-blue-600 hover:bg-blue-700 text-white"
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
} 