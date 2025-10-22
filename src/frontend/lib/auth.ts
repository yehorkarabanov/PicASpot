import * as SecureStore from 'expo-secure-store';
import api from './api';

export interface User {
  id: string;
  username: string;
  email?: string;
  // backend returns these flags; keep optional to remain compatible
  is_superuser?: boolean;
  is_verified?: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginData {
  id: string;
  username: string;
  email: string;
  is_superuser: boolean;
  is_verified: boolean;
  token?: Token;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

const ACCESS_KEY = 'access_token';

function setAuthHeader(token?: string | null) {
  if (token) {
    api.defaults.headers = api.defaults.headers || {};
    api.defaults.headers.common = api.defaults.headers.common || {};
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    if (api.defaults.headers && api.defaults.headers.common) {
      delete api.defaults.headers.common['Authorization'];
    }
  }
}

async function saveToken(token: string) {
  await SecureStore.setItemAsync(ACCESS_KEY, token);
  setAuthHeader(token);
}

export const authService = {
  async initAuth(): Promise<void> {
    const token = await SecureStore.getItemAsync(ACCESS_KEY);
    if (token) setAuthHeader(token);
  },

  async login(credentials: LoginCredentials): Promise<ApiResponse<LoginData>> {
    const response = await api.post<ApiResponse<LoginData>>('/v1/auth/login', {
      username: credentials.username,
      password: credentials.password,
    });

    const access = response.data?.data?.token?.access_token;
    if (access) {
      await saveToken(access);
    }

    return response.data;
  },

  async register(
    credentials: RegisterCredentials
  ): Promise<ApiResponse<LoginData> | ApiResponse<User>> {
    // backend accepts only username, email and password
    const payload = {
      username: credentials.username,
      email: credentials.email,
      password: credentials.password,
    };

    const response = await api.post<ApiResponse<LoginData> | ApiResponse<User>>(
      '/v1/auth/register',
      payload
    );

    // Do NOT store access token on register (don't auto-login users after registering).
    // The backend may return a token, but for now we intentionally avoid saving it here.

    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/v1/auth/logout');
    } catch (error) {
    } finally {
      await SecureStore.deleteItemAsync(ACCESS_KEY);
      setAuthHeader(null);
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/v1/users/me');
    return response.data;
  },

  async hasToken(): Promise<boolean> {
    const token = await SecureStore.getItemAsync(ACCESS_KEY);
    return !!token;
  },
};

export const initAuth = authService.initAuth;
export const hasToken = authService.hasToken;
