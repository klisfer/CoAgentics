'use client'

import { useState } from 'react'
import { Bot, User, Clock, Zap, Info } from 'lucide-react'
import { cn, formatTime } from '@/lib/utils'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent?: string
  metadata?: any
  timing_info?: any
}

interface MessageBubbleProps {
  message: Message
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isError = message.agent === 'error'
  const [showInfo, setShowInfo] = useState(false)

  const formatContent = (content: string) => {
    // URL regex pattern
    const urlRegex = /(https?:\/\/[^\s]+)/g
    
    // Function to convert URLs to clickable links
    const linkifyText = (text: string) => {
      const parts = text.split(urlRegex)
      return parts.map((part, i) => {
        if (urlRegex.test(part)) {
          return (
            <a
              key={i}
              href={part}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline break-all font-medium hover:bg-blue-50 px-1 py-0.5 rounded transition-colors"
              onClick={(e) => {
                // Log the click and show a helpful message
                console.log('User clicked link:', part)
                
                // Optional: Show a toast notification
                if (part.includes('localhost:8080')) {
                  console.log('Opening login page - your chat session will be preserved when you return!')
                }
              }}
            >
              {part}
            </a>
          )
        }
        return part
      })
    }
    
    // Simple markdown-like formatting with URL detection
    return content
      .split('\n')
      .map((line, index) => {
        // Handle bold text
        if (line.includes('**')) {
          const parts = line.split('**')
          return (
            <p key={index} className="mb-2">
              {parts.map((part, i) => 
                i % 2 === 1 ? <strong key={i}>{linkifyText(part)}</strong> : linkifyText(part)
              )}
            </p>
          )
        }
        
        // Handle bullet points
        if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
          return (
            <li key={index} className="ml-4">
              {linkifyText(line.trim().replace(/^[•-]\s*/, ''))}
            </li>
          )
        }
        
        // Regular paragraph
        if (line.trim()) {
          return <p key={index} className="mb-2">{linkifyText(line)}</p>
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
          <div className={cn("prose prose-sm max-w-none", isUser ? "text-white" : "text-black")}>
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
          
          {/* Info button for additional details */}
          {(!isUser && (message.timing_info || message.metadata)) && (
            <>
              <span>•</span>
              <button
                onClick={() => setShowInfo(!showInfo)}
                className="flex items-center gap-1 hover:text-gray-700 transition-colors p-0.5 rounded hover:bg-gray-100"
                title="Show message details"
              >
                <Info className="w-3 h-3" />
              </button>
            </>
          )}
        </div>
        
        {/* Message Details Panel */}
        {showInfo && (message.timing_info || message.metadata) && (
                      <div className="mt-2 p-3 bg-gray-50 rounded-lg border text-xs">
              <div className="font-medium text-gray-700 mb-2">Message Details</div>
              <div className="space-y-2">
                
                {/* Timing Information */}
                {message.timing_info && (
                  <div>
                    <div className="font-medium text-gray-600 mb-1">Performance Breakdown:</div>
                    <div className="space-y-1 ml-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Time:</span>
                        <span className="font-mono">{message.timing_info.total_time}s</span>
                      </div>
                      {message.timing_info.operations && Object.entries(message.timing_info.operations).map(([operation, time]) => (
                        <div key={operation} className="flex justify-between">
                          <span className="text-gray-600 capitalize">{operation.replace(/_/g, ' ')}:</span>
                          <span className="font-mono">{time as number}s</span>
                        </div>
                      ))}
                      {message.timing_info.unaccounted_time > 0 && (
                        <div className="flex justify-between text-gray-500">
                          <span>Unaccounted Time:</span>
                          <span className="font-mono">{message.timing_info.unaccounted_time}s</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Additional Metadata */}
                {message.metadata && Object.keys(message.metadata).length > 0 && (
                  <div>
                    <div className="font-medium text-gray-600 mb-1">Additional Info:</div>
                    <div className="space-y-1 ml-2">
                      {Object.entries(message.metadata).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-mono">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
              </div>
            </div>
        )}
      </div>
    </div>
  )
} 