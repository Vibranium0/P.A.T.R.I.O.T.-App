import React from 'react';
import { useNavigate } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary';
import Button from '../Button/Button';
import styles from './ErrorBoundary.module.css';

/**
 * AuthErrorBoundary - Specialized error boundary for authentication-related errors
 * Provides auth-specific fallback UI and recovery options
 */

const AuthErrorFallback = ({ error, resetError }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      // Call backend to clear HttpOnly cookie
      await fetch('http://localhost:5001/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout request failed:', error);
    }
    
    // Clear remember_me preference
    localStorage.removeItem('remember_me');
    
    // Redirect to login (this will clear memory state via page reload)
    window.location.href = '/patriot-login';
  };

  const isAuthError = error?.message?.toLowerCase().includes('auth') ||
                      error?.message?.toLowerCase().includes('token') ||
                      error?.message?.toLowerCase().includes('unauthorized');

  return (
    <div className={styles.errorContainer}>
      <div className={styles.errorCard}>
        <div className={styles.errorIcon}>🔐</div>
        <h1 className={styles.errorTitle}>
          {isAuthError ? 'Authentication Error' : 'Something went wrong'}
        </h1>
        <p className={styles.errorMessage}>
          {isAuthError 
            ? 'There was a problem with your authentication. Please log in again.'
            : 'An unexpected error occurred in the authentication system.'}
        </p>
        
        {process.env.NODE_ENV === 'development' && error && (
          <details className={styles.errorDetails}>
            <summary>Error Details (Development Only)</summary>
            <div className={styles.errorStack}>
              <p><strong>Error:</strong> {error.toString()}</p>
            </div>
          </details>
        )}
        
        <div className={styles.errorActions}>
          {isAuthError ? (
            <Button 
              variant="primary" 
              onClick={handleLogout}
            >
              Return to Login
            </Button>
          ) : (
            <>
              <Button 
                variant="primary" 
                onClick={resetError}
              >
                Try Again
              </Button>
              <Button 
                variant="secondary" 
                onClick={handleLogout}
              >
                Logout
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * AuthErrorBoundary wrapper component
 */
const AuthErrorBoundary = ({ children }) => {
  return (
    <ErrorBoundary
      fallback={(error, resetError) => (
        <AuthErrorFallback error={error} resetError={resetError} />
      )}
      title="Authentication Error"
      message="There was a problem with your authentication session."
    >
      {children}
    </ErrorBoundary>
  );
};

export default AuthErrorBoundary;
