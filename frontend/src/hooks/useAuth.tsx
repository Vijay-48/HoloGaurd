import React, { createContext, useContext, useEffect, useState } from 'react';

interface AuthUser {
  id: string;
  username: string;
}

interface AuthContextType {
  user: AuthUser | null;
  session: { user: AuthUser } | null;
  token: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  signup: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    // Check for existing token on app load
    const savedToken = localStorage.getItem('haloguard_token');
    const savedUser = localStorage.getItem('haloguard_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const authUser = { id: username, username }; // Backend doesn't return user details in token endpoint
        
        setToken(data.access_token);
        setUser(authUser);
        localStorage.setItem('haloguard_token', data.access_token);
        localStorage.setItem('haloguard_user', JSON.stringify(authUser));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const signup = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        // After successful signup, automatically log in
        return await login(username, password);
      }
      return false;
    } catch (error) {
      console.error('Signup failed:', error);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('haloguard_token');
    localStorage.removeItem('haloguard_user');
  };

  const value: AuthContextType = {
    user,
    session: user ? { user } : null,
    token,
    login,
    signup,
    logout,
    isLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};