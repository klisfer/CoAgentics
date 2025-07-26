'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { FirestoreService, UserProfile, INDUSTRY_TYPES, INDIAN_STATES } from '@/lib/firestore';
import { Loader2, CheckCircle, User, MapPin, Briefcase, Users, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormData {
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer-not-to-say';
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed';
  employmentStatus: 'salaried' | 'self-employed' | 'unemployed';
  industryType: string;
  monthlyIncome: number;
  dependents: {
    wife: boolean;
    parents: boolean;
    kids: boolean;
  };
  kidsCount: number;
  location: {
    state: string;
    city: string;
  };
  insurance: {
    life: boolean;
    health: boolean;
  };
  insuranceCoverage: {
    healthClaimLimit: number;
    lifeClaimLimit: number;
  };
}

const STEPS = [
  { id: 'personal', title: 'Personal Information', icon: User },
  { id: 'employment', title: 'Employment Details', icon: Briefcase },
  { id: 'family', title: 'Family & Dependents', icon: Users },
  { id: 'location', title: 'Location', icon: MapPin },
  { id: 'insurance', title: 'Insurance', icon: Shield },
];

export default function OnboardingForm() {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { currentUser, refreshUserProfile } = useAuth();
  const router = useRouter();

  const [formData, setFormData] = useState<FormData>({
    name: currentUser?.displayName || '',
    age: 25,
    gender: 'prefer-not-to-say',
    maritalStatus: 'single',
    employmentStatus: 'salaried',
    industryType: '',
    monthlyIncome: 0,
    dependents: {
      wife: false,
      parents: false,
      kids: false,
    },
    kidsCount: 0,
    location: {
      state: '',
      city: '',
    },
    insurance: {
      life: false,
      health: false,
    },
    insuranceCoverage: {
      healthClaimLimit: 0,
      lifeClaimLimit: 0,
    },
  });

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 0: // Personal Information
        if (!formData.name.trim()) newErrors.name = 'Name is required';
        if (formData.age < 18 || formData.age > 100) newErrors.age = 'Age must be between 18 and 100';
        break;
      case 1: // Employment
        if (formData.employmentStatus === 'salaried' && !formData.industryType) {
          newErrors.industryType = 'Industry type is required for salaried employees';
        }
        if (formData.employmentStatus !== 'unemployed' && formData.monthlyIncome <= 0) {
          newErrors.monthlyIncome = 'Monthly income is required and must be greater than 0';
        }
        break;
      case 2: // Family
        if (formData.dependents.kids && formData.kidsCount < 1) {
          newErrors.kidsCount = 'Number of kids is required when kids dependency is selected';
        }
        break;
      case 3: // Location
        if (!formData.location.state) newErrors.state = 'State is required';
        if (!formData.location.city.trim()) newErrors.city = 'City is required';
        break;
      case 4: // Insurance
        if (formData.insurance.health && formData.insuranceCoverage.healthClaimLimit <= 0) {
          newErrors.healthClaimLimit = 'Health insurance claim limit is required when health insurance is selected';
        }
        if (formData.insurance.life && formData.insuranceCoverage.lifeClaimLimit <= 0) {
          newErrors.lifeClaimLimit = 'Life insurance claim limit is required when life insurance is selected';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      if (currentStep < STEPS.length - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        handleSubmit();
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!currentUser) return;

    setLoading(true);
    try {
      // Create base profile object
      const baseProfile = {
        uid: currentUser.uid,
        email: currentUser.email || '',
        name: formData.name,
        age: formData.age,
        gender: formData.gender,
        maritalStatus: formData.maritalStatus,
        employmentStatus: formData.employmentStatus,
        monthlyIncome: formData.monthlyIncome,
        dependents: formData.dependents,
        location: formData.location,
        insurance: formData.insurance,
        insuranceCoverage: formData.insuranceCoverage,
        profileCompleted: true,
      };

      // Add conditional fields only if they have valid values
      const profile: Omit<UserProfile, 'createdAt' | 'updatedAt'> = {
        ...baseProfile,
        ...(formData.employmentStatus === 'salaried' && formData.industryType && {
          industryType: formData.industryType
        }),
        ...(formData.dependents.kids && formData.kidsCount > 0 && {
          kidsCount: formData.kidsCount
        }),
      };

      await FirestoreService.createUserProfile(profile);
      
      // Refresh the auth context to update onboarding status
      await refreshUserProfile();
      
      router.push('/');
    } catch (error) {
      console.error('Error saving profile:', error);
      setErrors({ submit: 'Failed to save profile. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (updates: Partial<FormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => updateFormData({ name: e.target.value })}
                className={cn(
                  "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                  errors.name ? "border-red-500" : "border-gray-300"
                )}
                placeholder="Enter your full name"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Age *
              </label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => updateFormData({ age: parseInt(e.target.value) || 0 })}
                className={cn(
                  "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                  errors.age ? "border-red-500" : "border-gray-300"
                )}
                min="18"
                max="100"
              />
              {errors.age && <p className="text-red-500 text-sm mt-1">{errors.age}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Gender
              </label>
              <select
                value={formData.gender}
                onChange={(e) => updateFormData({ gender: e.target.value as FormData['gender'] })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
                <option value="prefer-not-to-say">Prefer not to say</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Marital Status
              </label>
              <select
                value={formData.maritalStatus}
                onChange={(e) => updateFormData({ maritalStatus: e.target.value as FormData['maritalStatus'] })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="single">Single</option>
                <option value="married">Married</option>
                <option value="divorced">Divorced</option>
                <option value="widowed">Widowed</option>
              </select>
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Employment Status
              </label>
              <select
                value={formData.employmentStatus}
                onChange={(e) => updateFormData({ 
                  employmentStatus: e.target.value as FormData['employmentStatus'],
                  industryType: e.target.value !== 'salaried' ? '' : formData.industryType
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="salaried">Salaried</option>
                <option value="self-employed">Self-employed</option>
                <option value="unemployed">Unemployed</option>
              </select>
            </div>

            {formData.employmentStatus === 'salaried' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry Type *
                </label>
                <select
                  value={formData.industryType}
                  onChange={(e) => updateFormData({ industryType: e.target.value })}
                  className={cn(
                    "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    errors.industryType ? "border-red-500" : "border-gray-300"
                  )}
                >
                  <option value="">Select Industry</option>
                  {INDUSTRY_TYPES.map((industry) => (
                    <option key={industry} value={industry}>
                      {industry}
                    </option>
                  ))}
                </select>
                {errors.industryType && <p className="text-red-500 text-sm mt-1">{errors.industryType}</p>}
              </div>
            )}

            {formData.employmentStatus !== 'unemployed' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Income (₹) *
                </label>
                <input
                  type="number"
                  value={formData.monthlyIncome || ''}
                  onChange={(e) => updateFormData({ monthlyIncome: parseInt(e.target.value) || 0 })}
                  placeholder="Enter your monthly income in rupees"
                  className={cn(
                    "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    errors.monthlyIncome ? "border-red-500" : "border-gray-300"
                  )}
                />
                {errors.monthlyIncome && <p className="text-red-500 text-sm mt-1">{errors.monthlyIncome}</p>}
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Dependents (Select all that apply)
              </label>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.dependents.wife}
                    onChange={(e) => updateFormData({
                      dependents: { ...formData.dependents, wife: e.target.checked }
                    })}
                    className="mr-2 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm">Wife</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.dependents.parents}
                    onChange={(e) => updateFormData({
                      dependents: { ...formData.dependents, parents: e.target.checked }
                    })}
                    className="mr-2 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm">Parents</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.dependents.kids}
                    onChange={(e) => updateFormData({
                      dependents: { ...formData.dependents, kids: e.target.checked },
                      kidsCount: e.target.checked ? formData.kidsCount : 0
                    })}
                    className="mr-2 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm">Kids</span>
                </label>
              </div>
            </div>

            {formData.dependents.kids && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Kids *
                </label>
                <input
                  type="number"
                  value={formData.kidsCount}
                  onChange={(e) => updateFormData({ kidsCount: parseInt(e.target.value) || 0 })}
                  className={cn(
                    "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    errors.kidsCount ? "border-red-500" : "border-gray-300"
                  )}
                  min="1"
                  max="10"
                />
                {errors.kidsCount && <p className="text-red-500 text-sm mt-1">{errors.kidsCount}</p>}
              </div>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State *
              </label>
              <select
                value={formData.location.state}
                onChange={(e) => updateFormData({
                  location: { ...formData.location, state: e.target.value }
                })}
                className={cn(
                  "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                  errors.state ? "border-red-500" : "border-gray-300"
                )}
              >
                <option value="">Select State</option>
                {INDIAN_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
              {errors.state && <p className="text-red-500 text-sm mt-1">{errors.state}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City *
              </label>
              <input
                type="text"
                value={formData.location.city}
                onChange={(e) => updateFormData({
                  location: { ...formData.location, city: e.target.value }
                })}
                className={cn(
                  "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                  errors.city ? "border-red-500" : "border-gray-300"
                )}
                placeholder="Enter your city"
              />
              {errors.city && <p className="text-red-500 text-sm mt-1">{errors.city}</p>}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Insurance (Select all that apply)
              </label>
              <div className="space-y-6">
                <div>
                  <label className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      checked={formData.insurance.life}
                      onChange={(e) => updateFormData({
                        insurance: { ...formData.insurance, life: e.target.checked }
                      })}
                      className="mr-2 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <span className="text-sm">Life Insurance</span>
                  </label>
                  
                  {formData.insurance.life && (
                    <div className="ml-6">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Life Insurance Claim Limit (₹) *
                      </label>
                      <input
                        type="number"
                        value={formData.insuranceCoverage.lifeClaimLimit || ''}
                        onChange={(e) => updateFormData({
                          insuranceCoverage: {
                            ...formData.insuranceCoverage,
                            lifeClaimLimit: parseInt(e.target.value) || 0
                          }
                        })}
                        placeholder="Enter life insurance claim limit"
                        className={cn(
                          "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                          errors.lifeClaimLimit ? "border-red-500" : "border-gray-300"
                        )}
                      />
                      {errors.lifeClaimLimit && <p className="text-red-500 text-sm mt-1">{errors.lifeClaimLimit}</p>}
                    </div>
                  )}
                </div>

                <div>
                  <label className="flex items-center mb-3">
                    <input
                      type="checkbox"
                      checked={formData.insurance.health}
                      onChange={(e) => updateFormData({
                        insurance: { ...formData.insurance, health: e.target.checked }
                      })}
                      className="mr-2 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <span className="text-sm">Health Insurance</span>
                  </label>

                  {formData.insurance.health && (
                    <div className="ml-6">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Health Insurance Claim Limit (₹) *
                      </label>
                      <input
                        type="number"
                        value={formData.insuranceCoverage.healthClaimLimit || ''}
                        onChange={(e) => updateFormData({
                          insuranceCoverage: {
                            ...formData.insuranceCoverage,
                            healthClaimLimit: parseInt(e.target.value) || 0
                          }
                        })}
                        placeholder="Enter health insurance claim limit"
                        className={cn(
                          "w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                          errors.healthClaimLimit ? "border-red-500" : "border-gray-300"
                        )}
                      />
                      {errors.healthClaimLimit && <p className="text-red-500 text-sm mt-1">{errors.healthClaimLimit}</p>}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
          <p className="text-gray-600">Help us personalize your financial planning experience</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {STEPS.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStep;
              const isCompleted = index < currentStep;

              return (
                <div key={step.id} className="flex flex-col items-center">
                  <div
                    className={cn(
                      "w-10 h-10 rounded-full flex items-center justify-center border-2 mb-2",
                      isActive
                        ? "bg-blue-600 border-blue-600 text-white"
                        : isCompleted
                        ? "bg-green-600 border-green-600 text-white"
                        : "border-gray-300 text-gray-400"
                    )}
                  >
                    {isCompleted ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span
                    className={cn(
                      "text-xs text-center max-w-20",
                      isActive ? "text-blue-600 font-medium" : "text-gray-500"
                    )}
                  >
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-xl shadow-xl p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {STEPS[currentStep].title}
            </h2>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
              />
            </div>
          </div>

          {renderStep()}

          {errors.submit && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{errors.submit}</p>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className={cn(
                "px-6 py-2 rounded-lg font-medium transition-colors",
                currentStep === 0
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              )}
            >
              Previous
            </button>

            <button
              onClick={handleNext}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center">
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Saving...
                </div>
              ) : currentStep === STEPS.length - 1 ? (
                'Complete Profile'
              ) : (
                'Next'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 