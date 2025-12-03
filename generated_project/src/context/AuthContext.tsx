import React, { createContext, useContext, useState } from 'react';
import { tokenStorage } from '../utils/storage';

interface User {
  id: number;
  email: string;
  // additional fields from the user definition
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // Implement login logic
    // tokenStorage.setAuthToken(token);
    setUser({ id: 1, email }); // Placeholder user
  };

  const logout = () => {
    tokenStorage.removeAuthToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
