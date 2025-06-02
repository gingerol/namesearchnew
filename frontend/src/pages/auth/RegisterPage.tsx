import { useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store/authStore';
import { RegisterForm } from '@/features/auth/components/RegisterForm';
import { useRedirectIfAuthenticated } from '@/features/auth/hooks/useProtectedRoute';
import { Button } from '@/components/ui/button';
import { Logo } from '@/components/Logo';

export default function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Redirect if already authenticated
  useRedirectIfAuthenticated();

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container relative min-h-screen flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0">
      {/* Left side - Form */}
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white lg:flex dark:border-r">
        <div className="absolute inset-0 bg-gradient-to-br from-primary to-primary/80" />
        <div className="relative z-20 flex items-center text-lg font-medium">
          <Logo className="h-8 w-auto text-white" />
          <span className="ml-2 font-bold">Namesearch.io</span>
        </div>
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-2">
            <p className="text-lg">
              "Join our community of domain investors and developers finding the perfect domain names."
            </p>
            <footer className="text-sm">Start your journey today</footer>
          </blockquote>
        </div>
      </div>

      {/* Right side - Content */}
      <div className="lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[400px]">
          <div className="flex flex-col space-y-2 text-center lg:hidden">
            <h1 className="text-2xl font-semibold tracking-tight">
              Create an account
            </h1>
            <p className="text-sm text-muted-foreground">
              Enter your information to get started
            </p>
          </div>
          
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <RegisterForm />
          </div>
          
          <p className="px-8 text-center text-sm text-muted-foreground">
            By creating an account, you agree to our{' '}
            <Link to="/terms" className="underline underline-offset-4 hover:text-primary">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link to="/privacy" className="underline underline-offset-4 hover:text-primary">
              Privacy Policy
            </Link>
            .
          </p>
          
          <div className="text-center text-sm">
            Already have an account?{' '}
            <Link 
              to="/login" 
              state={location.state}
              className="font-medium text-primary hover:underline"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
