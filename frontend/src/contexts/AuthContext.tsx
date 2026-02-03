import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load token and user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }

    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await axios.post(`${API_URL}/login`, formData);
    const { user: userData, token: tokenData } = response.data;

    setUser(userData);
    setToken(tokenData.access_token);

    // Persist to localStorage
    localStorage.setItem('token', tokenData.access_token);
    localStorage.setItem('user', JSON.stringify(userData));

    // Set default axios header
    axios.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`;
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    fullName?: string
  ) => {
    const response = await axios.post(`${API_URL}/register`, {
      username,
      email,
      password,
      full_name: fullName,
    });

    const { user: userData, token: tokenData } = response.data;

    setUser(userData);
    setToken(tokenData.access_token);

    // Persist to localStorage
    localStorage.setItem('token', tokenData.access_token);
    localStorage.setItem('user', JSON.stringify(userData));

    // Set default axios header
    axios.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user && !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
