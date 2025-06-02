import { useState, useCallback, useRef, useEffect } from 'react';
import { useApiError } from './useApiError';

type FormSubmitHandler<T> = (data: T) => Promise<any>;

export function useFormSubmit<T = any>(
  submitHandler: FormSubmitHandler<T>,
  options: {
    onSuccess?: (data: any) => void;
    onError?: (error: Error) => void;
    successMessage?: string;
    errorMessage?: string;
    resetFormOnSuccess?: boolean;
  } = {}
) {
  const {
    onSuccess,
    onError,
    successMessage,
    errorMessage,
    resetFormOnSuccess = false,
  } = options;
  
  const { showError } = useApiError();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitCount, setSubmitCount] = useState(0);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const formRef = useRef<HTMLFormElement>(null);
  
  // Reset success state after a delay
  useEffect(() => {
    if (isSuccess) {
      const timer = setTimeout(() => {
        setIsSuccess(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [isSuccess]);
  
  // Handle form submission
  const handleSubmit = useCallback(async (data: T) => {
    setIsSubmitting(true);
    setError(null);
    setSubmitCount(prev => prev + 1);
    
    try {
      const result = await submitHandler(data);
      
      // Call success handler if provided
      if (onSuccess) {
        onSuccess(result);
      }
      
      // Show success message if provided
      if (successMessage) {
        // You can replace this with your preferred notification system
        console.log(successMessage);
      }
      
      // Reset form if needed
      if (resetFormOnSuccess && formRef.current) {
        formRef.current.reset();
      }
      
      setIsSuccess(true);
      return result;
    } catch (error) {
      const err = error as Error;
      
      // Call error handler if provided
      if (onError) {
        onError(err);
      }
      
      // Show error message
      const message = errorMessage || err.message || 'An error occurred';
      showError(err, { errorMessage: message });
      
      setError(err);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  }, [submitHandler, onSuccess, onError, successMessage, errorMessage, resetFormOnSuccess, showError]);
  
  // Reset form state
  const reset = useCallback(() => {
    setIsSubmitting(false);
    setError(null);
    setIsSuccess(false);
    setSubmitCount(0);
    
    if (formRef.current) {
      formRef.current.reset();
    }
  }, []);
  
  return {
    // Form state
    isSubmitting,
    isSuccess,
    error,
    submitCount,
    
    // Form ref
    formRef,
    
    // Handlers
    handleSubmit,
    reset,
    
    // Helper methods
    setError,
  };
}

// Hook for handling form field changes
export function useFormField<T extends Record<string, any>>(initialState: T) {
  const [formData, setFormData] = useState<T>(initialState);
  
  const handleChange = useCallback(<K extends keyof T>(
    field: K,
    value: T[K]
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  }, []);
  
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      
      // Handle checkboxes and radio buttons
      if (e.target.type === 'checkbox' && 'checked' in e.target) {
        setFormData(prev => ({
          ...prev,
          [name]: (e.target as HTMLInputElement).checked,
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          [name]: type === 'number' && value !== '' ? Number(value) : value,
        }));
      }
    },
    []
  );
  
  const resetForm = useCallback((newState?: T) => {
    setFormData(newState || initialState);
  }, [initialState]);
  
  return {
    formData,
    setFormData,
    handleChange,
    handleInputChange,
    resetForm,
  };
}

// Hook for handling form validation
export function useFormValidation<T extends Record<string, any>>(
  initialState: T,
  validate: (values: T) => Record<keyof T, string>,
  onSubmit: (values: T) => void | Promise<void>
) {
  const [values, setValues] = useState<T>(initialState);
  const [errors, setErrors] = useState<Record<keyof T, string>>({} as Record<keyof T, string>);
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Validate form when values or touched state changes
  useEffect(() => {
    if (Object.keys(touched).length > 0) {
      setErrors(validate(values));
    }
  }, [values, touched, validate]);
  
  // Check if form is valid
  const isValid = useCallback(() => {
    return Object.keys(errors).length === 0 || Object.values(errors).every(x => !x);
  }, [errors]);
  
  // Handle input change
  const handleChange = useCallback(<K extends keyof T>(
    field: K,
    value: T[K]
  ) => {
    setValues(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Mark field as touched
    setTouched(prev => ({
      ...prev,
      [field]: true,
    }));
  }, []);
  
  // Handle blur event
  const handleBlur = useCallback((field: keyof T) => {
    setTouched(prev => ({
      ...prev,
      [field]: true,
    }));
  }, []);
  
  // Handle form submission
  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    
    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce((acc, key) => ({
      ...acc,
      [key]: true,
    }), {} as Record<keyof T, boolean>);
    
    setTouched(allTouched);
    
    // Validate form
    const formErrors = validate(values);
    setErrors(formErrors);
    
    // If form is valid, submit it
    if (Object.values(formErrors).every(x => !x)) {
      setIsSubmitting(true);
      
      try {
        await onSubmit(values);
      } finally {
        setIsSubmitting(false);
      }
    }
  }, [onSubmit, validate, values]);
  
  // Reset form
  const resetForm = useCallback((newValues?: T) => {
    setValues(newValues || initialState);
    setErrors({} as Record<keyof T, string>);
    setTouched({});
  }, [initialState]);
  
  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid: isValid(),
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setValues,
    setErrors,
    setTouched,
    setIsSubmitting,
  };
}
