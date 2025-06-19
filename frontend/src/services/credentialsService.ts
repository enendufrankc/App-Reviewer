import api from './api';

export const credentialsService = {
  // GET /credentials
  getCredentialsInfo: () => api.get('/credentials'),
  
  // POST /credentials/upload
  uploadCredentials: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/credentials/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // POST /credentials/validate
  validateCredentials: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/credentials/validate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // POST /credentials/test
  testCredentials: () => api.post('/credentials/test'),
  
  // DELETE /credentials
  deleteCredentials: () => api.delete('/credentials')
};