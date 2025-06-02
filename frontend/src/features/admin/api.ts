import axios from 'axios';
import type { 
  AdminStats, 
  AdminUser, 
  AdminProject, 
  AdminLog, 
  AdminApiKey, 
  TimeRange,
  AdminMetrics
} from './types';
import { generateMockStats } from './utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add a request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    // You can add auth token here if needed
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
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
    // Handle common errors here (e.g., 401 Unauthorized)
    if (error.response?.status === 401) {
      // Handle unauthorized (e.g., redirect to login)
      console.error('Unauthorized access - please log in');
    }
    return Promise.reject(error);
  }
);

// Mock data generators for development
const isDev = import.meta.env.DEV;

const generateMockUsers = (count = 50): AdminUser[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    email: `user${i + 1}@example.com`,
    full_name: `User ${i + 1}`,
    is_active: Math.random() > 0.2, // 80% active
    is_superuser: i % 10 === 0, // 10% are admins
    last_login: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - Math.floor(Math.random() * 365) * 24 * 60 * 60 * 1000).toISOString(),
    project_count: Math.floor(Math.random() * 20)
  }));
};

const generateMockProjects = (count = 100): AdminProject[] => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Project ${i + 1}`,
    owner: {
      id: (i % 50) + 1,
      email: `user${(i % 50) + 1}@example.com`,
      full_name: `User ${(i % 50) + 1}`
    },
    status: ['active', 'archived', 'deleted'][Math.floor(Math.random() * 3)] as 'active' | 'archived' | 'deleted',
    created_at: new Date(Date.now() - Math.floor(Math.random() * 180) * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    name_count: Math.floor(Math.random() * 500)
  }));
};

const generateMockLogs = (count = 200): AdminLog[] => {
  // Intentionally unused - kept for future reference
  const _unused_actions = [
    'logged in', 
    'created project', 
    'deleted project', 
    'updated settings', 
    'exported data',
    'viewed dashboard',
    'searched names'
  ] as const;
  
  const messages = [
    'User performed action',
    'System update completed',
    'Data export finished',
    'New user registered',
    'Project created',
    'Project deleted',
    'Settings updated',
    'Search query executed',
    'API key generated',
    'Password changed',
    'Login successful',
    'Login failed',
    'Password reset requested',
    'Email verified',
    'Profile updated'
  ];

  const levels = ['info', 'warning', 'error'] as const;
  type LogLevel = typeof levels[number];
  
  return Array.from({ length: count }, (_, i) => {
    const level = levels[Math.floor(Math.random() * levels.length)] as LogLevel;
    return {
      id: i + 1,
      timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      level,
      message: messages[Math.floor(Math.random() * messages.length)],
      user_id: Math.random() > 0.3 ? Math.floor(Math.random() * 50) + 1 : null,
      user_email: Math.random() > 0.3 ? `user${Math.floor(Math.random() * 50) + 1}@example.com` : null
    };
  }).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

export const adminApi = {
  // Stats
  async getStats(): Promise<AdminStats> {
    if (isDev) {
      return new Promise(resolve => {
        setTimeout(() => resolve(generateMockStats()), 500);
      });
    }
    const res = await apiClient.get<AdminStats>('/admin/stats');
    return res.data;
  },

  // Users
  async getUsers(params?: { page?: number; pageSize?: number; search?: string }): Promise<{ data: AdminUser[]; total: number }> {
    if (isDev) {
      const users = generateMockUsers(50);
      return new Promise(resolve => {
        setTimeout(() => resolve({
          data: users.slice(
            ((params?.page || 1) - 1) * (params?.pageSize || 10),
            (params?.page || 1) * (params?.pageSize || 10)
          ),
          total: users.length
        }), 300);
      });
    }
    const res = await apiClient.get<{ data: AdminUser[]; total: number }>('/admin/users', { params });
    return res.data;
  },

  async getUser(userId: number): Promise<AdminUser> {
    if (isDev) {
      return new Promise(resolve => {
        const users = generateMockUsers(1).map(u => ({ ...u, id: userId }));
        setTimeout(() => resolve(users[0]), 200);
      });
    }
    const res = await apiClient.get<AdminUser>(`/admin/users/${userId}`);
    return res.data;
  },

  async updateUser(userId: number, data: Partial<AdminUser>): Promise<AdminUser> {
    if (isDev) {
      return new Promise(resolve => {
        const user = generateMockUsers(1)[0];
        setTimeout(() => resolve({ ...user, ...data, id: userId }), 300);
      });
    }
    const res = await apiClient.put<AdminUser>(`/admin/users/${userId}`, data);
    return res.data;
  },

  async deleteUser(userId: number): Promise<void> {
    if (isDev) {
      return new Promise(resolve => setTimeout(resolve, 300));
    }
    await apiClient.delete(`/admin/users/${userId}`);
  },

  // Projects
  async getProjects(params?: { 
    page?: number; 
    pageSize?: number; 
    search?: string;
    ownerId?: number;
    status?: string;
  }): Promise<{ data: AdminProject[]; total: number }> {
    if (isDev) {
      const projects = generateMockProjects(100);
      let filtered = [...projects];
      
      if (params?.ownerId) {
        filtered = filtered.filter(p => p.owner.id === params.ownerId);
      }
      
      if (params?.status) {
        filtered = filtered.filter(p => p.status === params.status);
      }
      
      if (params?.search) {
        const searchLower = params.search.toLowerCase();
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(searchLower) ||
          p.owner.email.toLowerCase().includes(searchLower) ||
          (p.owner.full_name?.toLowerCase().includes(searchLower) ?? false)
        );
      }
      
      return new Promise(resolve => {
        setTimeout(() => resolve({
          data: filtered.slice(
            ((params?.page || 1) - 1) * (params?.pageSize || 10),
            (params?.page || 1) * (params?.pageSize || 10)
          ),
          total: filtered.length
        }), 300);
      });
    }
    
    const res = await apiClient.get<{ data: AdminProject[]; total: number }>('/admin/projects', { params });
    return res.data;
  },

  async getProject(projectId: number): Promise<AdminProject> {
    if (isDev) {
      return new Promise(resolve => {
        const projects = generateMockProjects(1).map(p => ({ ...p, id: projectId }));
        setTimeout(() => resolve(projects[0]), 200);
      });
    }
    const res = await apiClient.get<AdminProject>(`/admin/projects/${projectId}`);
    return res.data;
  },

  async updateProject(projectId: number, data: Partial<AdminProject>): Promise<AdminProject> {
    if (isDev) {
      return new Promise(resolve => {
        const project = generateMockProjects(1)[0];
        setTimeout(() => resolve({ ...project, ...data, id: projectId }), 300);
      });
    }
    const res = await apiClient.put<AdminProject>(`/admin/projects/${projectId}`, data);
    return res.data;
  },

  async deleteProject(projectId: number): Promise<void> {
    if (isDev) {
      return new Promise(resolve => setTimeout(resolve, 300));
    }
    await apiClient.delete(`/admin/projects/${projectId}`);
  },

  // Logs
  async getLogs(params?: { 
    page?: number; 
    pageSize?: number; 
    level?: 'info' | 'warning' | 'error';
    userId?: number;
    startDate?: string;
    endDate?: string;
  }): Promise<{ data: AdminLog[]; total: number }> {
    if (isDev) {
      const logs = generateMockLogs(200);
      let filtered = [...logs];
      
      if (params?.level) {
        filtered = filtered.filter(log => log.level === params.level);
      }
      
      if (params?.userId) {
        filtered = filtered.filter(log => log.user_id === params.userId);
      }
      
      if (params?.startDate) {
        const start = new Date(params.startDate);
        filtered = filtered.filter(log => new Date(log.timestamp) >= start);
      }
      
      if (params?.endDate) {
        const end = new Date(params.endDate);
        end.setHours(23, 59, 59, 999);
        filtered = filtered.filter(log => new Date(log.timestamp) <= end);
      }
      
      return new Promise(resolve => {
        setTimeout(() => resolve({
          data: filtered.slice(
            ((params?.page || 1) - 1) * (params?.pageSize || 20),
            (params?.page || 1) * (params?.pageSize || 20)
          ),
          total: filtered.length
        }), 300);
      });
    }
    
    const res = await apiClient.get<{ data: AdminLog[]; total: number }>('/admin/logs', { params });
    return res.data;
  },

  // API Keys
  async getApiKeys(userId?: number): Promise<AdminApiKey[]> {
    if (isDev) {
      const keys = Array.from({ length: 15 }, (_, i) => ({
        id: `key_${i + 1}`,
        name: `API Key ${i + 1}`,
        owner: {
          id: (i % 5) + 1,
          email: `user${(i % 5) + 1}@example.com`,
          full_name: `User ${(i % 5) + 1}`
        },
        last_used: i % 3 === 0 ? null : new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - Math.floor(Math.random() * 90) * 24 * 60 * 60 * 1000).toISOString(),
        expires_at: i % 4 === 0 ? new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString() : null
      }));
      
      const filtered = userId ? keys.filter(k => k.owner.id === userId) : keys;
      
      return new Promise(resolve => {
        setTimeout(() => resolve(filtered), 300);
      });
    }
    
    const res = await apiClient.get<AdminApiKey[]>('/admin/api-keys', { params: { userId } });
    return res.data;
  },

  async createApiKey(data: { name: string; userId: number; expiresInDays?: number }): Promise<{ key: string }> {
    if (isDev) {
      return new Promise((resolve) => {
        setTimeout(() => resolve({
          key: `sk_test_${Math.random().toString(36).substring(2, 15)}_${Math.random().toString(36).substring(2, 15)}`
        }), 300);
      });
    }
    const res = await apiClient.post<{ key: string }>('/admin/api-keys', data);
    return res.data;
  },

  async revokeApiKey(keyId: string): Promise<void> {
    if (isDev) {
      return new Promise(resolve => setTimeout(resolve, 300));
    }
    await apiClient.delete(`/admin/api-keys/${keyId}`);
  },

  // Metrics
  async getMetrics(timeRange: TimeRange = '7d'): Promise<AdminMetrics[]> {
    if (isDev) {
      const now = new Date();
      const data: AdminMetrics[] = [];
      let days = 7; // Default to 7 days
      
      switch (timeRange) {
        case '24h':
          // Hourly data for last 24 hours
          for (let i = 23; i >= 0; i--) {
            const date = new Date(now);
            date.setHours(date.getHours() - i);
            data.push({
              date: date.toISOString(),
              active_users: Math.floor(Math.random() * 100) + 50,
              new_users: Math.floor(Math.random() * 10) + 1,
              api_requests: Math.floor(Math.random() * 1000) + 500,
              storage_used: Math.floor(Math.random() * 1000000000) + 1000000000 // 1-2GB
            });
          }
          break;
          
        case '7d':
          days = 7;
          break;
          
        case '30d':
          days = 30;
          break;
          
        case '90d':
          days = 90;
          break;
          
        case '1y':
          // Monthly data for the last year
          for (let i = 11; i >= 0; i--) {
            const date = new Date(now);
            date.setMonth(date.getMonth() - i);
            data.push({
              date: date.toISOString(),
              active_users: Math.floor(Math.random() * 500) + 200,
              new_users: Math.floor(Math.random() * 100) + 20,
              api_requests: Math.floor(Math.random() * 5000) + 2000,
              storage_used: Math.floor(Math.random() * 10000000000) + 10000000000 // 10-20GB
            });
          }
          return new Promise(resolve => setTimeout(() => resolve(data), 300));
      }
      
      // Generate daily data
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        data.push({
          date: date.toISOString(),
          active_users: Math.floor(Math.random() * 200) + 100,
          new_users: Math.floor(Math.random() * 20) + 5,
          api_requests: Math.floor(Math.random() * 2000) + 1000,
          storage_used: Math.floor(Math.random() * 5000000000) + 2000000000 // 2-7GB
        });
      }
      
      return new Promise(resolve => setTimeout(() => resolve(data), 300));
    }
    
    const res = await apiClient.get<AdminMetrics[]>('/admin/metrics', { params: { range: timeRange } });
    return res.data;
  },
};
