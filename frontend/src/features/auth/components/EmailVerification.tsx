import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2, Loader2, Mail, RotateCw } from 'lucide-react';

export const EmailVerification = () => {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { verifyEmail, resendVerificationEmail, user: currentUser } = useAuthStore();
  
  const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  
  const token = searchParams.get('token');
  const emailFromParams = searchParams.get('email');
  const emailFromState = (location.state as any)?.email;
  const email = emailFromParams || emailFromState || currentUser?.email || '';

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) return;
      
      setStatus('verifying');
      setError(null);
      
      try {
        await verifyEmail(token);
        setStatus('success');
        
        // Auto-navigate to dashboard after 3 seconds if user is logged in
        if (currentUser) {
          setTimeout(() => {
            navigate('/dashboard', { replace: true });
          }, 3000);
        }
      } catch (err) {
        console.error('Email verification error:', err);
        setStatus('error');
        setError(
          err instanceof Error ? err.message : 'Failed to verify email. The link may be invalid or expired.'
        );
      }
    };

    if (token) {
      verifyToken();
    } else {
      setStatus('idle');
    }
  }, [token, verifyEmail, navigate, currentUser]);

  const handleResendEmail = async () => {
    if (!email) return;
    
    setIsResending(true);
    setError(null);
    
    try {
      await resendVerificationEmail(email);
      setResendSuccess(true);
      
      // Hide success message after 5 seconds
      setTimeout(() => {
        setResendSuccess(false);
      }, 5000);
    } catch (err) {
      console.error('Resend verification email error:', err);
      setError(
        err instanceof Error ? err.message : 'Failed to resend verification email. Please try again.'
      );
    } finally {
      setIsResending(false);
    }
  };

  if (status === 'verifying') {
    return (
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Verifying your email</h1>
          <p className="text-muted-foreground">
            Please wait while we verify your email address...
          </p>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <CheckCircle2 className="h-8 w-8 text-green-600" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Email verified successfully!</h1>
          <p className="text-muted-foreground">
            Thank you for verifying your email address.
          </p>
          {currentUser && (
            <p className="text-sm text-muted-foreground">
              Redirecting to your dashboard...
            </p>
          )}
        </div>
        {!currentUser && (
          <Button asChild className="w-full mt-4">
            <a href="/login">Go to login</a>
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <Mail className="h-8 w-8 text-blue-600" />
        </div>
        <h1 className="mt-4 text-2xl font-bold">Verify your email</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {email ? (
            <>
              We've sent a verification link to <strong>{email}</strong>
            </>
          ) : (
            'Enter your email below to receive a verification link'
          )}
        </p>
      </div>

      {status === 'error' && error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {resendSuccess && (
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>
            Verification email sent successfully. Please check your inbox.
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        <Button
          onClick={handleResendEmail}
          disabled={isResending || !email}
          className="w-full"
        >
          {isResending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <RotateCw className="mr-2 h-4 w-4" />
              Resend verification email
            </>
          )}
        </Button>

        <div className="text-center text-sm">
          <p className="text-muted-foreground">
            Already verified your email?{' '}
            <a href="/login" className="font-medium text-primary hover:underline">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};
