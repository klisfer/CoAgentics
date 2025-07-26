'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Settings } from 'lucide-react'
import { systemAPI, chatAPI } from '@/lib/api'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'
import { FirestoreService } from '@/lib/firestore'
import MessageBubble from './MessageBubble'
import AgentTyping from './AgentTyping'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent?: string
  metadata?: any
  timing_info?: any
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

  // Clear session on page load to start fresh each time
  useEffect(() => {
    localStorage.removeItem('coagentics_session_id')
    setSessionId(null)
    console.log('🆕 Starting fresh session - cleared any existing session data')
  }, [])

  // Save session ID to localStorage when it changes (but only for same-session continuity)
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('coagentics_session_id', sessionId)
      console.log('💾 Saved session ID for same-session continuity:', sessionId)
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
          
          // Fetch user profile from Firestore if user is authenticated
          let userProfile = null
          if (currentUser?.uid) {
            try {
              console.log('Fetching user profile from Firestore for user:', currentUser.uid)
              userProfile = await FirestoreService.getUserProfile(currentUser.uid)
              console.log('User profile fetched:', userProfile)
            } catch (error) {
              console.warn('Failed to fetch user profile from Firestore:', error)
            }
          }
          
          response = await chatAPI.sendMessageV2({ 
            message: input.trim(),
            user_id: currentUser?.uid || 'anonymous_user', // Use actual Firebase user ID
            session_id: sessionId || undefined, // Pass current session ID (undefined for first request)
            user_profile: userProfile // Include user profile data
          })
          // Store session ID from response for future requests
          if (response.session_id && response.session_id !== sessionId) {
            console.log('Received new session ID:', response.session_id)
            setSessionId(response.session_id)
          }
          // Log timing information
          if (response.timing_info) {
            console.log('⏱️ Backend Timing:', response.timing_info)
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
        metadata: response.metadata,
        timing_info: response.timing_info
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Chat error:', error)
      
      let errorContent = "I'm sorry, I encountered an error while processing your request. Please try again."
      
      if (error.response?.status === 503) {
        errorContent = "The AI service is currently unavailable. Please try again in a moment."
      } else if (error.response?.status === 429) {
        errorContent = "Too many requests. Please wait a moment before trying again."
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
            <h3 className="font-medium text-gray-900 mb-3">API Version</h3>
            <div className="space-y-2">
              {[
                { id: 'v2', name: 'V2 - Financial Assistant (Recommended)', desc: 'Google ADK-based financial advisor' },
                { id: 'v1', name: 'V1 - Multi-Agent System', desc: 'Original agent orchestration system' },
                { id: 'demo', name: 'Demo - Quick Chat', desc: 'Simple demo endpoint (no auth)' }
              ].map((version) => (
                <label key={version.id} className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="apiVersion"
                    value={version.id}
                    checked={apiVersion === version.id}
                    onChange={(e) => setApiVersion(e.target.value as any)}
                    className="mt-1"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{version.name}</div>
                    <div className="text-sm text-gray-600">{version.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <AgentTyping />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about investments, retirement planning, or any financial topic..."
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={1}
              style={{ minHeight: '52px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={cn(
              "px-4 py-3 rounded-lg font-medium transition-colors",
              !input.trim() || isLoading
                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
} 