/**
 * Custom React Hooks for Service Management System
 * useAuth, useApi, useLocation, etc.
 */

import { useState, useCallback, useEffect, useContext, createContext } from 'react';
import axios from 'axios';
import { useQuery, useMutation } from 'react-query';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Hook: useAuth
 * Manages authentication state and operations
 */
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load user from token on mount
  useEffect(() => {
    if (token) {
      loadUserProfile();
    }
  }, [token]);

  const loadUserProfile = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/auth/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (err) {
      setError(err.message);
      setToken(null);
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${API_URL}/auth/login`, {
        username,
        password
      });
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('authToken', access_token);
      return true;
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
  }, []);

  const register = useCallback(async (userData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${API_URL}/auth/register`, userData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    user,
    token,
    loading,
    error,
    login,
    logout,
    register,
    isAuthenticated: !!token
  };
};

/**
 * Hook: useApi
 * Generic API request hook with error handling and loading states
 */
export const useApi = (url, options = {}) => {
  const token = localStorage.getItem('authToken');

  return useQuery(
    [url, options],
    async () => {
      const response = await axios.get(`${API_URL}${url}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          ...options.headers
        },
        ...options
      });
      return response.data;
    },
    {
      enabled: !!token,
      staleTime: options.staleTime || 1000 * 60 * 5, // 5 minutes
      cacheTime: options.cacheTime || 1000 * 60 * 10, // 10 minutes
      retry: options.retry !== false,
      onError: (error) => {
        console.error('API Error:', error);
      }
    }
  );
};

/**
 * Hook: useLocation
 * Get and track user/technician location
 */
export const useLocation = (options = {}) => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported');
      setLoading(false);
      return;
    }

    const success = (position) => {
      const { latitude, longitude } = position.coords;
      setLocation({ latitude, longitude });
      setLoading(false);
    };

    const handleError = (err) => {
      setError(err.message);
      setLoading(false);
    };

    const watchId = navigator.geolocation.watchPosition(
      success,
      handleError,
      {
        enableHighAccuracy: options.highAccuracy !== false,
        timeout: options.timeout || 10000,
        maximumAge: options.maximumAge || 0
      }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  return { location, error, loading };
};

/**
 * Hook: useLocalStorage
 * Persist state to localStorage
 */
export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
};

/**
 * Hook: useAsync
 * Handle async operations with loading and error states
 */
export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState(immediate ? 'pending' : 'idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async () => {
    setStatus('pending');
    setData(null);
    setError(null);
    try {
      const response = await asyncFunction();
      setData(response);
      setStatus('success');
      return response;
    } catch (err) {
      setError(err);
      setStatus('error');
      throw err;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (!immediate) return;
    execute();
  }, [execute, immediate]);

  return { execute, status, data, error };
};

/**
 * Hook: useDebounce
 * Debounce value changes
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Hook: useFetch
 * Simple fetch hook with refetch capability
 */
export const useFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const token = localStorage.getItem('authToken');

  const refetch = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}${url}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          ...options.headers
        },
        ...options
      });
      setData(response.data);
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [url, token, options]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
};

/**
 * Hook: useMutateApi
 * Handle POST, PUT, DELETE requests
 */
export const useMutateApi = (method = 'POST') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const token = localStorage.getItem('authToken');

  const mutate = useCallback(async (url, data = null, options = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios({
        method,
        url: `${API_URL}${url}`,
        data,
        headers: {
          Authorization: `Bearer ${token}`,
          ...options.headers
        },
        ...options
      });
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Operation failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [token, method]);

  return { mutate, loading, error };
};

export default {
  useAuth,
  useApi,
  useLocation,
  useLocalStorage,
  useAsync,
  useDebounce,
  useFetch,
  useMutateApi
};
