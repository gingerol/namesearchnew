import type { AdminLog, TimeRange } from './types';

export const formatDate = (dateString: string | null | undefined, options: Intl.DateTimeFormatOptions = {}) => {
  if (!dateString) return 'Never';
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };
  
  return new Date(dateString).toLocaleString(undefined, { ...defaultOptions, ...options });
};

export const getLogLevelColor = (level: AdminLog['level']) => {
  switch (level) {
    case 'error':
      return 'bg-red-100 text-red-800';
    case 'warning':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-blue-100 text-blue-800';
  }
};

export const getStatusBadgeColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800';
    case 'inactive':
    case 'suspended':
      return 'bg-yellow-100 text-yellow-800';
    case 'deleted':
    case 'banned':
      return 'bg-red-100 text-red-800';
    case 'pending':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getTimeRangeLabel = (range: TimeRange) => {
  switch (range) {
    case '24h':
      return 'Last 24 hours';
    case '7d':
      return 'Last 7 days';
    case '30d':
      return 'Last 30 days';
    case '90d':
      return 'Last 90 days';
    case '1y':
      return 'Last year';
    default:
      return range;
  }
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

export const generateMockMetrics = (timeRange: TimeRange): { date: string; value: number }[] => {
  const now = new Date();
  const data = [];
  let days = 7; // Default to 7 days
  
  switch (timeRange) {
    case '24h':
      // Generate hourly data for last 24 hours
      for (let i = 23; i >= 0; i--) {
        const date = new Date(now);
        date.setHours(date.getHours() - i);
        data.push({
          date: date.toISOString(),
          value: Math.floor(Math.random() * 1000) + 500
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
          value: Math.floor(Math.random() * 10000) + 5000
        });
      }
      return data;
  }
  
  // Generate daily data
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    data.push({
      date: date.toISOString(),
      value: Math.floor(Math.random() * 2000) + 1000
    });
  }
  
  return data;
};

export const generateMockStats = (): any => ({
  user_count: 1243,
  project_count: 5782,
  active_sessions: 243,
  storage_used: '45.8 GB',
  recent_signups: Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toISOString().split('T')[0],
      count: Math.floor(Math.random() * 50) + 10
    };
  })
});
