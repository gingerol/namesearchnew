import { useState, useCallback, useRef } from 'react';
import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { useAuth } from '@/features/auth/context/AuthProvider';
import type { ApiError } from './useApiError';

// Extend AxiosRequestConfig to include our custom options
interface ApiRequestConfig extends AxiosRequestConfig {
  requireAuth?: boolean;
  skipAuthRefresh?: boolean;
  skipErrorToast?: boolean;
}

// Extend AxiosResponse to include our custom properties
interface ApiResponse<T = any> extends Omit<AxiosResponse<T>, 'config'> {
  config: ApiRequestConfig;
}

// Extend AxiosError to include our custom properties
interface ApiRequestError<T = any> extends Omit<AxiosError<T>, 'response' | 'config'> {
  config: ApiRequestConfig;
  response?: ApiResponse<T>;
}

// Create axios instance with base config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

/**
 * Hook for making API requests with authentication and error handling
 */
export function useApi() {
  const { isAuthenticated, refreshToken, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<any>(null);
  
  // Keep track of ongoing refresh token request to prevent multiple simultaneous refreshes
  const refreshTokenPromise = useRef<Promise<boolean> | null>(null);
  
  // Handle API errors
  const handleError = useCallback(async (error: unknown, config: ApiRequestConfig = {}) => {
    const apiError = error as ApiRequestError;
    console.error('API Error:', apiError);
    
    // Don't show error toast if skipErrorToast is true
    if (!config.skipErrorToast && !(apiError.config?.skipErrorToast)) {
      // Show error toast or handle error UI here
      console.error('API Error:', apiError.message);
    }
    
    // Handle 401 Unauthorized errors
    if ((apiError.response?.status === 401) && !config.skipAuthRefresh) {
      // If we're not already trying to refresh the token, try to refresh it
      if (!refreshTokenPromise.current) {
        refreshTokenPromise.current = (async () => {
          try {
            const success = await refreshToken();
            if (!success) {
              // If refresh fails, log the user out
              await logout();
              return false;
            }
            return true;
          } finally {
            refreshTokenPromise.current = null;
          }
        })();
      }
      
      // Return the refresh token promise so the caller can retry the request
      return refreshTokenPromise.current;
    }
    
    // For other errors, reject with the error
    return Promise.reject(apiError);
  }, [refreshToken, logout]);
  
  // Generic request method that handles all HTTP methods
  const request = useCallback(async <T = any>(
    config: ApiRequestConfig
  ): Promise<T> => {
    const {
      requireAuth = true,
      skipAuthRefresh = false,
      ...requestConfig
    } = config;
    
    // Set loading state
    setIsLoading(true);
    setError(null);
    
    // Add auth header if required
    if (requireAuth && isAuthenticated) {
      requestConfig.headers = {
        ...requestConfig.headers,
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
      };
    }
    
    try {
      const response = await api.request<T>(requestConfig);
      setData(response.data);
      return response.data;
    } catch (error) {
      const apiError = error as ApiRequestError;
      setError(apiError);
      
      // Handle error and potentially refresh token
      const refreshResult = await handleError(apiError, { skipAuthRefresh });
      
      // If we got a new token, retry the original request
      if (refreshResult === true) {
        return request<T>(config);
      }
      
      // Otherwise, rethrow the error
      throw apiError;
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, handleError]);
  
  // Make a GET request
  const get = useCallback(async <T = any>(
    url: string, 
    config: ApiRequestConfig = {}
  ): Promise<T> => {
    return request<T>({ ...config, method: 'GET', url });
  }, [request]);
  
  // Make a POST request
  const post = useCallback(async <T = any>(
    url: string, 
    data?: any, 
    config: ApiRequestConfig = {}
  ): Promise<T> => {
    return request<T>({ ...config, method: 'POST', url, data });
  }, [request]);
  
  // Make a PUT request
  const put = useCallback(async <T = any>(
    url: string, 
    data?: any, 
    config: ApiRequestConfig = {}
  ): Promise<T> => {
    return request<T>({ ...config, method: 'PUT', url, data });
  }, [request]);
  
  // Make a PATCH request
  const patch = useCallback(async <T = any>(
    url: string, 
    data?: any, 
    config: ApiRequestConfig = {}
  ): Promise<T> => {
    return request<T>({ ...config, method: 'PATCH', url, data });
  }, [request]);
  
  // Make a DELETE request
  const del = useCallback(async <T = any>(
    url: string, 
    config: ApiRequestConfig = {}
  ): Promise<T> => {
    return request<T>({ ...config, method: 'DELETE', url });
  }, [request]);
  
  // Clear error state
  const clearError = useCallback(() => {
    setError(null);
  }, []);
  
  // Clear data state
  const clearData = useCallback(() => {
    setData(null);
  }, []);
  
  // Reset all state
  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setData(null);
  }, []);
  
  return {
    // Request methods
    request,
    get,
    post,
    put,
    patch,
    delete: del,
    
    // State
    data,
    isLoading,
    error,
    
    // Utilities
    clearError,
    clearData,
    reset,
  };
}

// Export the axios instance for direct use if needed
export { api };

// Helper function to create API hooks for specific endpoints
export function createApiHook<RequestData = any, ResponseData = any>(
  defaultConfig: ApiRequestConfig
) {
  return function useApiHook(
    config?: Partial<ApiRequestConfig>,
    deps: any[] = []
  ) {
    const [state, setState] = useState<{
      data: ResponseData | null;
      isLoading: boolean;
      error: ApiError | null;
    }>({
      data: null,
      isLoading: false,
      error: null,
    });
    
    const { request, reset } = useApi();
    
    const execute = useCallback(async (
      data?: RequestData,
      requestConfig?: Partial<ApiRequestConfig>
    ) => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      try {
        const mergedConfig = { ...defaultConfig, ...config, ...requestConfig };
        
        // If data is provided, use it in the request
        if (data) {
          if (mergedConfig.method?.toLowerCase() === 'get') {
            mergedConfig.params = { ...mergedConfig.params, ...data };
          } else {
            mergedConfig.data = data;
          }
        }
        
        const response = await request<ResponseData>(mergedConfig);
        setState({ data: response, isLoading: false, error: null });
        return response;
      } catch (error) {
        const apiError = error as ApiRequestError;
        const errorMessage = apiError.response?.data?.message || apiError.message;
        const errorStatus = apiError.response?.status;
        const errorData = apiError.response?.data;
        
        const errorObj: ApiError = {
          name: 'ApiError',
          message: errorMessage,
          status: errorStatus,
          data: errorData,
        };
        
        setState({
          data: null,
          isLoading: false,
          error: errorObj,
        });
        throw error;
      }
    }, [request, config, ...deps]);
    
    return {
      ...state,
      execute,
      reset: () => {
        reset();
        setState({ data: null, isLoading: false, error: null });
      },
    };
  };
}
