import axios from 'axios';
import type { AxiosError } from 'axios';
import type { DomainSearchParams, DomainSearchResult, DomainSearchResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor for auth if needed
apiClient.interceptors.request.use((config) => {
  // Add auth token if available
  // const token = localStorage.getItem('auth_token');
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error);
    throw error;
  }
);

export const domainSearchApi = {
  /**
   * Search for domains with AI-powered analysis
   */
  async searchDomains(params: DomainSearchParams): Promise<DomainSearchResponse> {
    try {
      const response = await apiClient.post<DomainSearchResponse>('/domains/search', params);
      return response.data;
    } catch (error) {
      console.error('Error searching domains:', error);
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
  async analyzeDomain(domain: string): Promise<DomainSearchResult> {
    try {
      const response = await apiClient.get<DomainSearchResult>(`/domains/analyze`, {
        params: { domain }
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing domain:', error);
      throw new Error('Failed to analyze domain');
    }
  }
};
