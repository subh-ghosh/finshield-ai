import axios, { AxiosError } from 'axios';
import { NetworkError, AuthenticationError, NotFoundError } from './errors/ApplicationError';
import { Logger } from './observability/logger';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Bypass-Tunnel-Reminder': 'true',
    ...(import.meta.env.VITE_API_KEY ? { 'X-API-Key': import.meta.env.VITE_API_KEY } : {})
  },
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    Logger.error('API Error', error.message, { url: error.config?.url, status: error.response?.status });
    
    if (!error.response) {
      throw new NetworkError();
    }
    
    switch (error.response.status) {
      case 401:
      case 403:
        throw new AuthenticationError();
      case 404:
        throw new NotFoundError();
      default:
        throw new NetworkError(error.message);
    }
  }
);
