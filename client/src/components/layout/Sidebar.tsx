'use client'

import { useState } from 'react'
import { 
  MessageCircle, 
  Calculator, 
  Activity, 
  Search, 
  Settings,
  Brain,
  TrendingUp,
  PiggyBank,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const navigation = [
  { id: 'chat', name: 'Chat', icon: MessageCircle, description: 'AI Assistant' },
  { id: 'calculators', name: 'Calculators', icon: Calculator, description: 'Financial Tools' },
  { id: 'research', name: 'Research', icon: Search, description: 'Market Data' },
  { id: 'portfolio', name: 'Portfolio', icon: TrendingUp, description: 'Analysis' },
  { id: 'planning', name: 'Planning', icon: PiggyBank, description: 'Goals & Strategy' },
  { id: 'agents', name: 'Agents', icon: Brain, description: 'AI Status' },
  { id: 'system', name: 'System', icon: Activity, description: 'Health & Monitoring' },
]

export default function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { currentUser, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <div className={cn(
      "bg-white border-r border-gray-200 flex flex-col transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-emerald-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">CoAgentics</h1>
              <p className="text-xs text-gray-500">AI Finance</p>
            </div>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 rounded-md hover:bg-gray-100 transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-500" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id

            return (
              <li key={item.id}>
                <button
                  onClick={() => onTabChange(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors",
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                  )}
                  title={isCollapsed ? item.name : undefined}
                >
                  <Icon className={cn(
                    "flex-shrink-0",
                    isActive ? "text-blue-600" : "text-gray-500",
                    isCollapsed ? "w-5 h-5" : "w-4 h-4"
                  )} />
                  {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="font-medium">{item.name}</div>
                      <div className="text-xs text-gray-500 truncate">
                        {item.description}
                      </div>
                    </div>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* User Profile */}
      <div className="border-t border-gray-200">
        {!isCollapsed ? (
          <div className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-gray-900 truncate">
                  {currentUser?.displayName || currentUser?.email || 'User'}
                </div>
                <div className="text-xs text-gray-500 truncate">
                  {currentUser?.email}
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        ) : (
          <div className="p-2">
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center p-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <div>CoAgentics AI System</div>
            <div>Version 1.0.0</div>
          </div>
        </div>
      )}
    </div>
  )
} 