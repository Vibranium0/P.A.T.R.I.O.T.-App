import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshTimerId, setRefreshTimerId] = useState(null);

  // Decode JWT to get expiration time
  const decodeToken = (token) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  };

  // Schedule token refresh 5 minutes before expiration
  const scheduleTokenRefresh = useCallback((token) => {
    // Clear any existing timer
    if (refreshTimerId) {
      clearTimeout(refreshTimerId);
    }

    const payload = decodeToken(token);
    if (!payload || !payload.exp) {
      console.error('Invalid token payload');
      return;
    }

    const expiresAt = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    const refreshIn = expiresAt - now - 5 * 60 * 1000; // Refresh 5 minutes before expiration

    if (refreshIn > 0) {
      const timerId = setTimeout(() => {
        refreshAccessToken();
      }, refreshIn);
      setRefreshTimerId(timerId);
    } else {
      // Token already expired or will expire soon, refresh immediately
      refreshAccessToken();
    }
  }, [refreshTimerId]);

  // Refresh the access token using the HttpOnly cookie
  const refreshAccessToken = async () => {
    try {
      const rememberMe = localStorage.getItem('remember_me') === 'true';
      
      const response = await fetch('/auth/refresh', {
        method: 'POST',
        credentials: 'include', // Include HttpOnly cookie
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ remember_me: rememberMe }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      setAccessToken(data.access_token);
      scheduleTokenRefresh(data.access_token);
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Clear auth state on refresh failure
      logout();
    }
  };

  // Login function - stores access token in memory
  const login = (token, userData) => {
    setAccessToken(token);
    setUser(userData);
    scheduleTokenRefresh(token);
  };

  // Logout function - clears memory and calls backend to clear cookie
  const logout = async () => {
    try {
      // Call backend to clear HttpOnly cookie
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    }

    // Clear memory state
    setAccessToken(null);
    setUser(null);
    if (refreshTimerId) {
      clearTimeout(refreshTimerId);
      setRefreshTimerId(null);
    }
    
    // Clear remember_me preference
    localStorage.removeItem('remember_me');
  };

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Try to refresh token from HttpOnly cookie
        await refreshAccessToken();
      } catch (error) {
        console.log('No valid session found');
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Cleanup timers on unmount
    return () => {
      if (refreshTimerId) {
        clearTimeout(refreshTimerId);
      }
    };
  }, []);

  const value = {
    accessToken,
    user,
    loading,
    login,
    logout,
    refreshAccessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
