import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Layouts
import { Layout } from './components/layout/Layout';
import { AdminLayout } from './components/layout/AdminLayout';

// Auth
import { LoginPage } from './features/auth/LoginPage';
import { SignUpPage } from './features/auth/SignUpPage';

// Main App
import { DashboardPage } from './features/dashboard/DashboardPage';
import { DomainSearchPage } from './features/search/DomainSearchPage';
import { ProjectsPage } from './features/projects/ProjectsPage';
import { WatchlistPage } from './features/watchlist/WatchlistPage';
import { TrendsPage } from './features/trends/TrendsPage';
import { AnalysisPage } from './features/analysis/AnalysisPage';

// Admin
import { AdminDashboard } from './features/admin/AdminDashboard';
import { UserManagement } from './features/admin/UserManagement';
import { AdminProjects } from './features/admin/AdminProjects';
import { AnalyticsPage } from './features/admin/AnalyticsPage';
import { SystemSettings } from './features/admin/SystemSettings';
import { ApiKeys } from './features/admin/ApiKeys';
import { SystemLogs } from './features/admin/SystemLogs';

// Error
import { NotFoundPage } from './features/error/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  // In a real app, you would check for an auth token here
  const isAuthenticated = false; // Will be replaced with actual auth check

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/search" />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" /> : <SignUpPage />} />
          <Route path="/search" element={<DomainSearchPage />} />
          
          {/* Protected routes - require authentication */}
          <Route path="/" element={isAuthenticated ? <Layout><Outlet /></Layout> : <Navigate to="/search" />}>
            <Route index element={<DashboardPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="projects/:projectId" element={<DomainSearchPage />} />
            <Route path="watchlist" element={<WatchlistPage />} />
            <Route path="trends" element={<TrendsPage />} />
            <Route path="analysis" element={<AnalysisPage />} />
            <Route path="admin" element={<AdminLayout><Outlet /></AdminLayout>}>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="projects" element={<AdminProjects />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="settings" element={<SystemSettings />} />
              <Route path="api-keys" element={<ApiKeys />} />
              <Route path="logs" element={<SystemLogs />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Router>
      
      <ReactQueryDevtools initialIsOpen={false} />
      <Toaster position="top-right" />
    </QueryClientProvider>
  );
}

export default App;
