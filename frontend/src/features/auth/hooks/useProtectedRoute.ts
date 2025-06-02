import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

/**
 * Hook to protect routes that require authentication
 * @param redirectTo Path to redirect to if not authenticated (default: '/login')
 * @param requireVerifiedEmail Whether to require email verification (default: false)
 * @param allowedRoles Array of allowed user roles (default: ['user', 'admin'])
 */
export const useProtectedRoute = ({
  redirectTo = '/login',
  requireVerifiedEmail = false,
  allowedRoles = ['user', 'admin'],
} = {}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuthStore();

  useEffect(() => {
    if (isLoading) return;

    // If not authenticated, redirect to login with return URL
    if (!isAuthenticated) {
      navigate(redirectTo, {
        state: { from: location },
        replace: true,
      });
      return;
    }

    // If email verification is required but user is not verified
    if (requireVerifiedEmail && user && !user.isVerified) {
      navigate('/verify-email', {
        state: { from: location },
        replace: true,
      });
      return;
    }

    // Check user role
    if (user && !allowedRoles.includes(user.role)) {
      navigate('/unauthorized', { replace: true });
    }
  }, [
    isAuthenticated,
    user,
    isLoading,
    navigate,
    location,
    redirectTo,
    requireVerifiedEmail,
    allowedRoles,
  ]);

  return { isAuthorized: isAuthenticated, isLoading, user };
};

/**
 * Hook to protect admin routes
 */
export const useAdminRoute = () => {
  return useProtectedRoute({
    redirectTo: '/login',
    requireVerifiedEmail: true,
    allowedRoles: ['admin'],
  });
};

/**
 * Hook to redirect authenticated users away from auth pages (login/register)
 */
export const useRedirectIfAuthenticated = (redirectTo = '/dashboard') => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Get the return URL from location state or default to dashboard
      const from = (location.state as any)?.from?.pathname || redirectTo;
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, location, redirectTo]);

  return { isAuthenticated, isLoading };
};
