import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

export type UserRole = 'SUPER_ADMIN' | 'INSTITUTION_ADMIN' | 'HOD' | 'FACULTY' | 'STUDENT';

export interface User {
  id?: number;
  email: string;
  full_name: string;
  role: UserRole;
  institution_id?: number;
  department_id?: number;
  student_id?: number | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isSuperAdmin: boolean;
  isFaculty: boolean;
  isHod: boolean;
  isStudent: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(() => {
    const email = localStorage.getItem('user_email');
    const full_name = localStorage.getItem('user_name');
    const role = localStorage.getItem('user_role') as UserRole | null;
    if (email && full_name && role) {
      return { email, full_name, role };
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const res = await api.get('/auth/me');
        setUser(res.data);
      } catch (err) {
        logout();
      } finally {
        setIsLoading(false);
      }
    };
    fetchUser();
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await api.post('/auth/login-json', { email, password });
    const { access_token, role, full_name, email: userEmail } = res.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user_role', role);
    localStorage.setItem('user_name', full_name);
    localStorage.setItem('user_email', userEmail);

    setToken(access_token);
    setUser({ email: userEmail, full_name, role });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    setToken(null);
    setUser(null);
  };

  const role = user?.role || null;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
        isSuperAdmin: role === 'SUPER_ADMIN',
        isFaculty: role === 'FACULTY' || role === 'HOD' || role === 'SUPER_ADMIN',
        isHod: role === 'HOD' || role === 'SUPER_ADMIN',
        isStudent: role === 'STUDENT',
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
