import { useState, useCallback } from 'react';

export interface ApiError extends Error {
  name: string;
  message: string;
  status?: number;
  errors?: Record<string, string[]>;
  data?: any;
  response?: {
    data?: any;
    status?: number;
    statusText?: string;
    headers?: any;
    config?: any;
  };
  config?: {
    skipErrorToast?: boolean;
    [key: string]: any;
  };
  isAxiosError?: boolean;
  code?: string | number;
  stack?: string;
}

// Helper function to create a proper Error object
const createError = (message: string, name: string = 'ApiError'): ApiError => {
  const error = new Error(message) as ApiError;
  error.name = name;
  return error;
};

export function useApiError() {
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleError = useCallback((error: unknown): ApiError => {
    // If error is already an ApiError, return it
    if (error && typeof error === 'object' && 'name' in error && 'message' in error) {
      return error as ApiError;
    }

    console.error('API Error:', error);
    
    let errorMessage = 'An unexpected error occurred';
    let status: number | undefined;
    let errors: Record<string, string[]> = {};
    let data: any = undefined;

    if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      const err = error as Record<string, any>;
      
      // Handle Error objects
      if ('message' in err) {
        errorMessage = String(err.message);
      }
      
      // Handle Axios errors
      if ('isAxiosError' in err && err.response) {
        const response = err.response as Record<string, any>;
        status = response.status;
        
        if (response.data) {
          data = response.data;
          
          // Handle validation errors
          if (response.data.errors) {
            errors = response.data.errors;
            errorMessage = 'Validation failed';
          } else if (response.data.message) {
            errorMessage = response.data.message;
          } else if (typeof response.data === 'string') {
            errorMessage = response.data;
          }
        }
      }
    }

    const apiError: ApiError = createError(errorMessage, 'ApiError');
    apiError.status = status;
    apiError.data = data;
    
    if (Object.keys(errors).length > 0) {
      apiError.errors = errors;
    }
    
    if (error && typeof error === 'object') {
      const err = error as Record<string, any>;
      if ('config' in err) {
        apiError.config = err.config;
      }
      if ('response' in err) {
        apiError.response = err.response;
      }
      if ('isAxiosError' in err) {
        apiError.isAxiosError = true;
      }
    }

    setError(apiError);
    return apiError;
  }, []);

  const showError = useCallback((error: unknown, options: {
    errorMessage?: string;
  } = {}) => {
    const { errorMessage } = options;
    const apiError = handleError(error);
    
    // Don't handle 401 (Unauthorized) errors here as they're handled by the auth flow
    if (apiError.status === 401) {
      return apiError;
    }

    const message = errorMessage || apiError.message || 'An error occurred';
    
    // Log the error to console
    console.error('API Error:', {
      message,
      status: apiError.status,
      errors: apiError.errors,
      originalError: error
    });
    
    // Log validation errors if available
    if (apiError.errors && Object.keys(apiError.errors).length > 0) {
      const errorMessages = Object.entries(apiError.errors)
        .map(([field, messages]) => {
          const messageList = Array.isArray(messages) ? messages : [String(messages)];
          return `${field}: ${messageList.join(', ')}`;
        })
        .join('\n');
      
      console.error('Validation Error:', errorMessages);
    } else {
      console.error('Error:', message);
    }

    return apiError;
  }, [handleError]);
  
  // Helper function to handle API errors with a simple message
  const handleSimpleError = useCallback((error: unknown, defaultMessage: string = 'An error occurred'): string => {
    const apiError = handleError(error);
    return apiError.message || defaultMessage;
  }, [handleError]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const withErrorHandling = useCallback(async <T>(
    promise: Promise<T>,
    options: {
      onSuccess?: (data: T) => void;
      onError?: (error: ApiError) => void;
    } = {}
  ): Promise<{ data: T | null; error: ApiError | null }> => {
    const { onSuccess, onError } = options;

    setIsLoading(true);
    clearError();

    try {
      const data = await promise;
      
      if (onSuccess) {
        onSuccess(data);
      }

      return { data, error: null };
    } catch (error) {
      const apiError = handleError(error);

      if (onError) {
        onError(apiError);
      }

      return { data: null, error: apiError };
    } finally {
      setIsLoading(false);
    }
  }, [clearError, handleError]);

  return {
    error,
    isLoading,
    handleError,
    showError,
    handleSimpleError,
    clearError,
    withErrorHandling,
  } as const;
}

// Hook for common API error scenarios
export function useApiStatus() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [apiError, setApiError] = useState<ApiError | null>(null);
  
  const startLoading = useCallback(() => {
    setStatus('loading');
    setApiError(null);
  }, []);
  
  const setSuccess = useCallback(() => {
    setStatus('success');
  }, []);
  
  const setFailed = useCallback((err: unknown) => {
    setStatus('error');
    
    let errorMessage = 'An error occurred';
    if (err instanceof Error) {
      errorMessage = err.message;
    } else if (typeof err === 'string') {
      errorMessage = err;
    }
    
    const newError = createError(errorMessage, 'ApiError');
    setApiError(newError);
    return errorMessage;
  }, []);
  
  const reset = useCallback(() => {
    setStatus('idle');
    setApiError(null);
  }, []);
  
  return {
    status,
    isLoading: status === 'loading',
    isSuccess: status === 'success',
    isError: status === 'error',
    error: apiError,
    startLoading,
    setSuccess,
    setFailed,
    reset,
  } as const;
}
