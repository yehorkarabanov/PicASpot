import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import * as Localization from 'expo-localization';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'https://192.168.1.108/api';
console.log (`API URL: ${API_URL}`);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Falls back to UTC if timezone cannot be determined
    const timezone = Localization.getCalendars()[0]?.timeZone || 'UTC';
    config.headers['X-Timezone'] = timezone;

    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url} [Timezone: ${timezone}]`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, clear it
      await SecureStore.deleteItemAsync('access_token');
    }

    // Log detailed error info
    console.error('API Error:', {
      message: error.message,
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
    });

    return Promise.reject(error);
  }
);

export default api;
