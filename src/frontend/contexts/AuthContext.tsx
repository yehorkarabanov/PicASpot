import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService, initAuth, hasToken, type User, type LoginCredentials, type RegisterCredentials } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  // true when a recently-registered or loaded user still needs to verify their email
  needsEmailVerification: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [needsEmailVerification, setNeedsEmailVerification] = useState(false);
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
        setNeedsEmailVerification(!Boolean((currentUser as any)?.is_verified));
      } else {
        setUser(null);
        setNeedsEmailVerification(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setNeedsEmailVerification(false);
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
        setNeedsEmailVerification(!Boolean(maybe.is_verified));
      } else {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        setNeedsEmailVerification(!Boolean((currentUser as any).is_verified));
      }
    } catch (err) {
      // If fetching user fails, clear user to be safe
      console.error('Failed to set user after login:', err);
      setUser(null);
      setNeedsEmailVerification(false);
      throw err;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    // call register; backend may return a token or just user data
    const resp = await authService.register(credentials);

    // If authService stored a token during register, fetch current user
    const tokenExists = await hasToken();
    if (tokenExists) {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      setNeedsEmailVerification(!Boolean((currentUser as any).is_verified));
      return;
    }

    // If server returned user data without token, set it directly
    const maybe = (resp as any)?.data;
    if (maybe && maybe.id) {
      const u: User = {
        id: maybe.id,
        username: maybe.username,
        email: maybe.email,
      };
      setUser(u);
      setNeedsEmailVerification(!Boolean(maybe.is_verified));
      return;
    }

    // As a fallback, try to login using provided identifier (username or email)
    const identifier = (credentials as any).username ?? (credentials as any).email;
    if (identifier) {
      await login({ username: identifier, password: credentials.password });
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setNeedsEmailVerification(false);
  };

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      setNeedsEmailVerification(!Boolean((currentUser as any).is_verified));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
      setNeedsEmailVerification(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        needsEmailVerification,
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
