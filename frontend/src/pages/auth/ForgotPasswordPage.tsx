import { Link } from 'react-router-dom';
import { ForgotPasswordForm } from '@/features/auth/components/ForgotPasswordForm';
import { Logo } from '@/components/Logo';

export default function ForgotPasswordPage() {
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
              "Forgot your password? No worries, we've got you covered."
            </p>
            <footer className="text-sm">We'll help you get back into your account</footer>
          </blockquote>
        </div>
      </div>

      {/* Right side - Content */}
      <div className="lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[400px]">
          <div className="flex flex-col space-y-2 text-center lg:hidden">
            <h1 className="text-2xl font-semibold tracking-tight">
              Forgot your password?
            </h1>
            <p className="text-sm text-muted-foreground">
              Enter your email to reset your password
            </p>
          </div>
          
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <ForgotPasswordForm />
          </div>
          
          <p className="px-8 text-center text-sm text-muted-foreground">
            Remember your password?{' '}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
