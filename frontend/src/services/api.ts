import axios from 'axios';

// Get API URL from environment or use default
const getApiUrl = () => {
  // For production, use the backend service URL from Railway
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_URL || '/api/v1';
  }
  // For development
  return 'http://localhost:8000/api/v1';
};

const api = axios.create({
  baseURL: getApiUrl(),
  timeout: 300000, // 5 minutes for file processing
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export default api;