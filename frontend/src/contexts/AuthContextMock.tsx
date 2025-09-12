import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthContextType, RegisterData } from '../types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

// Mock user for demo purposes
const mockUser: User = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  budget: 2000,
  created_at: '2024-03-01'
};

export const AuthProviderMock: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Simulate being logged in for demo
  useEffect(() => {
    const timer = setTimeout(() => {
      setUser(mockUser);
      setToken('mock-token');
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setUser(mockUser);
    setToken('mock-token');
    setLoading(false);
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    const newUser = {
      ...mockUser,
      username: userData.username,
      email: userData.email,
      full_name: userData.full_name || userData.username,
      budget: userData.budget || 2000
    };
    setUser(newUser);
    setToken('mock-token');
    setLoading(false);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};