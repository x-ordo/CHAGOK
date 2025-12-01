/**
 * Authentication Hook
 * Handles login state, logout, and version-based session invalidation
 */

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/router';

// App version - update this when deploying new versions
// This will force logout on version mismatch
const APP_VERSION = '0.2.0';
const AUTH_TOKEN_KEY = 'authToken';
const APP_VERSION_KEY = 'appVersion';

export function useAuth() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check version and invalidate session if version changed
  const checkVersionAndAuth = useCallback(() => {
    const storedVersion = localStorage.getItem(APP_VERSION_KEY);
    const token = localStorage.getItem(AUTH_TOKEN_KEY);

    // If version changed, clear auth and force re-login
    if (storedVersion && storedVersion !== APP_VERSION) {
      console.log(`App version changed: ${storedVersion} -> ${APP_VERSION}. Logging out.`);
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.setItem(APP_VERSION_KEY, APP_VERSION);
      setIsAuthenticated(false);
      return false;
    }

    // Store current version
    localStorage.setItem(APP_VERSION_KEY, APP_VERSION);

    if (token) {
      setIsAuthenticated(true);
      return true;
    }

    setIsAuthenticated(false);
    return false;
  }, []);

  // Initialize auth state
  useEffect(() => {
    checkVersionAndAuth();
    setIsLoading(false);
  }, [checkVersionAndAuth]);

  // Logout handler
  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setIsAuthenticated(false);
    router.push('/login');
  }, [router]);

  // Get auth token
  const getToken = useCallback(() => {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  }, []);

  return {
    isAuthenticated,
    isLoading,
    logout,
    getToken,
    checkVersionAndAuth,
  };
}

export default useAuth;
