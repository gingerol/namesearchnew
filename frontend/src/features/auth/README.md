# Authentication System

This module provides a complete authentication system for the Namesearch.io application, including user registration, login, password reset, and email verification.

## Features

- User registration with email verification
- Login with email/password
- Password reset flow
- Email verification
- Protected routes and role-based access control
- Persistent authentication state
- Token refresh
- Social login (OAuth) ready

## Components

### Pages

- `LoginPage` - User login form
- `RegisterPage` - User registration form
- `ForgotPasswordPage` - Request password reset
- `ResetPasswordPage` - Set new password
- `VerifyEmailPage` - Email verification

### Forms

- `LoginForm` - Login form component
- `RegisterForm` - Registration form with validation
- `ForgotPasswordForm` - Password reset request form
- `ResetPasswordForm` - New password form
- `EmailVerification` - Email verification component

### Utilities

- `AuthRedirect` - Component for route protection
- `RequireAuth` - Wrapper for authenticated routes
- `RequireVerified` - Wrapper for verified user routes
- `RequireAdmin` - Wrapper for admin routes
- `RequireGuest` - Wrapper for public-only routes

## Hooks

- `useAuthForm` - Form handling with validation
- `useProtectedRoute` - Route protection hook
- `useAuthStore` - Global authentication state (Zustand)

## Usage

### Protected Routes

```tsx
import { RequireAuth, RequireAdmin } from '@/features/auth';

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Protected routes */}
      <Route element={<RequireAuth />}>
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
      
      {/* Admin-only routes */}
      <Route element={<RequireAdmin />}>
        <Route path="/admin" element={<AdminPage />} />
      </Route>
    </Routes>
  );
}
```

### Using Auth State

```tsx
import { useAuthStore } from '@/features/auth';

function UserProfile() {
  const { user, isAuthenticated, logout } = useAuthStore();
  
  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }
  
  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## Environment Variables

The following environment variables are required:

```
VITE_API_BASE_URL=your_api_url
# For OAuth (optional)
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GITHUB_CLIENT_ID=your_github_client_id
```

## API Integration

The authentication system expects the following API endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh-token` - Refresh access token
- `POST /auth/logout` - User logout
- `POST /auth/request-password-reset` - Request password reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/verify-email` - Verify email
- `POST /auth/resend-verification` - Resend verification email

## Error Handling

All forms handle errors automatically and display them to the user. The `useAuthStore` also provides error states that can be used for custom error handling.

## Styling

Components are styled using Tailwind CSS and the project's design system. Customize the styles by modifying the component classes or extending the theme.

## Testing

To test the authentication flow:

1. Register a new account
2. Verify your email
3. Log in with your credentials
4. Test password reset flow
5. Verify protected routes

## Security Considerations

- All sensitive data is sent over HTTPS
- Passwords are hashed before being sent to the server
- JWT tokens are stored securely in HTTP-only cookies
- CSRF protection is implemented
- Rate limiting is applied to authentication endpoints
- Password requirements are enforced client and server-side
