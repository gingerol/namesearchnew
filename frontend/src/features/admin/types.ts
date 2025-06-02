export interface AdminStats {
  user_count: number;
  project_count: number;
  active_sessions: number;
  storage_used: string;
  recent_signups: { date: string; count: number }[];
}

export interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  last_login: string | null;
  created_at: string;
  project_count: number;
}

export interface AdminProject {
  id: number;
  name: string;
  owner: {
    id: number;
    email: string;
    full_name: string | null;
  };
  status: 'active' | 'archived' | 'deleted';
  created_at: string;
  updated_at: string;
  name_count: number;
}

export interface AdminLog {
  id: number;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  user_id: number | null;
  user_email: string | null;
}

export interface AdminApiKey {
  id: string;
  name: string;
  owner: {
    id: number;
    email: string;
    full_name: string | null;
  };
  last_used: string | null;
  created_at: string;
  expires_at: string | null;
}

export interface AdminMetrics {
  date: string;
  active_users: number;
  new_users: number;
  api_requests: number;
  storage_used: number;
}

export type TimeRange = '24h' | '7d' | '30d' | '90d' | '1y';
