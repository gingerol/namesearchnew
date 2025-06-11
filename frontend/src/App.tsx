import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Layouts
import { Layout } from './components/layout/Layout';
import { AdminLayout } from './components/layout/AdminLayout';
import { PublicLayout } from './components/layout/PublicLayout';

// Auth
import { LoginPage } from './features/auth/LoginPage';
import { SignUpPage } from './features/auth/SignUpPage';

// Main App
import DashboardPage from './features/dashboard/DashboardPage';
import DomainSearchPage from './features/search/DomainSearchPage';
import { PublicDomainSearchPage } from './features/search/PublicDomainSearchPage';
import { ProjectsPage } from './features/projects/ProjectsPage';
import { WatchlistPage } from './features/watchlist/WatchlistPage';
import { TrendsPage } from './features/trends/TrendsPage';
import { AnalysisPage } from './features/analysis/AnalysisPage';

// Admin
import AdminDashboard from './features/admin/AdminDashboard';
import { UserManagement } from './features/admin/UserManagement';
import { AdminProjects } from './features/admin/AdminProjects';
import { AnalyticsPage } from './features/admin/AnalyticsPage';
import { SystemSettings } from './features/admin/SystemSettings';
import { ApiKeys } from './features/admin/ApiKeys';
import { SystemLogs } from './features/admin/SystemLogs';

// Error
import { NotFoundPage } from './features/error/NotFoundPage';
import { useAuthStore } from './features/auth/store/authStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  // Get authentication state from the auth store
  const { isAuthenticated, isLoading, isInitialized } = useAuthStore();
  
  // Show loading state only if we're still initializing
  if (isLoading && !isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          {/* Root route - always redirects to search */}
          <Route path="/" element={<Navigate to="/search" replace />} />
          
          {/* Public routes with public layout */}
          <Route element={<PublicLayout><Outlet /></PublicLayout>}>
            <Route path="/search" element={<PublicDomainSearchPage />} />
            <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
            <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <SignUpPage />} />
            <Route path="/forgot-password" element={<div>Forgot Password Page</div>} />
            <Route path="/reset-password" element={<div>Reset Password Page</div>} />
            <Route path="/verify-email" element={<div>Verify Email Page</div>} />
            <Route path="/pricing" element={<div>Pricing Page</div>} />
            <Route path="/about" element={<div>About Page</div>} />
            <Route path="/contact" element={<div>Contact Page</div>} />
            <Route path="/terms" element={<div>Terms of Service</div>} />
            <Route path="/privacy" element={<div>Privacy Policy</div>} />
          </Route>
          
          {/* Protected routes - require authentication */}
          <Route element={<Layout><Outlet /></Layout>}>
            <Route path="dashboard" element={
              isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />
            } />
            <Route path="projects" element={
              isAuthenticated ? <ProjectsPage /> : <Navigate to="/login" replace />
            } />
            <Route path="projects/:projectId" element={
              isAuthenticated ? <DomainSearchPage /> : <Navigate to="/login" replace />
            } />
            <Route path="watchlist" element={
              isAuthenticated ? <WatchlistPage /> : <Navigate to="/login" replace />
            } />
            <Route path="trends" element={
              isAuthenticated ? <TrendsPage /> : <Navigate to="/login" replace />
            } />
            <Route path="analysis" element={
              isAuthenticated ? <AnalysisPage /> : <Navigate to="/login" replace />
            } />
            <Route path="admin" element={
              isAuthenticated ? (
                <AdminLayout><Outlet /></AdminLayout>
              ) : (
                <Navigate to="/login" replace />
              )}
            >
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
