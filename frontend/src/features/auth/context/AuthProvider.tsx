import { createContext, useContext, useEffect, useMemo, useCallback, useState } from 'react';
import type { ReactNode, FC } from 'react';
import { useAuthStore } from '../store/authStore';
import { useApiError } from '../../../hooks/useApiError';
import { authApi } from '../api/authApi';
import { toast } from 'sonner';

interface AuthContextType {
  // Auth state
  isAuthenticated: boolean;
  isInitializing: boolean;
  isVerifying: boolean;
  user: any | null;
  
  // Auth methods
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { name: string; email: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  requestPasswordReset: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerificationEmail: (email: string) => Promise<void>;
  
  // Status
  isLoading: boolean;
  error: Error | null;
  clearError: () => void;
}

interface TokenResponse {
  accessToken: string;
  refreshToken: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const {
    user,
    accessToken,
    refreshToken: storedRefreshToken,
    isAuthenticated,
    isLoading,
    error: authError,
    logout: logoutFromStore,
    clearError: clearAuthError,
  } = useAuthStore();
  
  const { error: apiError, showError, clearError: clearApiError } = useApiError();
  
  const [isInitializing, setIsInitializing] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  
  // Clear any errors when the component unmounts
  useEffect(() => {
    return () => {
      clearAuthError();
      clearApiError();
    };
  }, [clearAuthError, clearApiError]);
  
  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (storedRefreshToken) {
          // Try to refresh the token if we have a refresh token
          await refreshToken();
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        // Don't show error to user during initialization
      } finally {
        setIsInitializing(false);
      }
    };
    
    initializeAuth();
  }, [storedRefreshToken]);
  
  // Handle token refresh
  const refreshToken = useCallback(async (): Promise<boolean> => {
    if (!storedRefreshToken) return false;
    
    try {
      const response = await authApi.refreshToken(storedRefreshToken) as TokenResponse;
      
      // Update auth store with new tokens
      useAuthStore.setState({
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        isAuthenticated: true,
      });
      
      return true;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Call logout directly instead of using the function to avoid circular dependency
      try {
        if (accessToken) {
          await authApi.logout();
        }
      } catch (logoutError) {
        console.error('Error during logout after token refresh failed:', logoutError);
      } finally {
        logoutFromStore();
      }
      return false;
    }
  }, [storedRefreshToken, accessToken, logoutFromStore]);
  
  // Login handler
  const login = async (email: string, password: string) => {
    try {
      const { accessToken, refreshToken } = await authApi.login(email, password);
      
      // Get user data from the token
      const userData = JSON.parse(atob(accessToken.split('.')[1]));
      
      useAuthStore.setState({
        user: userData,
        accessToken,
        refreshToken,
        isAuthenticated: true,
      });
      
      toast.success('Successfully logged in');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to log in. Please check your credentials.' });
      throw error;
    }
  };
  
  // Register handler
  const register = async (userData: { name: string; email: string; password: string }) => {
    try {
      await authApi.register(userData);
      toast.success('Registration successful! Please check your email to verify your account.');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to register. Please try again.' });
      throw error;
    }
  };
  

  
  // Password reset request handler
  const requestPasswordReset = async (email: string) => {
    try {
      await authApi.requestPasswordReset(email);
      toast.success('Password reset link sent to your email');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to send password reset email.' });
      throw error;
    }
  };
  
  // Reset password handler
  const resetPassword = async (token: string, newPassword: string) => {
    try {
      await authApi.resetPassword(token, newPassword);
      toast.success('Password reset successful. You can now log in with your new password.');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to reset password.' });
      throw error;
    }
  };
  
  // Verify email handler
  const verifyEmail = async (token: string) => {
    setIsVerifying(true);
    try {
      await authApi.verifyEmail(token);
      
      // Update user verification status
      if (user) {
        useAuthStore.setState({
          user: { ...user, isVerified: true },
        });
      }
      
      toast.success('Email verified successfully!');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to verify email.' });
      throw error;
    } finally {
      setIsVerifying(false);
    }
  };
  
  // Resend verification email handler
  const resendVerificationEmail = async (email: string) => {
    try {
      await authApi.resendVerificationEmail(email);
      toast.success('Verification email sent. Please check your inbox.');
    } catch (error) {
      showError(error, { errorMessage: 'Failed to resend verification email.' });
      throw error;
    }
  };
  
  // Logout handler
  const logout = useCallback(async () => {
    try {
      await logoutFromStore();
    } catch (error) {
      console.error('Logout error:', error);
    }
  }, [logoutFromStore]);

  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo((): AuthContextType => ({
    isAuthenticated,
    isInitializing,
    isVerifying,
    user,
    login,
    register,
    logout,
    refreshToken,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    resendVerificationEmail,
    isLoading,
    error: authError || apiError ? new Error(authError || apiError?.message || 'An error occurred') : null,
    clearError: () => {
      clearAuthError();
      clearApiError();
    },
  }), [
    isAuthenticated,
    isInitializing,
    isVerifying,
    user,
    login,
    register,
    logout,
    refreshToken,
    requestPasswordReset,
    resetPassword,
    verifyEmail,
    resendVerificationEmail,
    isLoading,
    authError,
    apiError,
    clearAuthError,
    clearApiError,
  ]);
  
  return (
    <AuthContext.Provider value={value}>
      {!isInitializing ? children : (
        <div className="flex h-screen w-full items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      )}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Higher-order component for class components
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  const WithAuth: React.FC<P> = (props) => {
    const auth = useAuth();
    return <Component {...props} auth={auth} />;
  };
  
  // Set a display name for the component for better debugging
  const displayName = Component.displayName || Component.name || 'Component';
  WithAuth.displayName = `withAuth(${displayName})`;
  
  return WithAuth;
};

export default AuthContext;
