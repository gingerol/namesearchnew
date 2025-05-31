import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "../../stores/auth";
import { adminApi } from "./api";

interface AdminStats {
  user_count: number;
  project_count: number;
}

interface AdminUser {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AdminProject {
  id: number;
  name: string;
  owner?: { email: string };
  status?: string;
}

interface AdminLog {
  timestamp: string;
  message: string;
}

interface AdminApiKey {
  key: string;
  owner: string;
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [logs, setLogs] = useState<AdminLog[]>([]);
  const [apiKeys, setApiKeys] = useState<AdminApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      adminApi.getStats(),
      adminApi.getUsers(),
      adminApi.getProjects(),
      adminApi.getLogs(),
      adminApi.getApiKeys(),
    ])
      .then(([stats, users, projects, logs, apiKeys]) => {
        setStats(stats);
        setUsers(users);
        setProjects(projects);
        setLogs(logs);
        setApiKeys(apiKeys);
        setLoading(false);
      })
      .catch((err) => {
        setError(err?.message || "Failed to load admin data");
        setLoading(false);
      });
  }, []);

  if (!user || !user.is_superuser) {
    return <Navigate to="/" replace />;
  }

  if (loading) return <div className="p-8 text-center">Loading admin data...</div>;
  if (error) return <div className="p-8 text-center text-red-600">{error}</div>;

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Stats Widget */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Stats</h2>
          <ul className="text-gray-700">
            <li><b>Users:</b> {stats?.user_count ?? '-'}</li>
            <li><b>Projects:</b> {stats?.project_count ?? '-'}</li>
          </ul>
        </div>
        {/* Users Widget */}
        <div className="bg-white rounded-lg shadow p-6 overflow-x-auto">
          <h2 className="text-xl font-semibold mb-2">Users</h2>
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                <th className="text-left pr-4">Email</th>
                <th className="text-left pr-4">Active</th>
                <th className="text-left pr-4">Superuser</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="pr-4">{u.email}</td>
                  <td className="pr-4">{u.is_active ? "Yes" : "No"}</td>
                  <td className="pr-4">{u.is_superuser ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Projects Widget */}
        <div className="bg-white rounded-lg shadow p-6 overflow-x-auto">
          <h2 className="text-xl font-semibold mb-2">Projects</h2>
          <table className="min-w-full text-sm">
            <thead>
              <tr>
                <th className="text-left pr-4">Name</th>
                <th className="text-left pr-4">Owner</th>
                <th className="text-left pr-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id}>
                  <td className="pr-4">{p.name}</td>
                  <td className="pr-4">{p.owner?.email ?? '-'} </td>
                  <td className="pr-4">{p.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Logs Widget */}
        <div className="bg-white rounded-lg shadow p-6 overflow-x-auto">
          <h2 className="text-xl font-semibold mb-2">System Logs</h2>
          <ul className="text-gray-700 max-h-48 overflow-y-auto">
            {logs.map((log, i) => (
              <li key={i} className="mb-1">
                <span className="font-mono text-xs">[{log.timestamp}]</span> {log.message}
              </li>
            ))}
          </ul>
        </div>
        {/* API Keys Widget */}
        <div className="bg-white rounded-lg shadow p-6 overflow-x-auto">
          <h2 className="text-xl font-semibold mb-2">API Keys</h2>
          <ul className="text-gray-700">
            {apiKeys.map((k, i) => (
              <li key={i} className="mb-1">
                <span className="font-mono text-xs">{k.key}</span> <span className="text-gray-500">({k.owner})</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
