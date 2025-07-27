'use client'

import { useState, useEffect } from 'react'
import { Mic, MicOff, Square, Loader2 } from 'lucide-react'
import { useVoiceRecording } from '@/hooks/useVoiceRecording'
import { cn } from '@/lib/utils'

interface VoiceRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void
  onError?: (error: string) => void
  disabled?: boolean
  className?: string
}

export default function VoiceRecorder({ 
  onRecordingComplete, 
  onError, 
  disabled = false,
  className 
}: VoiceRecorderProps) {
  const [recordingMode, setRecordingMode] = useState<'hold' | 'toggle'>('hold')
  
  const {
    isRecording,
    isProcessing,
    recordingDuration,
    hasPermission,
    startRecording,
    stopRecording,
    cancelRecording,
    requestPermission
  } = useVoiceRecording({
    onRecordingComplete,
    onError
  })

  // Format duration for display
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Handle mouse events for hold-to-record mode
  const handleMouseDown = () => {
    if (disabled || hasPermission === false) return
    
    if (recordingMode === 'hold' && !isRecording) {
      startRecording()
    }
  }

  const handleMouseUp = () => {
    if (recordingMode === 'hold' && isRecording) {
      stopRecording()
    }
  }

  const handleMouseLeave = () => {
    if (recordingMode === 'hold' && isRecording) {
      stopRecording()
    }
  }

  // Handle click for toggle mode
  const handleClick = () => {
    if (disabled || hasPermission === false) return
    
    if (recordingMode === 'toggle') {
      if (isRecording) {
        stopRecording()
      } else {
        startRecording()
      }
    }
  }

  // Request permission on first render if needed
  useEffect(() => {
    if (hasPermission === null) {
      // Don't auto-request permission, wait for user interaction
    }
  }, [hasPermission])

  const isDisabled = disabled || hasPermission === false || isProcessing

  if (hasPermission === false) {
    return (
      <button
        onClick={requestPermission}
        className={cn(
          "px-3 py-3 rounded-lg font-medium transition-colors",
          "bg-gray-100 text-gray-500 hover:bg-gray-200",
          className
        )}
        title="Click to enable microphone"
      >
        <MicOff className="w-5 h-5" />
      </button>
    )
  }

  return (
    <div className="flex items-center gap-2">
      {/* Recording Mode Toggle */}
      {isRecording && (
        <div className="text-xs text-gray-500 flex items-center gap-1">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          {formatDuration(recordingDuration)}
        </div>
      )}
      
      {/* Main Record Button */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        disabled={isDisabled}
        className={cn(
          "px-3 py-3 rounded-lg font-medium transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1",
          isRecording
            ? "bg-red-500 text-white hover:bg-red-600 shadow-lg scale-110"
            : isDisabled
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "bg-blue-100 text-blue-600 hover:bg-blue-200 hover:text-blue-700",
          className
        )}
        title={
          isRecording 
            ? `Recording... (${recordingMode === 'hold' ? 'release to stop' : 'click to stop'})`
            : hasPermission === null
            ? 'Click to start voice recording'
            : recordingMode === 'hold'
            ? 'Hold to record'
            : 'Click to start recording'
        }
      >
        {isProcessing ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : isRecording ? (
          recordingMode === 'hold' ? (
            <Square className="w-5 h-5" />
          ) : (
            <MicOff className="w-5 h-5" />
          )
        ) : (
          <Mic className="w-5 h-5" />
        )}
      </button>

      {/* Cancel Button (only show when recording in toggle mode) */}
      {isRecording && recordingMode === 'toggle' && (
        <button
          onClick={cancelRecording}
          className="px-2 py-1 text-xs text-gray-500 hover:text-red-500 transition-colors"
          title="Cancel recording"
        >
          Cancel
        </button>
      )}

      {/* Mode Switch (hidden for now, can be shown later) */}
      {false && !isRecording && (
        <button
          onClick={() => setRecordingMode(recordingMode === 'hold' ? 'toggle' : 'hold')}
          className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          title={`Switch to ${recordingMode === 'hold' ? 'click' : 'hold'} mode`}
        >
          {recordingMode === 'hold' ? 'Hold' : 'Click'}
        </button>
      )}
    </div>
  )
} 