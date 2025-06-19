import api from './api';

export const evaluationService = {
  // GET /eligibility-criteria
  getCriteria: () => api.get('/eligibility-criteria'),
  
  // PUT /eligibility-criteria
  updateCriteria: (content: string) => 
    api.put('/eligibility-criteria', { content }),
  
  // POST /eligibility-criteria/validate
  validateCriteria: (content: string) => 
    api.post('/eligibility-criteria/validate', { content }),
  
  // POST /evaluate-candidates - Fixed to ensure user_email is always passed
  evaluateCandidates: (file: File, userEmail?: string, sessionName?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // CRITICAL FIX: Always require user_email
    if (!userEmail || userEmail.trim() === '') {
      throw new Error('User email is required for evaluation. Please log in and try again.');
    }
    
    formData.append('user_email', userEmail);
    
    if (sessionName) {
      formData.append('session_name', sessionName);
    } else {
      // Use a default session name with user info
      const defaultSessionName = `Evaluation Session ${new Date().toLocaleDateString()} - ${userEmail.split('@')[0]}`;
      formData.append('session_name', defaultSessionName);
    }
    
    console.log(`🔧 EvaluationService: Sending request with user_email: ${userEmail}`);
    
    return api.post('/evaluate-candidates', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 1)
        );
        console.log(`Upload Progress: ${percentCompleted}%`);
      }
    });
  },

  // Batch evaluation (fallback to regular evaluation for now)
  startBatchEvaluation: (file: File, userEmail: string, sessionName?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (userEmail) formData.append('user_email', userEmail);
    if (sessionName) formData.append('session_name', sessionName);
    
    return api.post('/evaluate-candidates', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
  },

  // TODO: These endpoints will be implemented with database integration
  getSessionStatus: (sessionId: string) => 
    Promise.resolve({ data: { status: 'not_implemented' } }),

  // Updated database endpoints
  getUserSessions: (userEmail: string) => 
    api.get(`/users/${encodeURIComponent(userEmail)}/sessions`),

  getSessionCandidates: (sessionId: string) => 
    api.get(`/sessions/${sessionId}/candidates`),

  getCandidateDetail: (candidateId: string) => 
    api.get(`/candidates/${candidateId}`),

  // New: Delete user sessions and evaluations
  deleteUserSessions: (userEmail: string) =>
    api.delete(`/users/${encodeURIComponent(userEmail)}/sessions`),

  deleteSession: (sessionId: string) =>
    api.delete(`/sessions/${sessionId}`),

  // User-specific criteria endpoints (now properly implemented)
  getUserCriteria: (userEmail: string) => 
    api.get(`/users/${encodeURIComponent(userEmail)}/criteria`),
  
  updateUserCriteria: (userEmail: string, content: string) => 
    api.put(`/users/${encodeURIComponent(userEmail)}/criteria`, { content }),

  getUserCriteriaHistory: (userEmail: string) => 
    Promise.resolve({ data: { history: [] } }),

  // User-specific credentials endpoints (fallback to general endpoints for now)
  uploadUserCredentials: (userEmail: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/credentials/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
  },

  getUserCredentialsInfo: (userEmail: string) => 
    api.get('/credentials'),
  
  // GET /health
  healthCheck: () => api.get('/health')
};