import { useState, useEffect } from 'react';

interface AnalysisProgressStepsProps {
  currentStep: string;
  progress: number;
}

const steps = [
  { id: 'submitting', label: 'Submitting Code' },
  { id: 'correctness', label: 'Correctness Analysis' },
  { id: 'edge_cases', label: 'Edge Cases' },
  { id: 'semantic', label: 'Semantic Analysis' },
  { id: 'test_cases', label: 'Test Cases' }
];

export default function AnalysisProgressSteps({ currentStep, progress }: AnalysisProgressStepsProps) {
  // Find current step index
  const currentStepIndex = steps.findIndex(step => step.id === currentStep);
  
  return (
    <div className="w-full">
      <div className="relative">
        {/* Progress bar */}
        <div className="absolute top-4 left-0 w-full h-1 bg-gray-200">
          <div 
            className="h-full bg-primary-600 transition-all duration-500 ease-in-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Steps */}
        <div className="relative flex justify-between">
          {steps.map((step, index) => {
            // A step is completed only if the current step index is beyond this step
            const isCompleted = index < currentStepIndex || (progress === 100 && index === steps.length - 1);
            // A step is current only if we're currently on this step and not completed yet
            const isCurrent = index === currentStepIndex;
            
            return (
              <div key={step.id} className="flex flex-col items-center">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center
                  transition-all duration-300 ease-in-out transform 
                  ${isCompleted ? 'bg-primary-600 text-white scale-105' : 
                    isCurrent ? 'bg-primary-100 text-primary-600 border-2 border-primary-600' : 
                    'bg-gray-200 text-gray-500'}
                `}>
                  {isCompleted ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                <span className={`
                  mt-2 text-xs font-medium
                  ${isCompleted || isCurrent ? 'text-primary-600' : 'text-gray-500'}
                `}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}