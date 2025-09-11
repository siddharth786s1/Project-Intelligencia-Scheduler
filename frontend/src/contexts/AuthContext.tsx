import { createContext, ReactNode, useContext, useState, useEffect } from 'react';
import AuthService from '../services/authService';
import type { LoginCredentials, RegisterData } from '../services/authService';
import type { User } from '../types/api';

export interface AuthError {
  message: string;
  code?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;
  login: (credentials: LoginCredentials) => Promise<any>;
  register: (data: RegisterData) => Promise<any>;
  logout: () => void;
  clearError: () => void;
  hasRole: (role: string | string[]) => boolean;
  setCurrentInstitution: (institutionId: string) => void;
  currentInstitutionId: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<AuthError | null>(null);
  const [currentInstitutionId, setCurrentInstitutionId] = useState<string | null>(
    localStorage.getItem('currentInstitutionId')
  );
  
  const isAuthenticated = !!user;

  useEffect(() => {
    // Check if user is authenticated
    const checkAuth = async () => {
      try {
        if (AuthService.isAuthenticated()) {
          const userData = await AuthService.getCurrentUser();
          setUser(userData);
          
          // If institution ID is stored but not current, retrieve from localStorage
          if (!currentInstitutionId && userData.institution_id) {
            setCurrentInstitutionId(userData.institution_id);
          }
        }
      } catch (err: any) {
        console.error('Failed to verify authentication:', err);
        setError({ message: 'Session expired. Please login again.' });
        AuthService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [currentInstitutionId]);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const authResponse = await AuthService.login(credentials);
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
      
      // Set default institution if user has one
      if (userData.institution_id) {
        setCurrentInstitution(userData.institution_id);
      }
      
      return authResponse;
    } catch (err: any) {
      console.error('Login failed:', err);
      const errorMessage = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError({ message: errorMessage });
      throw err;
    } finally {
      setIsLoading(false);
    }
  };
  
  const register = async (data: RegisterData) => {
    setIsLoading(true);
    setError(null);
    try {
      const user = await AuthService.register(data);
      return user;
    } catch (err: any) {
      console.error('Registration failed:', err);
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError({ message: errorMessage });
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    AuthService.logout();
    setUser(null);
    setCurrentInstitutionId(null);
    localStorage.removeItem('currentInstitutionId');
  };
  
  const clearError = () => {
    setError(null);
  };
  
  const hasRole = (role: string | string[]) => {
    if (!user) return false;
    
    if (Array.isArray(role)) {
      return role.includes(user.role);
    }
    
    return user.role === role;
  };
  
  const setCurrentInstitution = (institutionId: string) => {
    setCurrentInstitutionId(institutionId);
    localStorage.setItem('currentInstitutionId', institutionId);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError,
        hasRole,
        setCurrentInstitution,
        currentInstitutionId,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
