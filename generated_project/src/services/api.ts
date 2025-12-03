import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('Unauthorized. Please log in again.');
          break;
        case 403:
          console.error('Forbidden access.');
          break;
        case 404:
          console.error('Resource not found.');
          break;
        case 500:
          console.error('Internal server error.');
          break;
        default:
          console.error('An error occurred.');
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// Ensure API instance is exported for consistent use
