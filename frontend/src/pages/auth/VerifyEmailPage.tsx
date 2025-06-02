import { useSearchParams, useLocation } from 'react-router-dom';
import { EmailVerification } from '@/features/auth/components/EmailVerification';
import { Logo } from '@/components/Logo';

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  
  // Get email from URL params or location state
  const emailFromParams = searchParams.get('email');
  const emailFromState = (location.state as any)?.email;
  const email = emailFromParams || emailFromState || '';

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
              "Verify your email to unlock all features and secure your account."
            </p>
            <footer className="text-sm">
              {email ? `Verifying ${email}` : 'Email verification in progress'}
            </footer>
          </blockquote>
        </div>
      </div>

      {/* Right side - Content */}
      <div className="lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[400px]">
          <div className="flex flex-col space-y-2 text-center lg:hidden">
            <h1 className="text-2xl font-semibold tracking-tight">
              Verify your email
            </h1>
            <p className="text-sm text-muted-foreground">
              {email 
                ? `We've sent a verification link to ${email}`
                : 'Please check your email for a verification link'}
            </p>
          </div>
          
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <EmailVerification />
          </div>
          
          <p className="px-8 text-center text-sm text-muted-foreground">
            Didn't receive an email? Check your spam folder or{' '}
            <a 
              href="/register" 
              className="font-medium text-primary hover:underline"
            >
              sign up
            </a>{' '}
            again.
          </p>
        </div>
      </div>
    </div>
  );
}
