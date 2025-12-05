import axios from 'axios';

/** Create axios instance with default settings */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,  // Base URL from Vite environment
  timeout: 10000,  // Default timeout
  headers: { 'Content-Type': 'application/json' }  // Default headers
});

/** Request interceptor to include auth token */
api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');  // Retrieve token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

/** Response interceptor for global error handling */
api.interceptors.response.use(response => response, error => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // Handle unauthorized error
        break;
      case 403:
        // Handle forbidden error
        break;
      case 404:
        // Handle not found error
        break;
      case 500:
        // Handle server error
        break;
      default:
        break;
    }
  }
  return Promise.reject(error);
});

export default api;  // Default export