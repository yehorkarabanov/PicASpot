import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService, initAuth, hasToken, type User, type LoginCredentials, type RegisterCredentials } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        await initAuth();
      } catch (e) {
        console.warn('initAuth failed', e);
      }
      await checkAuth();
    };

    init();
  }, []);

  const checkAuth = async () => {
    try {
      const tokenExists = await hasToken();
      if (tokenExists) {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    // delegate to authService which will save token and set header
    const resp = await authService.login(credentials);

    // If the login response contained user fields, use them; otherwise fetch current user
    try {
      const maybe = (resp as any)?.data;
      if (maybe && maybe.id) {
        const u: User = {
          id: maybe.id,
          username: maybe.username,
          email: maybe.email,
        };
        setUser(u);
      } else {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      }
    } catch (err) {
      // If fetching user fails, clear user to be safe
      console.error('Failed to set user after login:', err);
      setUser(null);
      throw err;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    // Call register but do not auto-login or set user here.
    // The UI (register screen) will show that instructions were sent to the user.
    await authService.register(credentials);
    return;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
