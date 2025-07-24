'use client'

import { useState, useEffect } from 'react'
import { Brain, Activity, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { systemAPI } from '@/lib/api'
import { getAgentStatusColor, formatTime, cn } from '@/lib/utils'

interface Agent {
  agent_id: string
  name: string
  status: string
  current_iteration: number
  max_iterations: number
  execution_time?: number
  capabilities: string[]
  enabled: boolean
  priority: number
  tools_available?: number
}

interface SystemStatus {
  agents: Agent[]
  tools: Record<string, any>
  summary: {
    total_agents: number
    active_agents: number
    total_tools: number
    system_status: string
  }
}

export default function AgentStatus() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = async () => {
    try {
      const data = await systemAPI.getSystemStatus()
      setSystemStatus(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch system status')
      console.error('Status fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="h-full bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
          <p className="text-gray-600">Loading system status...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-2" />
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchStatus}
            className="mt-2 text-blue-600 hover:text-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-blue-600" />
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Agent Status</h1>
              <p className="text-sm text-gray-500">AI System Monitoring & Health</p>
            </div>
          </div>
          <button
            onClick={fetchStatus}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100"
          >
            <Activity className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* System Overview */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">System Overview</h2>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {systemStatus?.summary.total_agents || 0}
              </div>
              <div className="text-sm text-gray-500">Total Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {systemStatus?.summary.active_agents || 0}
              </div>
              <div className="text-sm text-gray-500">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {systemStatus?.summary.total_tools || 0}
              </div>
              <div className="text-sm text-gray-500">Tools Available</div>
            </div>
            <div className="text-center">
              <div className={cn(
                "text-2xl font-bold",
                systemStatus?.summary.system_status === 'operational' ? 'text-green-600' : 'text-red-600'
              )}>
                <CheckCircle className="w-8 h-8 mx-auto" />
              </div>
              <div className="text-sm text-gray-500">System Status</div>
            </div>
          </div>
        </div>

        {/* Agents List */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">AI Agents</h2>
          <div className="space-y-4">
            {systemStatus?.agents.map((agent) => (
              <div key={agent.agent_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={cn(
                      "w-3 h-3 rounded-full",
                      agent.enabled ? 'bg-green-500' : 'bg-gray-400'
                    )} />
                    <div>
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-500">{agent.agent_id}</p>
                    </div>
                  </div>
                  <div className={cn(
                    "px-2 py-1 rounded-full text-xs font-medium",
                    getAgentStatusColor(agent.status)
                  )}>
                    {agent.status}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Priority</div>
                    <div className="font-medium">{agent.priority}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Tools</div>
                    <div className="font-medium">{agent.tools_available || 0}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Execution Time</div>
                    <div className="font-medium">
                      {agent.execution_time ? formatTime(agent.execution_time) : 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="text-sm text-gray-500 mb-1">Capabilities</div>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.map((capability, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                      >
                        {capability.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tools Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Available Tools</h2>
          <div className="grid grid-cols-2 gap-4">
            {systemStatus?.tools && Object.entries(systemStatus.tools).map(([toolId, tool]) => (
              <div key={toolId} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{tool.name}</h3>
                  <div className={cn(
                    "w-3 h-3 rounded-full",
                    tool.initialized ? 'bg-green-500' : 'bg-red-500'
                  )} />
                </div>
                <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                <div className="text-xs text-gray-500">
                  Version: {tool.version || 'Unknown'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 