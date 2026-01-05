import React from 'react';
import styles from './ErrorBoundary.module.css';
import Button from '../Button/Button';

/**
 * ErrorBoundary - Catches JavaScript errors in child components
 * Displays a fallback UI instead of crashing the entire app
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
    
    // Store error details in state
    this.setState({
      error,
      errorInfo
    });

    // In production, you could send this to an error reporting service
    // logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ 
      hasError: false,
      error: null,
      errorInfo: null
    });
    
    // Optionally reload the page
    if (this.props.resetOnError) {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI provided by parent
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className={styles.errorContainer}>
          <div className={styles.errorCard}>
            <div className={styles.errorIcon}>⚠️</div>
            <h1 className={styles.errorTitle}>
              {this.props.title || 'Something went wrong'}
            </h1>
            <p className={styles.errorMessage}>
              {this.props.message || 'An unexpected error occurred. Please try again.'}
            </p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className={styles.errorDetails}>
                <summary>Error Details (Development Only)</summary>
                <div className={styles.errorStack}>
                  <p><strong>Error:</strong> {this.state.error.toString()}</p>
                  {this.state.errorInfo && (
                    <pre>{this.state.errorInfo.componentStack}</pre>
                  )}
                </div>
              </details>
            )}
            
            <div className={styles.errorActions}>
              <Button 
                variant="primary" 
                onClick={this.handleReset}
              >
                Try Again
              </Button>
              <Button 
                variant="secondary" 
                onClick={() => window.location.href = '/'}
              >
                Go Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
