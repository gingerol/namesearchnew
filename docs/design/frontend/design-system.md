# Frontend Design System

## Color Palette

### Primary Colors
- Primary: `#2563eb` (Blue 600)
- Secondary: `#16a34a` (Green 600)
- Accent: `#db2777` (Pink 600)

### Neutral Colors
- Background: `#ffffff`
- Surface: `#f9fafb`
- Border: `#e5e7eb`
- Text: `#1f2937`
- Text Secondary: `#6b7280`

## Typography

### Font Family
- Base: `Inter, system-ui, sans-serif`
- Heading: `Inter, system-ui, sans-serif`

### Font Sizes
- H1: `2.25rem` (36px)
- H2: `1.875rem` (30px)
- H3: `1.5rem` (24px)
- H4: `1.25rem` (20px)
- Body: `1rem` (16px)
- Small: `0.875rem` (14px)

## Spacing

### Base Unit
- Base: `0.25rem` (4px)

### Scale
- 0: `0`
- 1: `0.25rem` (4px)
- 2: `0.5rem` (8px)
- 3: `0.75rem` (12px)
- 4: `1rem` (16px)
- 5: `1.25rem` (20px)
- 6: `1.5rem` (24px)
- 8: `2rem` (32px)
- 10: `2.5rem` (40px)
- 12: `3rem` (48px)
- 16: `4rem` (64px)
- 20: `5rem` (80px)
- 24: `6rem` (96px)

## Breakpoints

### Responsive Breakpoints
- Mobile: `0px`
- Tablet: `640px`
- Laptop: `1024px`
- Desktop: `1280px`

## Component Tokens

### Buttons
```typescript
type ButtonTokens = {
  variants: {
    primary: {
      background: 'bg-blue-600';
      hover: 'hover:bg-blue-700';
      text: 'text-white';
    };
    secondary: {
      background: 'bg-green-600';
      hover: 'hover:bg-green-700';
      text: 'text-white';
    };
    danger: {
      background: 'bg-red-600';
      hover: 'hover:bg-red-700';
      text: 'text-white';
    };
  };
  sizes: {
    sm: 'px-3 py-1.5 text-sm';
    md: 'px-4 py-2';
    lg: 'px-6 py-3 text-lg';
  };
};
```

### Input Fields
```typescript
type InputTokens = {
  base: 'border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500';
  error: 'border-red-500 focus:ring-red-500';
  success: 'border-green-500 focus:ring-green-500';
};
```

### Cards
```typescript
type CardTokens = {
  base: 'bg-white rounded-lg shadow-sm border border-gray-200 p-4';
  hover: 'hover:shadow-md';
  variants: {
    primary: 'bg-blue-50 border-blue-200';
    secondary: 'bg-green-50 border-green-200';
    error: 'bg-red-50 border-red-200';
  };
};
```

## UI Components

### Loading States
```tsx
// LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

// Skeleton.tsx
interface SkeletonProps {
  width?: string;
  height?: string;
  variant: 'text' | 'rect' | 'circle';
}
```

### Error States
```tsx
// ErrorBoundary.tsx
interface ErrorBoundaryProps {
  fallback: React.ReactNode;
  children: React.ReactNode;
}

// Toast.tsx
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}
```

### Form Validation
```tsx
// Form.tsx
interface FormProps {
  onSubmit: (data: FormData) => void;
  validationSchema: Schema;
  initialValues: Record<string, any>;
}

// ValidationMessage.tsx
interface ValidationMessageProps {
  error: string | null;
  name: string;
}
```

## Design Patterns

### Search Patterns
```tsx
// SearchForm.tsx
interface SearchFormProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  error: string | null;
}

// ResultsList.tsx
interface ResultsListProps {
  items: Array<any>;
  loading: boolean;
  error: string | null;
  emptyMessage: string;
}
```

### Domain Display
```tsx
// DomainCard.tsx
interface DomainCardProps {
  domain: string;
  status: 'available' | 'taken';
  whoisData: WhoisData;
  analysisData: AnalysisData;
}

// WhoisResultCard.tsx
interface WhoisResultCardProps {
  data: WhoisData;
  loading: boolean;
  error: string | null;
}
```

### Bulk Operations
```tsx
// BulkCheckList.tsx
interface BulkCheckListProps {
  domains: string[];
  results: Record<string, DomainCheckResult>;
  onCheck: (domains: string[]) => void;
}

// ExportOptions.tsx
interface ExportOptionsProps {
  onExport: (format: 'csv' | 'excel' | 'pdf') => void;
}
```

## Admin Dashboard Components

### Monitoring
```tsx
// RequestStats.tsx
interface RequestStatsProps {
  stats: {
    total: number;
    success: number;
    errors: number;
  };
  period: string;
}

// PerformanceMetrics.tsx
interface PerformanceMetricsProps {
  metrics: {
    avgResponseTime: number;
    successRate: number;
    errorRate: number;
  };
}
```

### Configuration
```tsx
// WhoisConfig.tsx
interface WhoisConfigProps {
  settings: WhoisSettings;
  onSave: (settings: WhoisSettings) => void;
}

// RateLimitConfig.tsx
interface RateLimitConfigProps {
  limits: RateLimits;
  onSave: (limits: RateLimits) => void;
}
```

## Implementation Guidelines

### Loading States
1. Use skeleton loading for initial page loads
2. Use spinners for button states
3. Use progress indicators for longer operations

### Error Handling
1. Show error boundaries for critical failures
2. Use toasts for non-critical errors
3. Provide clear error messages

### Form Validation
1. Validate on blur and submit
2. Show error messages below fields
3. Highlight invalid fields

### Data Display
1. Use consistent card layouts
2. Show loading states for async data
3. Handle empty states gracefully

### Responsive Design
1. Use defined breakpoints
2. Test on all device sizes
3. Maintain readability at all sizes
