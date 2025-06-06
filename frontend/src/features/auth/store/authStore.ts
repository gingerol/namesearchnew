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
  isInitialized: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { name: string; email: string; password: string }) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<string | null>;
  resetPassword: (email: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerificationEmail: (email: string) => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      isInitialized: false,
      error: null,
      
      initializeAuth: async () => {
        try {
          const { accessToken, refreshToken } = get();
          
          // If we have tokens, verify them
          if (accessToken && refreshToken) {
            try {
              // Try to refresh the token to verify it
              await get().refreshAccessToken();
            } catch (error) {
              console.warn('Token refresh failed, clearing auth state');
              // If refresh fails, clear the auth state but don't throw
              set({
                user: null,
                accessToken: null,
                refreshToken: null,
                isAuthenticated: false,
                isLoading: false,
                isInitialized: true,
                error: null,
              });
              return;
            }
          }
          
          set({ 
            isLoading: false, 
            isInitialized: true,
            // Only set isAuthenticated to true if we have a valid token
            isAuthenticated: !!accessToken
          });
        } catch (error) {
          console.error('Error initializing auth:', error);
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true,
            error: 'Failed to initialize authentication',
          });
        }
      },

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

// Function to initialize auth service and state
const initializeAuthService = () => {
  if (typeof window === 'undefined') return;
  
  // Initialize auth service
  const getAccessToken = () => useAuthStore.getState().accessToken;
  const onUnauthenticated = () => useAuthStore.getState().logout();
  
  // Import and initialize auth service
  import('../api/authApi').then(({ initAuthService }) => {
    initAuthService(getAccessToken, onUnauthenticated);
    
    // Initialize auth state after auth service is ready
    const { initializeAuth } = useAuthStore.getState();
    initializeAuth().catch(console.error);
  });
  
  // Set up storage event listener to sync auth state across tabs
  const handleStorageChange = (e: StorageEvent) => {
    if (e.key === 'auth-storage' && e.newValue) {
      try {
        const storedState = JSON.parse(e.newValue);
        if (storedState.state) {
          useAuthStore.setState(storedState.state);
        }
      } catch (error) {
        console.error('Error syncing auth state:', error);
      }
    }
  };
  
  // Add storage event listener
  window.addEventListener('storage', handleStorageChange);
  
  // Return cleanup function
  return () => {
    window.removeEventListener('storage', handleStorageChange);
  };
};

// Initialize auth service when the store is created
if (typeof window !== 'undefined') {
  const cleanup = initializeAuthService();
  
  // Register cleanup for hot module replacement
  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      cleanup?.();
    });
  }
}
