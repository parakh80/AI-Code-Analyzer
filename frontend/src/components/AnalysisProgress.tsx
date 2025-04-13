import { useState, useEffect, useRef } from 'react';
import { getAnalysisResults } from '../services/api';
import AnalysisProgressSteps from './AnalysisProgressSteps';

interface AnalysisProgressProps {
  analysisId: string;
  onComplete: (results: any) => void;
  onError: (error: string) => void;
}

const STEPS = ['submitting', 'correctness', 'edge_cases', 'semantic', 'test_cases'];
const TOTAL_STEPS = STEPS.length;
// --- Configuration ---
// Total duration for the visual animation (e.g., 25 seconds)
const ANIMATION_DURATION_MS = 25000;
// How often to update the progress bar (e.g., every 50ms)
const UPDATE_INTERVAL_MS = 50;
// --- End Configuration ---

export default function AnalysisProgress({ analysisId, onComplete, onError }: AnalysisProgressProps) {
  const [status, setStatus] = useState<'processing' | 'fetching' | 'completed' | 'failed'>('processing');
  const [currentStep, setCurrentStep] = useState(STEPS[0]);
  const [progress, setProgress] = useState(0); // Start at 0
  const animationIntervalRef = useRef<NodeJS.Timeout | null>(null); // Ref to hold interval ID

  useEffect(() => {
    console.log('Starting decoupled progress animation for analysis:', analysisId);
    const startTime = Date.now();

    // Clear any existing interval before starting a new one
    if (animationIntervalRef.current) {
      clearInterval(animationIntervalRef.current);
    }

    animationIntervalRef.current = setInterval(() => {
      const elapsedTime = Date.now() - startTime;

      // --- Animation Phase ---
      if (elapsedTime < ANIMATION_DURATION_MS) {
        // Calculate visual progress (0% to 95% over the animation duration)
        const currentVisualProgress = Math.min(95, (elapsedTime / ANIMATION_DURATION_MS) * 95);
        setProgress(currentVisualProgress);

        // Determine which step should be visually active based on time
        // Each step gets an equal portion of the animation time
        const timePerStep = ANIMATION_DURATION_MS / TOTAL_STEPS;
        const currentVisualStepIndex = Math.min(TOTAL_STEPS - 1, Math.floor(elapsedTime / timePerStep));

        // Update the current step state if it has changed visually
        if (STEPS[currentVisualStepIndex] !== currentStep) {
          setCurrentStep(STEPS[currentVisualStepIndex]);
        }
      }
      // --- Animation Complete - Fetch Results ---
      else {
        // Ensure interval is cleared only once
        if (animationIntervalRef.current) {
          clearInterval(animationIntervalRef.current);
          animationIntervalRef.current = null; // Mark as cleared
        }

        // Set final pre-fetching state
        setProgress(95);
        setCurrentStep(STEPS[TOTAL_STEPS - 1]); // Ensure last step is visually current
        setStatus('fetching');

        // Now, actually fetch the results
        getAnalysisResults(analysisId)
          .then(results => {
            setProgress(100); // Set to 100% on success
            setStatus('completed');
            onComplete(results?.results || results);
          })
          .catch(error => {
            console.error('Error fetching results:', error);
            setStatus('failed'); // Set status to failed on error
            // Keep progress at 95 or reset? Let's keep it at 95 to indicate it finished fetching but failed.
            // setProgress(0); // Optionally reset progress on failure
            onError(error instanceof Error ? error.message : 'Failed to fetch results');
          });
      }
    }, UPDATE_INTERVAL_MS);

    // Cleanup function to clear interval if component unmounts during animation
    return () => {
      if (animationIntervalRef.current) {
        clearInterval(animationIntervalRef.current);
      }
    };
    // Rerun effect only if analysisId changes
  }, [analysisId, onComplete, onError]); // Removed currentStep from dependencies

  // Determine the correct status message (remains the same)
  const getStatusMessage = () => {
    // ... (getStatusMessage function remains the same as previous version) ...
    if (status === 'failed') {
      return 'Analysis failed';
    }
    if (status === 'completed') {
      return 'Analysis complete!';
    }
    // If fetching and progress is high enough, show finalizing
    if (status === 'fetching' && progress >= 95) {
      return 'Finalizing analysis...';
    }
    // Otherwise, if processing or fetching (before finalizing), show analyzing
    if (status === 'processing' || status === 'fetching') {
      return 'Analyzing your code...';
    }
    return ''; // Default empty message
  };


  return (
    <div className="space-y-4">
      {/* AnalysisProgressSteps component doesn't need changes */}
      <AnalysisProgressSteps currentStep={currentStep} progress={progress} />

      <div className="text-center">
        <p className="text-sm text-gray-600">
          {getStatusMessage()}
        </p>
      </div>
    </div>
  );
}