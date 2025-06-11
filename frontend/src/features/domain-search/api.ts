import axios, { type InternalAxiosRequestConfig } from 'axios';
import type { AxiosError } from 'axios';
import type { 
  DomainSearchResult, 
  WhoisData, 
  AdvancedDomainSearchRequestFE, 
  PaginatedFilteredDomainsResponseFE 
} from './types';
import { useAuthStore } from '@/features/auth/store/authStore';

// Create axios instance with default config (no credentials by default)
const apiClient = axios.create({
  baseURL: '/api/v1',  // Using relative URL since we're using Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Don't send credentials by default
});

// Add request interceptor to include auth token for authenticated requests
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig & { _retry?: boolean }) => {
  // Always allow these public endpoints without auth
  const publicEndpoints = [
    '/domains/search',
    '/domains/check',
    '/domains/suggestions',
    '/domains/whois',
    '/domains/analyze'
  ];

  const isPublic = publicEndpoints.some(endpoint => config.url?.startsWith(endpoint));
  
  // Skip adding auth header for public endpoints
  if (isPublic) {
    console.log('Skipping auth for public endpoint:', config.url);
    // Ensure credentials are not sent for public endpoints
    config.withCredentials = false;
    return config;
  }
  
  // For non-public endpoints, try to add auth token if available
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
    // Send credentials for authenticated endpoints
    config.withCredentials = true;
  }
  
  return config;
});

// Helper function to check if a URL is a public endpoint
const isPublicEndpoint = (url: string | undefined): boolean => {
  if (!url) return false;
  const publicEndpoints = [
    '/domains/search',
    '/domains/check',
    '/domains/suggestions',
    '/domains/whois',
    '/domains/analyze'
  ];
  return publicEndpoints.some(endpoint => url.includes(endpoint));
};

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const isPublic = isPublicEndpoint(originalRequest?.url);
    
    // For public endpoints, just reject the promise without redirecting
    if (isPublic) {
      return Promise.reject(error);
    }
    
    // Only attempt token refresh for authenticated endpoints
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token for authenticated endpoints
        const { refreshAccessToken } = useAuthStore.getState();
        const newAccessToken = await refreshAccessToken();
        
        if (newAccessToken) {
          // Update the authorization header and retry the request
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Only redirect to login for non-public endpoints
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // For other errors, just log and rethrow
    console.error('API Error:', error);
    
    // Handle 401 for non-public endpoints
    if (error.response?.status === 401 && !isPublic) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    
    // For public endpoints, just reject with the error
    return Promise.reject(error);
  }
);

export const domainSearchApi = {
  /**
   * Search for domains with AI-powered analysis and advanced filters
   */
  async searchDomains(params: { query: string } & Partial<AdvancedDomainSearchRequestFE>): Promise<PaginatedFilteredDomainsResponseFE> {
    try {
      const cleanParams: any = {};

      // Add query parameter - required by the backend but not part of AdvancedDomainSearchRequestFE
      if (params.query) {
        cleanParams.query = params.query;
      }

      // Make sure tlds is always present and not empty
      if (params.tlds && params.tlds.length > 0) {
        cleanParams.tlds = params.tlds;
      } else {
        cleanParams.tlds = ['com', 'io', 'co', 'ai']; // Default TLDs if none selected
      }

      // Iterate over remaining keys and add to cleanParams if defined
      for (const key in params) {
        // Skip query and tlds as we've already handled them
        if (key === 'query' || key === 'tlds') continue;
        
        if (Object.prototype.hasOwnProperty.call(params, key)) {
          const value = params[key as keyof typeof params];
          if (value !== undefined) {
            if (Array.isArray(value) && value.length === 0) {
              // Do not send empty arrays, backend might interpret differently than undefined
              continue;
            }
            cleanParams[key] = value;
          }
        }
      }

      // Ensure page and page_size are numbers if they are present, or rely on backend defaults by omitting them
      if (params.page !== undefined) {
        cleanParams.page = Number(params.page) || undefined; // Ensure it's a number or undefined
      }
      if (params.page_size !== undefined) {
        cleanParams.page_size = Number(params.page_size) || undefined; // Ensure it's a number or undefined
      }
      
      // Remove undefined explicitly after potential coercion if Number() resulted in NaN then undefined
      if (cleanParams.page === undefined) delete cleanParams.page;
      if (cleanParams.page_size === undefined) delete cleanParams.page_size;

      // Log the cleaned parameters for debugging
      console.log('Sending domain search parameters:', cleanParams);

      const response = await apiClient.post<PaginatedFilteredDomainsResponseFE>('/domains/search', cleanParams);
      return response.data;
    } catch (error) {
      console.error('Error searching domains:', error);
      // Consider re-throwing the original AxiosError for more detailed error handling upstream
      // or creating a custom error object with more context.
      if (axios.isAxiosError(error) && error.response) {
        // You can access error.response.data, error.response.status, etc.
        throw new Error(`API Error (${error.response.status}): ${error.response.data?.detail || error.message}`);
      }
      throw new Error('Failed to search domains. Please try again.');
    }
  },

  /**
   * Check domain availability
   */
  async checkAvailability(domain: string): Promise<boolean> {
    try {
      const response = await apiClient.get<{ is_available: boolean }>('/domains/check', {
        params: { domain }
      });
      return response.data.is_available;
    } catch (error) {
      console.error('Error checking domain availability:', error);
      throw new Error('Failed to check domain availability');
    }
  },

  /**
   * Get domain name suggestions
   */
  async getSuggestions(query: string, count: number = 5): Promise<string[]> {
    try {
      const response = await apiClient.get<{ suggestions: string[] }>('/domains/suggestions', {
        params: { query, count }
      });
      return response.data.suggestions || [];
    } catch (error) {
      console.error('Error getting domain suggestions:', error);
      return [];
    }
  },

  /**
   * Get domain analysis
   */
  async analyzeDomain(domain: string, options?: { signal?: AbortSignal }): Promise<DomainSearchResult> {
    try {
      const response = await apiClient.get<DomainSearchResult>(
        `/domains/analyze/${encodeURIComponent(domain)}`,
        { signal: options?.signal }
      );
      return response.data;
    } catch (error) {
      console.error('Error analyzing domain:', error);
      throw error;
    }
  },

  /**
   * Get WHOIS information for a domain
   */
  async whois(domain: string, options?: { signal?: AbortSignal }): Promise<WhoisData> {
    try {
      const response = await apiClient.post<Record<string, WhoisData>>(
        '/domains/whois/search',
        { domain_names: [domain] },
        { signal: options?.signal }
      );
      
      // Extract the result for the requested domain
      const result = response.data[domain];
      if (!result) {
        throw new Error('No WHOIS data found for domain');
      }
      
      return result;
    } catch (error) {
      console.error('Error fetching WHOIS data:', error);
      throw error;
    }
  },
};
