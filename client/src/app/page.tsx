'use client'

import { useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import Sidebar from '@/components/layout/Sidebar'
import ChatInterface from '@/components/chat/ChatInterface'
import FinancialCalculators from '@/components/calculators/FinancialCalculators'
import AgentStatus from '@/components/status/AgentStatus'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface />
      case 'calculators':
        return <FinancialCalculators />
      case 'agents':
        return <AgentStatus />
      case 'research':
        return <PlaceholderPage title="Market Research" description="Coming soon..." />
      case 'portfolio':
        return <PlaceholderPage title="Portfolio Analysis" description="Coming soon..." />
      case 'planning':
        return <PlaceholderPage title="Financial Planning" description="Coming soon..." />
      case 'system':
        return <PlaceholderPage title="System Health" description="Coming soon..." />
      default:
        return <ChatInterface />
    }
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-100">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </ProtectedRoute>
  )
}

function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <div className="h-full bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-600">{description}</p>
        </div>
    </div>
  )
}
