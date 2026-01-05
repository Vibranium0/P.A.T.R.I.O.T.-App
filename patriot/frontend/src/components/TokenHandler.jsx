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

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('token');

    if (token) {
      // Store the token from Sentinel login
      localStorage.setItem('token', token);

      // Remove token from URL for security (don't keep it in browser history)
      searchParams.delete('token');
      
      // Construct clean URL without token parameter
      const newSearch = searchParams.toString();
      const newPath = location.pathname + (newSearch ? `?${newSearch}` : '');
      
      // Replace current URL to remove token from history
      window.history.replaceState({}, '', newPath);

      // Optional: Show success message
      console.log('✅ Authenticated successfully via Sentinel Login');
      
      // If we're on root or login page, redirect to dashboard
      if (location.pathname === '/' || location.pathname === '/login') {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [location, navigate]);

  return children;
};

export default TokenHandler;
