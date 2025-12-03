import React, { createContext, useContext, useState, useEffect } from 'react';
import { tokenStorage } from '../utils/storage';

interface User {
  id: number;
  email: string;
  // Add other user fields from erd.json
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check for existing token on mount
    const token = tokenStorage.getAuthToken();
    if (token) {
      // TODO: Validate token and fetch user data
      // For now, just set a placeholder
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // TODO: Call login API
      // const response = await authService.login(email, password);
      // tokenStorage.setAuthToken(response.token);
      // setUser(response.user);
      console.log('Login called with:', email);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    tokenStorage.removeAuthToken();
    setUser(null);
  };

  const register = async (email: string, password: string) => {
    try {
      // TODO: Call register API
      console.log('Register called with:', email);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
