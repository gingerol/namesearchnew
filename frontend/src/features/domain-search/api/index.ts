import axios from 'axios';
import type { DomainSearchResult, DomainSearchResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add a request interceptor to include auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.status, error.response.data);
      return Promise.reject(error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      return Promise.reject(new Error('No response received from server'));
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request error:', error.message);
      return Promise.reject(error);
    }
  }
);

export const domainSearchApi = {
  async searchDomains(query: string, tlds?: string[], limit: number = 10): Promise<DomainSearchResponse> {
    const response = await apiClient.post<DomainSearchResponse>('/domains', {
      query,
      tlds: tlds || ['com', 'io', 'ai', 'app', 'dev', 'net', 'org'],
      limit,
    });
    return response.data;
  },

  async getSuggestions(query: string, limit: number = 5): Promise<string[]> {
    // In a real app, you might have a dedicated suggestions endpoint
    // For now, we'll just return some basic variations
    const tlds = ['com', 'io', 'ai', 'app', 'dev'];
    const suffixes = ['', 'app', 'hq', 'inc', 'ai', 'io', 'get', 'try'];
    
    const suggestions = new Set<string>();
    
    for (const suffix of suffixes) {
      const base = query + (suffix ? `-${suffix}` : '');
      for (const tld of tlds) {
        if (suggestions.size >= limit) break;
        suggestions.add(`${base}.${tld}`);
      }
    }
    
    return Array.from(suggestions).slice(0, limit);
  },

  async checkDomainAvailability(domain: string): Promise<boolean> {
    try {
      const response = await apiClient.post<{ available: boolean }>('/domains/check', { domain });
      return response.data.available;
    } catch (error) {
      console.error('Error checking domain availability:', error);
      throw error;
    }
  },

  async getDomainDetails(domain: string): Promise<DomainSearchResult> {
    const response = await apiClient.get<DomainSearchResult>(`/domains/${encodeURIComponent(domain)}`);
    return response.data;
  },

  async getSearchHistory(limit: number = 10): Promise<DomainSearchResult[]> {
    const response = await apiClient.get<DomainSearchResult[]>(`/domains/history?limit=${limit}`);
    return response.data;
  },
};

export default domainSearchApi;
