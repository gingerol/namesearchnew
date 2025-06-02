import React from 'react';
import { Outlet } from 'react-router-dom';

export const AdminLayout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-4">
          <h1 className="text-xl font-bold text-gray-800">Admin</h1>
        </div>
        <nav className="mt-6">
          <NavItem to="/admin/overview" icon="dashboard">Overview</NavItem>
          <NavItem to="/admin/users" icon="people">Users</NavItem>
          <NavItem to="/admin/projects" icon="folder">Projects</NavItem>
          <NavItem to="/admin/analytics" icon="analytics">Analytics</NavItem>
          <NavItem to="/admin/settings" icon="settings">Settings</NavItem>
          <NavItem to="/admin/api-keys" icon="key">API Keys</NavItem>
          <NavItem to="/admin/logs" icon="list">System Logs</NavItem>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-6">
        {children || <Outlet />}
      </main>
    </div>
  );
};

const NavItem: React.FC<{ to: string; icon: string; children: React.ReactNode }> = ({ to, icon, children }) => (
  <a
    href={to}
    className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100"
  >
    <span className="material-icons mr-3">{icon}</span>
    <span>{children}</span>
  </a>
);
