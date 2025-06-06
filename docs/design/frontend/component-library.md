# Frontend Component Library

## Atomic Design Structure

### Atoms
```tsx
// components/atoms/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

// components/atoms/Input.tsx
interface InputProps {
  type?: 'text' | 'number' | 'email';
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  onChange?: (value: string) => void;
}

// components/atoms/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

// components/atoms/Badge.tsx
interface BadgeProps {
  variant?: 'success' | 'error' | 'warning' | 'info';
  children: React.ReactNode;
}

// components/atoms/Icon.tsx
interface IconProps {
  name: string;
  size?: number;
  color?: string;
}
```

### Molecules
```tsx
// components/molecules/SearchForm.tsx
interface SearchFormProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
  error: string | null;
  initialQuery?: string;
}

// components/molecules/DomainCard.tsx
interface DomainCardProps {
  domain: string;
  status: 'available' | 'taken';
  whoisData: WhoisData;
  analysisData: AnalysisData;
  onSelect: (domain: string) => void;
}

// components/molecules/WhoisResultCard.tsx
interface WhoisResultCardProps {
  data: WhoisData;
  loading: boolean;
  error: string | null;
  onRetry?: () => void;
}

// components/molecules/BulkCheckList.tsx
interface BulkCheckListProps {
  domains: string[];
  results: Record<string, DomainCheckResult>;
  onCheck: (domains: string[]) => void;
  onExport: (format: 'csv' | 'excel' | 'pdf') => void;
}

// components/molecules/AnalysisPanel.tsx
interface AnalysisPanelProps {
  domain: string;
  data: AnalysisData;
  loading: boolean;
  error: string | null;
}
```

### Organisms
```tsx
// components/organisms/DomainSearchSection.tsx
interface DomainSearchSectionProps {
  onSearch: (query: string) => void;
  onAdvancedSearch: () => void;
  onBulkCheck: () => void;
}

// components/organisms/ResultsSection.tsx
interface ResultsSectionProps {
  results: DomainSearchResult[];
  loading: boolean;
  error: string | null;
  onDomainSelect: (domain: string) => void;
}

// components/organisms/AnalysisSection.tsx
interface AnalysisSectionProps {
  domain: string;
  data: AnalysisData;
  loading: boolean;
  error: string | null;
}

// components/organisms/BulkCheckSection.tsx
interface BulkCheckSectionProps {
  domains: string[];
  results: Record<string, DomainCheckResult>;
  onCheck: (domains: string[]) => void;
  onExport: (format: 'csv' | 'excel' | 'pdf') => void;
}
```

## UI Patterns

### Loading States
```tsx
// components/ui/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

// components/ui/Skeleton.tsx
interface SkeletonProps {
  width?: string;
  height?: string;
  variant: 'text' | 'rect' | 'circle';
}

// components/ui/ProgressIndicator.tsx
interface ProgressIndicatorProps {
  value: number;
  max: number;
  size?: 'sm' | 'md' | 'lg';
}
```

### Error States
```tsx
// components/ui/ErrorBoundary.tsx
interface ErrorBoundaryProps {
  fallback: React.ReactNode;
  children: React.ReactNode;
}

// components/ui/Toast.tsx
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

// components/ui/ErrorMessage.tsx
interface ErrorMessageProps {
  error: string | null;
  onRetry?: () => void;
}
```

### Form Validation
```tsx
// components/ui/Form.tsx
interface FormProps {
  onSubmit: (data: FormData) => void;
  validationSchema: Schema;
  initialValues: Record<string, any>;
}

// components/ui/ValidationMessage.tsx
interface ValidationMessageProps {
  error: string | null;
  name: string;
}

// components/ui/FormSection.tsx
interface FormSectionProps {
  title: string;
  children: React.ReactNode;
}
```

## Design Tokens

### Colors
```typescript
const colors = {
  primary: {
    DEFAULT: '#2563eb',
    hover: '#1d4ed8',
    contrast: '#ffffff',
  },
  secondary: {
    DEFAULT: '#16a34a',
    hover: '#15803d',
    contrast: '#ffffff',
  },
  accent: {
    DEFAULT: '#db2777',
    hover: '#be185d',
    contrast: '#ffffff',
  },
  neutral: {
    background: '#ffffff',
    surface: '#f9fafb',
    border: '#e5e7eb',
    text: '#1f2937',
    textSecondary: '#6b7280',
  },
};
```

### Typography
```typescript
const typography = {
  fontSizes: {
    h1: '2.25rem',
    h2: '1.875rem',
    h3: '1.5rem',
    h4: '1.25rem',
    body: '1rem',
    small: '0.875rem',
  },
  fontWeights: {
    regular: 400,
    medium: 500,
    bold: 700,
  },
  lineHeights: {
    normal: 1.5,
    tight: 1.25,
    loose: 2,
  },
};
```

### Spacing
```typescript
const spacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
  24: '6rem',
};
```

## Implementation Guidelines

### Component Usage
1. Always use predefined variants
2. Follow consistent naming conventions
3. Use proper TypeScript interfaces
4. Implement proper error handling
5. Add proper loading states

### State Management
1. Use React Query for data fetching
2. Use Zustand for global state
3. Use React Context for local state
4. Implement proper caching
5. Handle loading states

### Error Handling
1. Use Error Boundaries for critical errors
2. Show Toast notifications for user feedback
3. Provide clear error messages
4. Implement retry mechanisms
5. Log errors properly

### Performance
1. Implement proper memoization
2. Use virtual scrolling for large lists
3. Implement proper caching
4. Optimize images and assets
5. Use lazy loading

## Best Practices

### Accessibility
1. Use proper ARIA labels
2. Implement keyboard navigation
3. Follow color contrast guidelines
4. Use semantic HTML
5. Test with screen readers

### Performance
1. Implement proper caching
2. Use lazy loading
3. Optimize images
4. Minimize re-renders
5. Use virtual scrolling

### Maintainability
1. Follow consistent code style
2. Add proper documentation
3. Write unit tests
4. Implement proper error handling
5. Follow component guidelines
