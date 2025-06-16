import axios from 'axios';

// For production, API calls go through nginx proxy to /api
// For development, direct calls to backend
const getApiUrl = () => {
  if (import.meta.env.PROD) {
    return '/api/v1'; // Proxied through nginx
  }
  return 'http://localhost:8000/api/v1'; // Direct to backend in dev
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