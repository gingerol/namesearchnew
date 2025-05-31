// API service for admin dashboard widgets
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const adminApi = {
  async getStats() {
    const res = await axios.get(`${API_BASE}/admin/stats`, { withCredentials: true });
    return res.data;
  },
  async getUsers() {
    const res = await axios.get(`${API_BASE}/admin/users`, { withCredentials: true });
    return res.data;
  },
  async getProjects() {
    const res = await axios.get(`${API_BASE}/admin/projects`, { withCredentials: true });
    return res.data;
  },
  async getLogs() {
    const res = await axios.get(`${API_BASE}/admin/logs`, { withCredentials: true });
    return res.data;
  },
  async getApiKeys() {
    const res = await axios.get(`${API_BASE}/admin/api-keys`, { withCredentials: true });
    return res.data;
  },
};
