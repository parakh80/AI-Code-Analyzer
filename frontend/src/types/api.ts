export type AnalysisMode = 'full' | 'quick' | 'deep';

export interface CodeSubmission {
  code: string;
  language: string;
  mode: AnalysisMode;
}

export interface AnalysisResponse {
  analysis_type: string;
  code_context: {
    file_name: string;
    total_lines: number;
  };
  response: string;
}

export interface AnalysisResultItem {
  correctness_analysis: AnalysisResponse;
  edge_cases: AnalysisResponse;
  semantic_analysis: AnalysisResponse;
  test_cases: AnalysisResponse;
}

export type AnalysisStep = 'submitting' | 'correctness' | 'edge_cases' | 'semantic' | 'test_cases';

export interface AnalysisStatus {
  status: 'processing' | 'completed' | 'failed';
  current_step: AnalysisStep;
  progress: number;
  error?: string;
  submitted_at?: string;
}

export interface AnalysisResult {
  status: 'processing' | 'completed' | 'failed';
  error?: string;
  results?: AnalysisResultItem;
  current_step?: AnalysisStep;
  progress?: number;
  submitted_at?: string;
  completed_at?: string;
} 