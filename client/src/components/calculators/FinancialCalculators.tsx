'use client'

import { useState } from 'react'
import { Calculator, DollarSign, TrendingUp, Home, CreditCard } from 'lucide-react'
import { toolsAPI } from '@/lib/api'
import { formatCurrency, formatPercentage, cn } from '@/lib/utils'

interface CalculationResult {
  type: string
  data: any
  loading: boolean
  error?: string
}

export default function FinancialCalculators() {
  const [activeCalculator, setActiveCalculator] = useState('compound')
  const [results, setResults] = useState<Record<string, CalculationResult>>({})

  const calculators = [
    { id: 'compound', name: 'Compound Interest', icon: TrendingUp },
    { id: 'retirement', name: 'Retirement Planning', icon: DollarSign },
    { id: 'loan', name: 'Loan Calculator', icon: CreditCard },
    { id: 'emergency', name: 'Emergency Fund', icon: Home },
  ]

  const handleCalculation = async (type: string, data: any) => {
    setResults(prev => ({
      ...prev,
      [type]: { type, data: null, loading: true }
    }))

    try {
      let result
      if (type === 'compound') {
        result = await toolsAPI.calculateCompoundInterest(data)
      } else if (type === 'retirement') {
        result = await toolsAPI.calculateRetirement(data)
      } else {
        result = await toolsAPI.calculate({
          calculation_type: type === 'loan' ? 'loan_payment' : 'emergency_fund',
          parameters: data
        })
      }

      setResults(prev => ({
        ...prev,
        [type]: { type, data: result, loading: false }
      }))
    } catch (error) {
      setResults(prev => ({
        ...prev,
        [type]: { type, data: null, loading: false, error: 'Calculation failed' }
      }))
    }
  }

  return (
    <div className="h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <Calculator className="w-6 h-6 text-blue-600" />
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Financial Calculators</h1>
            <p className="text-sm text-gray-500">Powerful tools for financial planning</p>
          </div>
        </div>
      </div>

      <div className="flex h-full">
        {/* Calculator Tabs */}
        <div className="w-64 bg-white border-r border-gray-200 p-4">
          <div className="space-y-2">
            {calculators.map(calc => {
              const Icon = calc.icon
              return (
                <button
                  key={calc.id}
                  onClick={() => setActiveCalculator(calc.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors",
                    activeCalculator === calc.id
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-50"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{calc.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Calculator Content */}
        <div className="flex-1 p-6">
          {activeCalculator === 'compound' && (
            <CompoundInterestCalculator 
              onCalculate={(data) => handleCalculation('compound', data)}
              result={results.compound}
            />
          )}
          {activeCalculator === 'retirement' && (
            <RetirementCalculator 
              onCalculate={(data) => handleCalculation('retirement', data)}
              result={results.retirement}
            />
          )}
          {activeCalculator === 'loan' && (
            <LoanCalculator 
              onCalculate={(data) => handleCalculation('loan', data)}
              result={results.loan}
            />
          )}
          {activeCalculator === 'emergency' && (
            <EmergencyFundCalculator 
              onCalculate={(data) => handleCalculation('emergency', data)}
              result={results.emergency}
            />
          )}
        </div>
      </div>
    </div>
  )
}

// Compound Interest Calculator
function CompoundInterestCalculator({ onCalculate, result }: { onCalculate: (data: any) => void; result?: CalculationResult }) {
  const [formData, setFormData] = useState({
    principal: 10000,
    annual_rate: 7,
    years: 10,
    compounds_per_year: 12
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCalculate(formData)
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-semibold mb-4">Compound Interest Calculator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Initial Investment
            </label>
            <input
              type="number"
              value={formData.principal}
              onChange={(e) => setFormData(prev => ({ ...prev, principal: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Annual Interest Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.annual_rate}
              onChange={(e) => setFormData(prev => ({ ...prev, annual_rate: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time Period (years)
            </label>
            <input
              type="number"
              value={formData.years}
              onChange={(e) => setFormData(prev => ({ ...prev, years: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Compounding Frequency
            </label>
            <select
              value={formData.compounds_per_year}
              onChange={(e) => setFormData(prev => ({ ...prev, compounds_per_year: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>Annually</option>
              <option value={4}>Quarterly</option>
              <option value={12}>Monthly</option>
              <option value={365}>Daily</option>
            </select>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={result?.loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {result?.loading ? 'Calculating...' : 'Calculate'}
        </button>
      </form>

      {result?.data && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Results</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Final Amount</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(result.data.result?.final_amount || 0)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Interest Earned</div>
              <div className="text-xl font-semibold text-blue-600">
                {formatCurrency(result.data.result?.total_interest || 0)}
              </div>
            </div>
          </div>
          {result.data.explanation && (
            <p className="mt-4 text-sm text-gray-600">{result.data.explanation}</p>
          )}
        </div>
      )}
    </div>
  )
}

// Retirement Calculator
function RetirementCalculator({ onCalculate, result }: { onCalculate: (data: any) => void; result?: CalculationResult }) {
  const [formData, setFormData] = useState({
    current_age: 30,
    retirement_age: 65,
    current_savings: 50000,
    monthly_contribution: 1000,
    annual_return: 8
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCalculate(formData)
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-semibold mb-4">Retirement Planning Calculator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Age
            </label>
            <input
              type="number"
              value={formData.current_age}
              onChange={(e) => setFormData(prev => ({ ...prev, current_age: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Retirement Age
            </label>
            <input
              type="number"
              value={formData.retirement_age}
              onChange={(e) => setFormData(prev => ({ ...prev, retirement_age: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Savings
            </label>
            <input
              type="number"
              value={formData.current_savings}
              onChange={(e) => setFormData(prev => ({ ...prev, current_savings: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Contribution
            </label>
            <input
              type="number"
              value={formData.monthly_contribution}
              onChange={(e) => setFormData(prev => ({ ...prev, monthly_contribution: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Expected Annual Return (%)
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.annual_return}
              onChange={(e) => setFormData(prev => ({ ...prev, annual_return: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={result?.loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {result?.loading ? 'Calculating...' : 'Calculate'}
        </button>
      </form>

      {result?.data && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Retirement Projection</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-500">Total at Retirement</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(result.data.result?.projected_retirement_savings || 0)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500">Monthly Income (4% rule)</div>
              <div className="text-xl font-semibold text-blue-600">
                {formatCurrency(result.data.result?.monthly_withdrawal_4_percent || 0)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Placeholder for other calculators
function LoanCalculator({ onCalculate, result }: { onCalculate: (data: any) => void; result?: CalculationResult }) {
  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-semibold mb-4">Loan Calculator</h2>
      <p className="text-gray-600">Loan calculator coming soon...</p>
    </div>
  )
}

function EmergencyFundCalculator({ onCalculate, result }: { onCalculate: (data: any) => void; result?: CalculationResult }) {
  return (
    <div className="max-w-2xl">
      <h2 className="text-xl font-semibold mb-4">Emergency Fund Calculator</h2>
      <p className="text-gray-600">Emergency fund calculator coming soon...</p>
    </div>
  )
} 