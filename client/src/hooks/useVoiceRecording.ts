import { useState, useRef, useCallback } from 'react'

interface UseVoiceRecordingProps {
  onRecordingComplete?: (audioBlob: Blob) => void
  onError?: (error: string) => void
}

export const useVoiceRecording = ({ onRecordingComplete, onError }: UseVoiceRecordingProps = {}) => {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const startTimeRef = useRef<number>(0)

  // Request microphone permission
  const requestPermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        } 
      })
      setHasPermission(true)
      // Stop the stream immediately since we just needed permission
      stream.getTracks().forEach(track => track.stop())
      return true
    } catch (error) {
      console.error('Microphone permission denied:', error)
      setHasPermission(false)
      onError?.('Microphone permission denied. Please allow microphone access to use voice recording.')
      return false
    }
  }, [onError])

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      // Request permission if not already granted
      if (hasPermission === null) {
        const granted = await requestPermission()
        if (!granted) return
      } else if (hasPermission === false) {
        onError?.('Microphone permission required. Please enable microphone access.')
        return
      }

      // Get media stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        } 
      })

      streamRef.current = stream
      audioChunksRef.current = []

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus' // WebM with Opus codec for better quality
      })

      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        setIsProcessing(true)
        try {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' })
          
          // Convert to MP3 (if needed, we can do this conversion on the backend instead)
          // For now, we'll send the WebM blob and let the backend handle conversion
          onRecordingComplete?.(audioBlob)
        } catch (error) {
          console.error('Error processing recording:', error)
          onError?.('Failed to process recording. Please try again.')
        } finally {
          setIsProcessing(false)
        }
      }

      // Start recording
      mediaRecorder.start(100) // Collect data every 100ms
      setIsRecording(true)
      startTimeRef.current = Date.now()

      // Start duration tracking
      durationIntervalRef.current = setInterval(() => {
        setRecordingDuration(Math.floor((Date.now() - startTimeRef.current) / 1000))
      }, 1000)

    } catch (error) {
      console.error('Failed to start recording:', error)
      onError?.('Failed to start recording. Please check your microphone.')
    }
  }, [hasPermission, requestPermission, onRecordingComplete, onError])

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setRecordingDuration(0)

      // Clear duration interval
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current)
        durationIntervalRef.current = null
      }

      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
    }
  }, [isRecording])

  // Cancel recording
  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      // Stop the media recorder without triggering the onstop event
      mediaRecorderRef.current.ondataavailable = null
      mediaRecorderRef.current.onstop = null
      mediaRecorderRef.current.stop()
      
      setIsRecording(false)
      setRecordingDuration(0)
      setIsProcessing(false)

      // Clear chunks
      audioChunksRef.current = []

      // Clear duration interval
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current)
        durationIntervalRef.current = null
      }

      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
    }
  }, [isRecording])

  // Cleanup
  const cleanup = useCallback(() => {
    cancelRecording()
  }, [cancelRecording])

  return {
    isRecording,
    isProcessing,
    recordingDuration,
    hasPermission,
    startRecording,
    stopRecording,
    cancelRecording,
    requestPermission,
    cleanup
  }
} 