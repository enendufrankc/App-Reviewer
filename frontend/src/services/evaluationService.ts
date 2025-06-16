
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
  
  // POST /evaluate-candidates
  evaluateCandidates: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
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
  
  // GET /health
  healthCheck: () => api.get('/health')
};
