'use client'

import { Bot, User, Clock, Zap } from 'lucide-react'
import { cn, formatTime } from '@/lib/utils'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent?: string
  metadata?: any
}

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isError = message.agent === 'error'

  const formatContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .split('\n')
      .map((line, index) => {
        // Handle bold text
        if (line.includes('**')) {
          const parts = line.split('**')
          return (
            <p key={index} className="mb-2">
              {parts.map((part, i) => 
                i % 2 === 1 ? <strong key={i}>{part}</strong> : part
              )}
            </p>
          )
        }
        
        // Handle bullet points
        if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
          return (
            <li key={index} className="ml-4">
              {line.trim().replace(/^[•-]\s*/, '')}
            </li>
          )
        }
        
        // Regular paragraph
        if (line.trim()) {
          return <p key={index} className="mb-2">{line}</p>
        }
        
        return <br key={index} />
      })
  }

  return (
    <div className={cn(
      "flex gap-3 max-w-4xl",
      isUser ? "ml-auto flex-row-reverse" : "mr-auto"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0",
        isUser 
          ? "bg-blue-600" 
          : isError
            ? "bg-red-500"
            : "bg-emerald-600"
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn(
        "flex flex-col gap-1 max-w-2xl",
        isUser ? "items-end" : "items-start"
      )}>
        {/* Message Bubble */}
        <div className={cn(
          "px-4 py-3 rounded-2xl",
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : isError
              ? "bg-red-50 text-red-900 border border-red-200 rounded-bl-md"
              : "bg-white text-gray-900 border border-gray-200 rounded-bl-md shadow-sm"
        )}>
          <div className="prose prose-sm max-w-none">
            {formatContent(message.content)}
          </div>
        </div>

        {/* Message Info */}
        <div className={cn(
          "flex items-center gap-2 text-xs text-gray-500",
          isUser ? "flex-row-reverse" : "flex-row"
        )}>
          <span>
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
          
          {!isUser && message.agent && message.agent !== 'error' && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                <span className="capitalize">
                  {message.agent.replace('_', ' ')}
                </span>
              </div>
            </>
          )}
          
          {message.metadata?.execution_time && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{formatTime(message.metadata.execution_time)}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
} 