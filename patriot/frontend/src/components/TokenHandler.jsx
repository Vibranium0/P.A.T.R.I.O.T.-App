import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * TokenHandler - Extracts token from URL query params after Sentinel login redirect
 * Stores token in localStorage and redirects to the intended destination
 * 
 * Usage: Wrap your app or add to routing structure
 */
const TokenHandler = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Always check for token in URL on mount and on location changes
  useEffect(() => {
    const handleToken = () => {
      const rawQuery = window.location.search;
      const searchParams = new URLSearchParams(rawQuery);
      const token = searchParams.get('token') || searchParams.get('jwt') || searchParams.get('access_token');
      console.log('[TokenHandler] window.location.search:', rawQuery);
      console.log('[TokenHandler] Extracted token:', token);
      if (token) {
        localStorage.setItem('token', token);
        searchParams.delete('token');
        searchParams.delete('jwt');
        searchParams.delete('access_token');
        const newSearch = searchParams.toString();
        const newPath = window.location.pathname + (newSearch ? `?${newSearch}` : '');
        window.history.replaceState({}, '', newPath);
        console.log('[TokenHandler] Token set in localStorage, reloading...');
        setTimeout(() => {
          window.location.reload();
        }, 250);
      }
    };
    handleToken();
  }, [location, navigate]);

  return children;
};

export default TokenHandler;
