import axios from 'axios';
import { tokenStorage } from '../utils/storage';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = tokenStorage.getAuthToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { status } = error.response;
    if (status === 401) {
      // Handle Unauthorized
    } else if (status === 403) {
      // Handle Forbidden
    } else if (status === 404) {
      // Handle Not Found
    } else if (status === 500) {
      // Handle Internal Server Error
    }
    return Promise.reject(error);
  }
);

export default api;