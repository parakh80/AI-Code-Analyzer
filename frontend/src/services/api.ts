import { AnalysisMode, CodeSubmission, AnalysisResult, AnalysisStatus } from '../types/api';

// Make sure this matches your backend URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Rate limiting configuration
const MAX_RETRIES = 5; // Increase retries
const INITIAL_RETRY_DELAY = 500; // 500ms - faster initial retry
const MAX_RETRY_DELAY = 5000; // 5 seconds

async function fetchWithRetry(url: string, options: RequestInit, retryCount = 0): Promise<Response> {
  try {
    console.log(`Attempting fetch to ${url} (attempt ${retryCount + 1}/${MAX_RETRIES + 1})`);
    
    // Create fetch options with timeout handling
    const fetchOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'test_key',
      },
      mode: 'cors' as RequestMode,
    };
    
    // Create a timeout promise
    const timeoutPromise = new Promise<Response>((_, reject) => {
      setTimeout(() => {
        reject(new Error('Request timeout: The server took too long to respond'));
      }, 180000); //  3 minutes timeout
    });
    
    // Race between fetch and timeout
    const response = await Promise.race([
      fetch(url, fetchOptions),
      timeoutPromise
    ]);

    // Log response details for debugging
    console.log(`Response status: ${response.status}`);
    
    // If we get a 429 (Too Many Requests), retry with exponential backoff
    if (response.status === 429 && retryCount < MAX_RETRIES) {
      const delay = Math.min(
        INITIAL_RETRY_DELAY * Math.pow(2, retryCount),
        MAX_RETRY_DELAY
      );
      console.log(`Rate limit hit, retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retryCount + 1);
    }

    // If response is not ok and not a rate limit, throw error
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorData.detail || response.statusText}`
      );
    }
    
    return response;
  } catch (error) {
    console.error(`Fetch error (attempt ${retryCount + 1}):`, error);
    
    // Check if it's a network error (server down or unreachable)
    const isNetworkError = error instanceof TypeError || 
      (error instanceof Error && (
        error.message === 'Failed to fetch' || 
        error.message.includes('NetworkError')
      ));
    
    // Check if it's a timeout
    const isTimeout = error instanceof Error && 
      error.message.includes('timeout');
    
    // Retry for network errors, timeouts, and other retryable errors
    if ((isNetworkError || isTimeout) && retryCount < MAX_RETRIES) {
      const delay = Math.min(
        INITIAL_RETRY_DELAY * Math.pow(2, retryCount),
        MAX_RETRY_DELAY
      );
      console.log(`Request failed (${isTimeout ? 'timeout' : 'network error'}), retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retryCount + 1);
    }
    
    // If we've exhausted retries or it's another type of error
    if (isNetworkError) {
      throw new Error(`Cannot connect to the analysis server. Is the backend running? (${API_BASE_URL})`);
    } else if (isTimeout) {
      throw new Error(`Request timeout. The server took too long to respond. Ensure backend is not overwhelmed.`);
    }
    
    throw error;
  }
}



export async function submitCode(code: string, mode: AnalysisMode = 'full', language: string = 'python'): Promise<{ analysis_id: string }> {
  console.log('Starting code analysis...', { mode, language, codeLength: code.length });
  
  // Basic validation to check if the content might be code
  if (!code || code.trim().length === 0) {
    throw new Error('Please enter some code to analyze');
  }
  
  // JavaScript-specific validation and preprocessing
  if (language === 'javascript' || language === 'js') {
    // Normalize language name
    language = 'javascript';
    
    // Basic JavaScript syntax check before sending to backend
    try {
      // Simple check for basic syntax - will throw if syntax is invalid
      new Function(code);
      console.log('JavaScript syntax validation passed');
    } catch (error) {
      // Type assertion to access error properties safely
      const syntaxError = error as Error;
      console.error('JavaScript syntax validation failed:', syntaxError);
      throw new Error(`JavaScript syntax error: ${syntaxError.message}`);
    }
  }
  
  // NOTE: JavaScript code follows the same analysis workflow as Python:
  // 1. Frontend submits code to backend API
  // 2. Backend processes the code through language-specific analyzers
  // 3. Both languages follow the same status checking and results retrieval flow
  // 4. The only difference is in how the backend processes each language internally
  
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: JSON.stringify({
        code,
        language,
        mode,
      } as CodeSubmission),
    });
    
    const data = await response.json();
    console.log('Analysis started successfully:', data);
    return data;
  } catch (error) {
    console.error('Error in submitCode:', error);
    

    
    // Handle 400 Bad Request errors (likely invalid code format)
    if (error instanceof Error && 
        error.message.includes('status: 400')) {
      throw new Error(`Invalid code format. Please submit valid ${language} code for analysis.`);
    }
    
    throw error;
  }
}

export async function getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
  console.log('Checking analysis status for ID:', analysisId);
  
  
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/status/${analysisId}`, {
      method: 'GET',
    });
    
    const data = await response.json();
    console.log('Current analysis status:', data);
    return data;
  } catch (error) {
    console.error('Error in getAnalysisStatus:', error);
    throw error;
  }
}

export async function getAnalysisResults(analysisId: string, retryCount = 0): Promise<AnalysisResult> {
  console.log('Fetching analysis results for ID:', analysisId);
  

  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/results/${analysisId}`, {
      method: 'GET',
    });
    
    const data = await response.json();
    console.log('Analysis results:', data);
    return data;
  } catch (error) {
    console.error('Error in getAnalysisResults:', error);
    
  
    
    // Handle 400 Bad Request errors with more detailed information
    if (error instanceof Error && error.message.includes('status: 400')) {
      // Extract the actual error message from the API if possible
      const detailMatch = error.message.match(/message: (.*?)$/);
      const detailMessage = detailMatch ? detailMatch[1] : '';
      
      if (detailMessage.includes('Analysis not completed')) {
        // Instead of throwing an error, retry with exponential backoff
        if (retryCount < 5) {  // Limit to 5 retries
          console.log(`Analysis still in progress, retrying after delay... (attempt ${retryCount + 1}/5)`);
          // Wait longer between each retry (1s, 2s, 4s, 8s, 16s)
          const delay = 1000 * Math.pow(2, retryCount);
          await new Promise(resolve => setTimeout(resolve, delay));
          return getAnalysisResults(analysisId, retryCount + 1);
        } else {
          console.warn('Max retries reached while waiting for analysis to complete');
          throw new Error('Analysis is taking longer than expected. Please check back later or try again.');
        }
      } else if (detailMessage.includes('syntax error') || detailMessage.includes('invalid syntax')) {
        throw new Error('Analysis failed due to syntax errors in the submitted code.');
      } else {
        throw new Error('Analysis failed. The submitted code may have errors or could not be analyzed properly.');
      }
    }
    
    throw error;
  }
}