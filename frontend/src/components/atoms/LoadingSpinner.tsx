import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
} as const;

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'blue',
  className = '',
}) => {
  const sizeClasses = sizeMap[size];
  const colorClasses = `border-${color}-500`;

  return (
    <div className={`relative ${className}`}>
      <div className={`animate-spin rounded-full ${sizeClasses} border-2 border-t-2 ${colorClasses} inline-block`} />
    </div>
  );
};

export default LoadingSpinner;
