/**
 * useAuth - Custom hook to access current user authentication data
 * Provides access to user_id, username, and household_id from localStorage
 */
import { useCallback } from 'react';

export const useAuth = () => {
  const getUserId = useCallback(() => {
    return localStorage.getItem('user_id');
  }, []);

  const getUsername = useCallback(() => {
    return localStorage.getItem('username');
  }, []);

  const getHouseholdId = useCallback(() => {
    return localStorage.getItem('household_id');
  }, []);

  const getToken = useCallback(() => {
    return localStorage.getItem('token');
  }, []);

  const isAuthenticated = useCallback(() => {
    return !!localStorage.getItem('token');
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('household_id');
  }, []);

  return {
    userId: getUserId(),
    username: getUsername(),
    householdId: getHouseholdId(),
    token: getToken(),
    isAuthenticated: isAuthenticated(),
    logout
  };
};

export default useAuth;
