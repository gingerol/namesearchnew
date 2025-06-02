import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Loader2 } from 'lucide-react';

interface AuthRedirectProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireVerified?: boolean;
  requireAdmin?: boolean;
  redirectTo?: string;
}

export function AuthRedirect({
  children,
  requireAuth = true,
  requireVerified = false,
  requireAdmin = false,
  redirectTo = '/login',
}: AuthRedirectProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuthStore();

  useEffect(() => {
    if (isLoading) return;

    // If authentication is required but user is not authenticated
    if (requireAuth && !isAuthenticated) {
      navigate(redirectTo, {
        state: { from: location },
        replace: true,
      });
      return;
    }

    // If user needs to be verified but isn't
    if (isAuthenticated && requireVerified && !user?.isVerified) {
      navigate('/verify-email', {
        state: { from: location },
        replace: true,
      });
      return;
    }

    // If admin access is required but user is not admin
    if (isAuthenticated && requireAdmin && user?.role !== 'admin') {
      navigate('/unauthorized', { replace: true });
      return;
    }
  }, [
    isAuthenticated,
    isLoading,
    user,
    requireAuth,
    requireVerified,
    requireAdmin,
    navigate,
    location,
    redirectTo,
  ]);

  // Show loading state while checking auth
  if (isLoading || (requireAuth && !isAuthenticated)) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If all checks pass, render children
  return <>{children}</>;
}

// Helper components for common auth patterns
export function RequireAuth({ children }: { children: React.ReactNode }) {
  return (
    <AuthRedirect requireAuth>
      {children}
    </AuthRedirect>
  );
}

export function RequireVerified({ children }: { children: React.ReactNode }) {
  return (
    <AuthRedirect requireAuth requireVerified>
      {children}
    </AuthRedirect>
  );
}

export function RequireAdmin({ children }: { children: React.ReactNode }) {
  return (
    <AuthRedirect requireAuth requireVerified requireAdmin>
      {children}
    </AuthRedirect>
  );
}

// For public routes that should only be accessible when not authenticated
export function RequireGuest({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Redirect to the previous page or home if user is authenticated
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, location]);

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
