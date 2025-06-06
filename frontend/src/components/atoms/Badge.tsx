import React from 'react';

interface BadgeProps {
  variant?: 'success' | 'error' | 'warning' | 'info';
  className?: string;
  children: React.ReactNode;
}

const variantMap = {
  success: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
} as const;

const Badge: React.FC<BadgeProps> = ({
  variant = 'info',
  className = '',
  children,
}) => {
  const variantClasses = variantMap[variant];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;
