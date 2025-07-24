'use client'

import { Bot } from 'lucide-react'

export default function AgentTyping() {
  return (
    <div className="flex gap-3 max-w-4xl mr-auto">
      {/* Avatar */}
      <div className="flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0 bg-emerald-600">
        <Bot className="w-4 h-4 text-white" />
      </div>

      {/* Typing Indicator */}
      <div className="flex flex-col gap-1">
        <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-bl-md shadow-sm">
          <div className="flex items-center gap-1">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm text-gray-500 ml-2">AI is thinking...</span>
          </div>
        </div>
      </div>
    </div>
  )
} 