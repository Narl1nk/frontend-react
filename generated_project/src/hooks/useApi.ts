import { useState, useCallback } from 'react';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/**
 * Custom React hook for managing async API calls with type safety.
 * @param apiFunction The asynchronous function making the API call.
 */

export function useApi<T>(apiFunction: (...args: any[]) => Promise<T>): {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
} {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  // Execute the API function and manage the loading and error states
  const execute = useCallback(async (...args: any[]) => {
    setState({ ...state, loading: true });
    try {
      const data = await apiFunction(...args);
      setState({ data, loading: false, error: null });
      return data;
    } catch (err: any) {
      setState({ data: null, loading: false, error: err.message || 'Error' });
      return null;
    }
  }, [apiFunction]);

  // Reset function to clear state
  const reset = () => {
    setState({ data: null, loading: false, error: null });
  };

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    execute,
    reset
  };
}