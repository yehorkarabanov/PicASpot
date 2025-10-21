import * as SecureStore from 'expo-secure-store';
import api from './api';

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await api.post<AuthResponse>('/v1/auth/jwt/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    if (response.data.access_token) {
      await SecureStore.setItemAsync('access_token', response.data.access_token);
    }

    return response.data;
  },

  async register(credentials: RegisterCredentials): Promise<User> {
    const response = await api.post<User>('/v1/auth/register', credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/jwt/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await SecureStore.deleteItemAsync('access_token');
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/v1/users/me');
    return response.data;
  },

  async hasToken(): Promise<boolean> {
    const token = await SecureStore.getItemAsync('access_token');
    return !!token;
  },

  async getToken(): Promise<string | null> {
    return await SecureStore.getItemAsync('access_token');
  },
};

