import axios from 'axios';

// For Railway production, everything goes through the same domain
const getApiUrl = () => {
  // Check if we're in Railway production
  if (window.location.hostname.includes('railway.app')) {
    return '/api/v1';
  }
  
  // For local development
  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api/v1';
  }
  
  // For other production environments
  return '/api/v1';
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