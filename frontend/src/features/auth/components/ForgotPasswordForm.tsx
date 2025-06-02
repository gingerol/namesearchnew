import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthForm, resetPasswordSchema } from '../hooks/useAuthForm';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Loader2, Mail } from 'lucide-react';

export const ForgotPasswordForm = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { resetPassword } = useAuthStore();

  const {
    values,
    errors,
    isSubmitting,
    submitError,
    handleChange,
    handleSubmit,
  } = useAuthForm({
    initialValues: {
      email: '',
    },
    validationSchema: resetPasswordSchema,
    onSubmit: async (values) => {
      try {
        await resetPassword(values.email);
        setIsSubmitted(true);
      } catch (error) {
        console.error('Password reset request error:', error);
      }
    },
  });

  if (isSubmitted) {
    return (
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <Mail className="h-8 w-8 text-green-600" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Check your email</h1>
          <p className="text-muted-foreground">
            We've sent a password reset link to <strong>{values.email}</strong>
          </p>
          <p className="text-sm text-muted-foreground">
            If you don't see the email, check your spam folder or try again.
          </p>
        </div>
        <Button asChild className="w-full mt-4">
          <Link to="/login">Back to login</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold tracking-tight">Forgot your password?</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Enter your email and we'll send you a link to reset your password
        </p>
      </div>

      {submitError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{submitError}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="name@example.com"
            value={values.email}
            onChange={handleChange}
            disabled={isSubmitting}
            autoComplete="email"
            className={errors.email ? 'border-red-500' : ''}
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email}</p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          Send reset link
        </Button>
      </form>

      <div className="text-center text-sm">
        <Link
          to="/login"
          className="font-medium text-primary hover:underline"
        >
          Back to login
        </Link>
      </div>
    </div>
  );
};
