import React, { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";

/**
 * ProtectedRoute - Protects routes that require authentication
 * Checks for JWT token and validates it with the backend
 * Redirects to /login if not authenticated
 * Stores user ID from validation response
 */
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = checking, true/false = result
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      try {
        // Validate token with backend
        const response = await fetch("/auth/validate", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });

        if (response.ok) {
          const data = await response.json();
          
          // Store user ID from validation response
          if (data.user_id) {
            localStorage.setItem("user_id", data.user_id);
          }
          
          // Store other user info if provided
          if (data.username) {
            localStorage.setItem("username", data.username);
          }
          if (data.household_id) {
            localStorage.setItem("household_id", data.household_id);
          }
          
          setIsAuthenticated(true);
        } else {
          // Token is invalid or expired
          localStorage.removeItem("token");
          localStorage.removeItem("user_id");
          localStorage.removeItem("username");
          localStorage.removeItem("household_id");
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error("Auth validation error:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("username");
        localStorage.removeItem("household_id");
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, [location.pathname]);

  // Show nothing while checking authentication
  if (isAuthenticated === null) {
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--background-primary, #0a0f1a)",
          color: "var(--text-primary, #e0e7ff)",
          fontFamily: "'Exo 2', sans-serif",
          fontSize: "18px",
          letterSpacing: "2px"
        }}
      >
        AUTHENTICATING...
      </div>
    );
  }

  // Redirect to Sentinel Login if not authenticated
  if (!isAuthenticated) {
    // Get Sentinel Login URL from env or use default
    const sentinelLoginUrl = import.meta.env.VITE_SENTINEL_LOGIN_URL || 'http://localhost:5173';
    const currentUrl = window.location.origin + location.pathname;
    
    // Redirect to Sentinel Login with return URL
    const redirectUrl = `${sentinelLoginUrl}/patriot-login?redirect=${encodeURIComponent(currentUrl)}`;
    window.location.href = redirectUrl;
    
    // Return loading state while redirecting
    return (
      <div
        style={{
          position: "fixed",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--background-primary, #0a0f1a)",
          color: "var(--text-primary, #e0e7ff)",
          fontFamily: "'Exo 2', sans-serif",
          fontSize: "18px",
          letterSpacing: "2px"
        }}
      >
        REDIRECTING TO LOGIN...
      </div>
    );
  }

  // Render protected content
  return children;
};

export default ProtectedRoute;
