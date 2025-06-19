export interface CredentialsInfo {
  type: string;
  project_id: string;
  client_email: string;
  client_id: string;
  auth_uri: string;
  token_uri: string;
  universe_domain: string;
  file_size: number;
  last_modified: string;
}

export interface EvaluationSession {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_candidates: number;
  processed_candidates: number;
  accepted_count: number;
  rejected_count: number;
  error_count: number;
  current_batch: number;
  total_batches: number;
  progress_percentage: number;
  created_at: string;
  completed_at?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface CandidateResult {
  outcome: 'Accepted' | 'Rejected' | 'Error';
  score: number;
  rationale: string;
  timestamp: string;
  email: string;
  name: string;
  gender?: string;
  date_of_birth?: string;
  marital_status?: string;
  religion?: string;
  phone_number?: string;
  residential_address?: string;
  current_employment?: string;
  employment_category?: string;
  company_address?: string;
  university_attended?: string;
  undergraduate_degree_type?: string;
  undergraduate_programme?: string;
  undergraduate_class?: string;
  undergraduate_completion_date?: string;
  postgraduate_degree_type?: string;
  postgraduate_programme?: string;
  postgraduate_class?: string;
  postgraduate_completion_date?: string;
  education_qualifications?: string;
  professional_qualifications?: string;
  career_interests?: string;
  msa_interests?: string;
  previous_applications?: string;
  candidate_essay: string;
  cv_url: string;
  video_url: string;
  cv_text: string;
  video_transcript: string;
  processing_errors: string[];
  evaluation_timestamp: string;
  files_processed_successfully: boolean;
  session_id: string;
}

export interface BatchProcessingStatus {
  batch_number: number;
  batch_size: number;
  total_processed: number;
  total_candidates: number;
  summary: {
    accepted: number;
    rejected: number;
    errors: number;
  };
  progress_percentage: number;
}

export interface EvaluationSummary {
  total_processed: number;
  accepted: number;
  rejected: number;
  errors: number;
}

export interface EvaluationResults {
  status: string;
  message: string;
  results: CandidateResult[];
  summary: EvaluationSummary;
}

export interface AppState {
  credentials: {
    isConfigured: boolean;
    info: CredentialsInfo | null;
    loading: boolean;
  };
  criteria: {
    content: string;
    loading: boolean;
  };
  evaluation: {
    results: CandidateResult[];
    summary: EvaluationSummary | null;
    loading: boolean;
  };
}
