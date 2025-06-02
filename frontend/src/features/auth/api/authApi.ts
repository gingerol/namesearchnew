import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface LoginResponse {
  accessToken: string;
  refreshToken: string;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
}

export const authApi = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/auth/login`,
      { email, password },
      { withCredentials: true }
    );
    return response.data;
  },

  async register(userData: RegisterData): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/register`,
      userData,
      { withCredentials: true }
    );
  },

  async logout(): Promise<void> {
    try {
      await axios.post(
        `${API_BASE_URL}/auth/logout`,
        {},
        { withCredentials: true }
      );
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  async refreshToken(refreshToken: string): Promise<{ accessToken: string }> {
    const response = await axios.post<{ accessToken: string }>(
      `${API_BASE_URL}/auth/refresh-token`,
      { refreshToken },
      { withCredentials: true }
    );
    return response.data;
  },

  async requestPasswordReset(email: string): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/request-password-reset`,
      { email },
      { withCredentials: true }
    );
  },

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/reset-password`,
      { token, newPassword },
      { withCredentials: true }
    );
  },

  async verifyEmail(token: string): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/verify-email`,
      { token },
      { withCredentials: true }
    );
  },

  async resendVerificationEmail(email: string): Promise<void> {
    await axios.post(
      `${API_BASE_URL}/auth/resend-verification`,
      { email },
      { withCredentials: true }
    );
  },

  async getCurrentUser(): Promise<any> {
    const response = await axios.get(
      `${API_BASE_URL}/auth/me`,
      { withCredentials: true }
    );
    return response.data;
  }
};

// Set up request interceptor to add auth token
export const setupAxiosInterceptors = (getAccessToken: () => string | null, onUnauthenticated: () => void) => {
  axios.interceptors.request.use(
    (config) => {
      const token = getAccessToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      
      // If error is 401 and we haven't tried to refresh yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          // Try to refresh the token
          const refreshToken = localStorage.getItem('auth-storage')
            ? JSON.parse(localStorage.getItem('auth-storage') || '{}').state?.refreshToken
            : null;
          
          if (refreshToken) {
            const { accessToken } = await authApi.refreshToken(refreshToken);
            
            // Update the auth store
            const authStore = JSON.parse(localStorage.getItem('auth-storage') || '{}');
            localStorage.setItem(
              'auth-storage',
              JSON.stringify({
                ...authStore,
                state: {
                  ...authStore.state,
                  accessToken,
                },
              })
            );
            
            // Update the authorization header and retry the request
            originalRequest.headers.Authorization = `Bearer ${accessToken}`;
            return axios(originalRequest);
          }
        } catch (error) {
          console.error('Error refreshing token:', error);
          onUnauthenticated();
          return Promise.reject(error);
        }
      }
      
      return Promise.reject(error);
    }
  );
};

// Export a function to initialize the auth service
export const initAuthService = (getAccessToken: () => string | null, onUnauthenticated: () => void) => {
  setupAxiosInterceptors(getAccessToken, onUnauthenticated);
};
