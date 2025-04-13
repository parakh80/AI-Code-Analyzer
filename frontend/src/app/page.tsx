'use client';

import { useState } from 'react';
import { submitCode } from '../services/api';
import { AnalysisMode } from '../types/api';
import dynamic from 'next/dynamic';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import AnalysisProgress from '../components/AnalysisProgress';
import type { Components } from 'react-markdown';

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function Home() {
  const [code, setCode] = useState('');
  const [mode, setMode] = useState<AnalysisMode>('full');
  const [language, setLanguage] = useState<string>('python');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code) {
      setError(`Please enter ${language} code to analyze`);
      return;
    }

    // Basic validation based on selected language
    let isValidCode = false;
    if (language === 'python') {
      // Check if it looks like Python code
      isValidCode = /^(?:def\s+|class\s+|import\s+|from\s+|#|print\s*\(|if\s+|for\s+|while\s+)/m.test(code);
      if (!isValidCode) {
        setError('This appears to be plain text, not Python code. Please enter valid Python code.');
        return;
      }
    } else if (language === 'javascript') {
      // Check if it looks like JavaScript code
      isValidCode = /^(?:function\s+|class\s+|import\s+|export\s+|\/\/|\/\*|\*\/|console\.|let\s+|const\s+|var\s+|if\s*\(|for\s*\()/m.test(code);
      if (!isValidCode) {
        setError('This appears to be plain text, not JavaScript code. Please enter valid JavaScript code.');
        return;
      }
    }

    setError(null);
    setStatus('processing');
    setResults(null);

    try {
      console.log(`Submitting ${language} code for analysis...`);
      const response = await submitCode(code, mode, language);
      console.log('Analysis started with ID:', response.analysis_id);
      setAnalysisId(response.analysis_id);
    } catch (error) {
      console.error('Error starting analysis:', error);
      handleAnalysisError(error instanceof Error ? error.message : 'Failed to start analysis');
    }
  };

  const handleAnalysisComplete = (results: any) => {
    console.log('Analysis completed with results:', results);
    // Set results directly instead of accessing results.results
    setResults(results);
    setStatus('completed');
  };

  const handleAnalysisError = (errorMessage: string) => {
    console.error('Analysis error:', errorMessage);
    setError(errorMessage);
    setStatus('failed');
    setAnalysisId(null); // Clear the analysis ID on error
  };

  const formatAnalysisResults = (results: any): string => {
    if (!results) {
      console.log('No results to format');
      return '';
    }

    console.log('Formatting results:', results);

    // Check if results has a nested 'results' property
    const analysisData = results.results || results;
    let markdownSections: string[] = []; // Store sections in an array

    // Add each analysis section with proper headers
    if (analysisData.correctness_analysis) {
      console.log('Adding correctness analysis');
      markdownSections.push(`## Correctness Analysis\n\n${analysisData.correctness_analysis}`);
    }

    if (analysisData.edge_cases) {
      console.log('Adding edge cases');
      markdownSections.push(`## Edge Cases\n\n${analysisData.edge_cases}`);
    }

    if (analysisData.semantic_analysis) {
      console.log('Adding semantic analysis');
      markdownSections.push(`## Semantic Analysis\n\n${analysisData.semantic_analysis}`);
    }

    if (analysisData.test_cases) {
      console.log('Adding test cases');
      // Ensure test cases are treated as code blocks if not already formatted
      const testCasesContent = analysisData.test_cases.trim().startsWith('```')
        ? analysisData.test_cases
        : `\`\`\`${language}\n${analysisData.test_cases}\n\`\`\``; // Add language hint
      markdownSections.push(`## Test Cases\n\n${testCasesContent}`);
    }

    // Join the sections with a Markdown horizontal rule
    const finalMarkdown = markdownSections.join('\n\n---\n\n'); // Use --- for horizontal rule

    console.log('Final markdown:', finalMarkdown);
    return finalMarkdown;
  };

  return (
    <main className="min-h-screen p-3 md:p-4">
      <div className="max-w-7xl mx-auto space-y-4">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">AI Code Analysis</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Code Editor Section */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-3 md:p-4">
            <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-2">Code Editor</h2>
            <div className="mb-2 grid grid-cols-2 gap-2">
              <div>
                <label htmlFor="language-select" className="block text-sm font-medium text-gray-700 mb-1">
                  Language
                </label>
                <select
                  id="language-select"
                  value={language}
                  onChange={(e) => {
                    const newLanguage = e.target.value;
                    setLanguage(newLanguage);
                    // Update Monaco Editor language
                    if (newLanguage === 'javascript') {
                      // Clear any previous validation errors when switching languages
                      setError(null);
                    }
                  }}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-sm"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>
              <div>
                <label htmlFor="mode-select" className="block text-sm font-medium text-gray-700 mb-1">
                  Analysis Mode
                </label>
                <select
                  id="mode-select"
                  value={mode}
                  onChange={(e) => setMode(e.target.value as AnalysisMode)}
                  className="w-full px-2 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-sm"
                >
                  <option value="full">Full Analysis</option>
                  <option value="quick">Quick Analysis</option>
                  <option value="deep">Deep Analysis</option>
                </select>
              </div>
            </div>
            <div className="h-[300px] border border-gray-300 rounded-lg overflow-hidden">
              <MonacoEditor
                height="100%"
                language={language}
                value={code}
                onChange={(value) => setCode(value || '')}
                theme="vs-light"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  readOnly: false,
                }}
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={status === 'processing' || !code}
              className="mt-3 w-full px-3 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              {status === 'processing' ? 'Analyzing...' : 'Analyze Code'}
            </button>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-3 md:p-4">
            <h2 className="text-lg md:text-xl font-semibold text-gray-900 mb-2">
              {status === 'processing' ? 'Analysis Progress' :
                status === 'completed' ? 'Analysis Complete' :
                  'Analysis Results'}
            </h2>

            {status === 'processing' && analysisId && (
              <AnalysisProgress
                analysisId={analysisId}
                onComplete={handleAnalysisComplete}
                onError={handleAnalysisError}
              />
            )}

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">{error}</p>
              </div>
            )}

{results && (
              // Apply prose styles for overall typography
              <div className="prose prose-sm max-w-none overflow-auto max-h-[80vh]">
                <ReactMarkdown
                  components={{
                    // Customize H2 rendering for section titles
                    h2: ({node, ...props}) => (
                      <h2
                        className="mt-6 mb-2 text-lg font-semibold border-b border-gray-200 pb-1" // Add top margin, bottom margin, border
                        {...props}
                      />
                    ),
                    // Customize HR rendering for section separators
                    hr: ({node, ...props}) => (
                      <hr className="my-6 border-gray-300" {...props} /> // Add vertical margin
                    ),
                    // Customize code block rendering (existing logic)
                    code: (({
                      node,
                      className,
                      children,
                      style: _ignoredStyle,
                      ref: _ignoredRef,
                      ...props
                    }) => {
                      const match = /language-(\w+)/.exec(className || '');
                      if (match) {
                        return (
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            customStyle={{
                              margin: '0', // Remove default margin from highlighter
                              padding: '1rem',
                              backgroundColor: '#1e1e1e',
                              borderRadius: '0.5rem',
                            }}
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        );
                      }
                      // Fallback for inline code
                      return (
                        <code className="px-1 py-0.5 bg-gray-100 rounded text-sm" {...props}>
                          {children}
                        </code>
                      );
                    }) as Components['code'],
                    // Optional: Customize paragraph styling if needed
                    // p: ({node, ...props}) => <p className="mb-3" {...props} />,
                  }}
                >
                  {formatAnalysisResults(results)}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
