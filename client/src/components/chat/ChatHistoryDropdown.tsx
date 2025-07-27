'use client'

import { useState, useEffect, useRef } from 'react'
import { Clock, ChevronDown, Trash2, MessageCircle } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { FirestoreService, ChatHistory } from '@/lib/firestore'
import { cn } from '@/lib/utils'

interface ChatHistoryDropdownProps {
  onSelectHistory: (chatHistory: ChatHistory) => void
  onNewChat: () => void
  currentSessionId?: string
  refreshTrigger?: number
}

export default function ChatHistoryDropdown({ onSelectHistory, onNewChat, currentSessionId, refreshTrigger }: ChatHistoryDropdownProps) {
  const { currentUser } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([])
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Fetch chat histories when user changes
  useEffect(() => {
    if (currentUser?.uid) {
      fetchChatHistories()
    }
  }, [currentUser?.uid])

  // Refresh chat histories when refreshTrigger changes
  useEffect(() => {
    if (currentUser?.uid && refreshTrigger !== undefined && refreshTrigger > 0) {
      console.log('🔄 Refreshing chat history due to trigger:', refreshTrigger)
      fetchChatHistories()
    }
  }, [refreshTrigger, currentUser?.uid])

  const fetchChatHistories = async () => {
    if (!currentUser?.uid) return

    setLoading(true)
    try {
      console.log('🔄 ChatHistoryDropdown: Fetching histories for user:', currentUser.uid)
      const histories = await FirestoreService.getUserChatHistory(currentUser.uid)
      console.log('📋 ChatHistoryDropdown: Received', histories.length, 'histories')
      console.log('📋 ChatHistoryDropdown: History details:', histories.map(h => ({
        id: h.id,
        session_id: h.session_id,
        title: h.title,
        messageCount: h.chat_data.length,
        updatedAt: h.updatedAt
      })))
      setChatHistories(histories)
    } catch (error) {
      console.error('❌ Error fetching chat histories:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectHistory = (history: ChatHistory) => {
    onSelectHistory(history)
    setIsOpen(false)
  }

  const handleDeleteHistory = async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    
    if (window.confirm('Are you sure you want to delete this chat?')) {
      try {
        await FirestoreService.deleteChatHistory(sessionId)
        await fetchChatHistories() // Refresh the list
      } catch (error) {
        console.error('Error deleting chat history:', error)
      }
    }
  }

  const handleNewChat = () => {
    onNewChat()
    setIsOpen(false)
  }

  const formatDate = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const truncateTitle = (title: string, maxLength: number = 30) => {
    return title.length > maxLength ? `${title.substring(0, maxLength)}...` : title
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <Clock className="w-4 h-4 text-gray-500" />
        <span className="text-gray-700">Chat History</span>
        <ChevronDown className={cn(
          "w-4 h-4 text-gray-500 transition-transform",
          isOpen && "rotate-180"
        )} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 flex items-center gap-3"
          >
            <MessageCircle className="w-4 h-4 text-blue-600" />
            <span className="font-medium text-blue-600">Start New Chat</span>
          </button>

          {/* Loading State */}
          {loading && (
            <div className="px-4 py-8 text-center text-gray-500">
              Loading chat history...
            </div>
          )}

          {/* Empty State */}
          {!loading && chatHistories.length === 0 && (
            <div className="px-4 py-8 text-center text-gray-500">
              No chat history found
            </div>
          )}

          {/* Chat History List */}
          {!loading && chatHistories.map((history) => (
            <div
              key={history.session_id}
              className={cn(
                "group relative border-b border-gray-100 last:border-b-0",
                history.session_id === currentSessionId && "bg-blue-50"
              )}
            >
              <button
                onClick={() => handleSelectHistory(history)}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <MessageCircle className="w-3 h-3 text-gray-400 flex-shrink-0" />
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {truncateTitle(history.title || 'Untitled Chat')}
                      </p>
                    </div>
                    <p className="text-xs text-gray-500">
                      {formatDate(history.updatedAt)}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {history.chat_data.length} messages
                    </p>
                  </div>
                  
                  <button
                    onClick={(e) => handleDeleteHistory(history.session_id, e)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-100 rounded"
                    title="Delete chat"
                  >
                    <Trash2 className="w-3 h-3 text-red-500" />
                  </button>
                </div>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 