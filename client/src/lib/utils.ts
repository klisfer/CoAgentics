import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

export function formatNumber(num: number, decimals = 2): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num)
}

export function formatPercentage(num: number, decimals = 1): string {
  return `${formatNumber(num, decimals)}%`
}

export function formatTime(seconds: number): string {
  if (seconds < 1) {
    return `${Math.round(seconds * 1000)}ms`
  }
  return `${formatNumber(seconds, 2)}s`
}

export function getAgentStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'idle':
      return 'text-green-600 bg-green-100'
    case 'thinking':
    case 'executing':
      return 'text-blue-600 bg-blue-100'
    case 'waiting':
      return 'text-yellow-600 bg-yellow-100'
    case 'completed':
      return 'text-emerald-600 bg-emerald-100'
    case 'error':
      return 'text-red-600 bg-red-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function parseFinancialData(data: any) {
  if (!data) return null
  
  // Handle different types of financial calculation results
  if (data.calculation_type) {
    return {
      type: data.calculation_type,
      inputs: data.inputs,
      result: data.result,
      explanation: data.explanation,
      assumptions: data.assumptions,
    }
  }
  
  return data
} 