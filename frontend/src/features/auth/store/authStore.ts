import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';
import { authApi } from '../api/authApi';

// Types
type User = {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  isVerified: boolean;
  createdAt: string;
};

type AuthState = {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { name: string; email: string; password: string }) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<string | null>;
  resetPassword: (email: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerificationEmail: (email: string) => Promise<void>;
  clearError: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const { accessToken, refreshToken } = await authApi.login(email, password);
          const { user } = jwtDecode<{ user: User }>(accessToken);
          
          set({
            user,
            accessToken,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register(userData);
          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Registration failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        // Call logout API in the background
        authApi.logout().catch(console.error);
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return null;

        try {
          const { accessToken } = await authApi.refreshToken(refreshToken);
          const { user } = jwtDecode<{ user: User }>(accessToken);
          
          set({
            accessToken,
            user,
            isAuthenticated: true,
          });
          
          return accessToken;
        } catch (error) {
          get().logout();
          return null;
        }
      },

      resetPassword: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.requestPasswordReset(email);
          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to send reset email',
            isLoading: false,
          });
          throw error;
        }
      },

      verifyEmail: async (token: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.verifyEmail(token);
          set((state) => ({
            user: state.user ? { ...state.user, isVerified: true } : null,
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Email verification failed',
            isLoading: false,
          });
          throw error;
        }
      },

      resendVerificationEmail: async (email: string) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.resendVerificationEmail(email);
          set({ isLoading: false });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to resend verification email',
            isLoading: false,
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Initialize auth state from storage on app load
if (typeof window !== 'undefined') {
  const { setState } = useAuthStore;
  const storedState = JSON.parse(localStorage.getItem('auth-storage') || '{}');
  
  if (storedState.state?.accessToken) {
    try {
      const { exp } = jwtDecode<{ exp: number }>(storedState.state.accessToken);
      
      // Clear expired token
      if (Date.now() >= exp * 1000) {
        setState({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      } else {
        // Initialize axios interceptors with the current token
        const getAccessToken = () => useAuthStore.getState().accessToken;
        const onUnauthenticated = () => useAuthStore.getState().logout();
        
        // Import and initialize auth service
        import('../api/authApi').then(({ initAuthService }) => {
          initAuthService(getAccessToken, onUnauthenticated);
        });
      }
    } catch (error) {
      console.error('Error initializing auth state:', error);
      // Clear invalid token
      setState({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
      });
    }
  }
}
