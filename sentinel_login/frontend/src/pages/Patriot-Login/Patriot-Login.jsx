import React, { useState, useEffect } from "react";
import { Helmet } from "react-helmet";
import { initBackgroundLogoRecalibration } from "shared/utils/background-logo-recalibration";
import patriotTheme from "./PatriotLoginTheme.module.css";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Patriot-Login.module.css";
import logo from '../../assets/patriot/logo.png';
import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";
import PasswordTextBox from "shared/ui/components/PasswordTextBox";
import AnimatedCard from "shared/ui/components/AnimatedCard";
import Checkbox from "shared/ui/components/Checkbox/Checkbox";
import Card from "shared/ui/components/Card/Card";
import ShakeOnError from "shared/ui/components/ShakeOnError";
import { PageTitle } from "shared/ui/components/PageTitle";
import { useAuth } from "../../contexts/AuthContext";

import { useTransitionOverlay } from "../../TransitionOverlayContext.jsx";


const PatriotLogin = () => {
  const [lastRedirectUrl, setLastRedirectUrl] = useState("");
  // DEBUG: Show JWT token from localStorage and extracted token from URL
  const jwtToken = typeof window !== 'undefined' ? localStorage.getItem('token') : '';
  const rawQuery = typeof window !== 'undefined' ? window.location.search : '';
  let extractedToken = '';
  if (typeof window !== 'undefined') {
    const searchParams = new URLSearchParams(window.location.search);
    extractedToken = searchParams.get('token') || searchParams.get('jwt') || searchParams.get('access_token') || '';
  }
  const location = useLocation();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  // Use app-level transition overlay
  const { triggerTransition, active: transitionActive } = useTransitionOverlay();
  const navigate = useNavigate();
  const { login } = useAuth();

  // Get redirect URL from query params or location state
  // Priority: 1. Query param ?redirect= 2. Location state 3. Default to P.A.T.R.I.O.T. dashboard
  const getRedirectUrl = () => {
    const searchParams = new URLSearchParams(location.search);
    const redirectParam = searchParams.get('redirect');
    if (redirectParam) {
      // Decode the redirect URL
      return decodeURIComponent(redirectParam);
    }
    if (location.state && location.state.from) {
      return location.state.from;
    }
    // Default: always redirect to Patriot dashboard on LAN IP for iPhone compatibility
    return "http://192.168.4.44:5173/dashboard";
  };

  // Initialize background logo recalibration on mount
  useEffect(() => {
    const cleanup = initBackgroundLogoRecalibration();
    return cleanup;
  }, []);

  // Load remember_me preference on mount
  useEffect(() => {
    const savedRememberMe = localStorage.getItem("remember_me") === "true";
    setRememberMe(savedRememberMe);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    // Client-side validation
    if (!identifier.trim()) {
      setError("Username is required");
      return;
    }

    if (identifier.trim().length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    if (!password) {
      setError("Password is required");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // Include cookies for refresh token
        body: JSON.stringify({
          username: identifier.trim(),
          password,
          remember_me: rememberMe
        })
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        console.log('Login successful, access_token:', data.access_token);
        // Store access token in memory via AuthContext (not localStorage)
        login(data.access_token, {
          username: data.username,
          email: data.email,
          household_id: data.household_id
        });
        // Only store remember_me preference (not sensitive)
        localStorage.setItem("remember_me", rememberMe ? "true" : "false");
        // Get the redirect URL
        let redirectUrl = getRedirectUrl();
        console.log('About to redirect, redirectUrl:', redirectUrl);
        setTimeout(() => {
          // If redirectUrl is a Patriot app URL, always append token as top-level param
          let decodedUrl = redirectUrl;
          if (redirectUrl.startsWith('http')) {
            decodedUrl = redirectUrl;
          } else {
            try {
              decodedUrl = decodeURIComponent(redirectUrl);
            } catch (e) {
              decodedUrl = redirectUrl;
            }
          }
          // Now append token to decodedUrl
          const urlObj = new URL(decodedUrl, window.location.origin);
          if (!urlObj.searchParams.get('token') && !urlObj.searchParams.get('jwt') && !urlObj.searchParams.get('access_token')) {
            urlObj.searchParams.set('token', data.access_token);
            decodedUrl = urlObj.toString();
          }
          setLastRedirectUrl(decodedUrl); // Show on UI for debugging
          // If redirecting to Patriot app (external), use window.location.href
          if (decodedUrl.includes('5173') || decodedUrl.includes('patriot') || decodedUrl.includes('dashboard')) {
            window.location.href = decodedUrl;
          } else {
            window.location.href = decodedUrl;
          }
        }, 1200);
      } else {
        setError(data.error || "Login failed. Check credentials.");
      }
    } catch (err) {
      setError("Network error. Try again.");
    }
    setLoading(false);
  };

  return (
    <>
      <Helmet>
        <title>Patriot Login</title>
        <link rel="icon" type="image/png" href="/favicon-patriot.png" />
      </Helmet>

      <div className={styles.background}>
        {/* DEBUG UI: JWT Token and Query Display */}
        <div style={{
          position: 'fixed',
          top: 8,
          right: 8,
          zIndex: 9999,
          background: 'rgba(0,0,0,0.85)',
          color: '#fff',
          padding: '12px 16px',
          borderRadius: '8px',
          fontSize: '13px',
          maxWidth: '90vw',
          wordBreak: 'break-all',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
        }}>
          <strong>window.location.search:</strong>
          <div>{rawQuery || 'No query string'}</div>
          <strong>Extracted Token from URL:</strong>
          <div>{extractedToken || 'No token in query'}</div>
          <strong>JWT Token in localStorage:</strong>
          <div>{jwtToken || 'No token found'}</div>
        </div>
        {/* Show logo and form (hide during active transitions) */}
        {/* DEBUG: Show last redirect URL visually for mobile troubleshooting */}
        {lastRedirectUrl && (
          <div style={{
            position: 'fixed',
            bottom: 8,
            left: 8,
            zIndex: 9999,
            background: 'rgba(0,0,0,0.85)',
            color: '#fff',
            padding: '12px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            maxWidth: '90vw',
            wordBreak: 'break-all',
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}>
            <strong>Last Redirect URL:</strong>
            <div>{lastRedirectUrl}</div>
          </div>
        )}
        <div style={{
          opacity: transitionActive ? 0 : 1,
          transition: 'opacity 0.3s ease',
          position: 'fixed',
          inset: 0,
          zIndex: 1000,
          backgroundColor: 'transparent',
          pointerEvents: 'auto'
        }}>
          <div className={styles.logoLayer}>
            <img
              src={logo}
              alt="Sentinel Logo"
              className={styles.logo}
              data-role="background-logo"
              draggable={false}
              aria-hidden="true"
            />
          </div>
          <div className={styles.centerOverlay}>
            <div className={styles.formLayer}>
              <div className={styles.cardWrapper}>
                <AnimatedCard>
                  <Card style={{
                    border: '5px solid red !important',
                    backgroundColor: 'rgba(255, 0, 0, 0.5) !important',
                    minHeight: '400px',
                    minWidth: '400px'
                  }}>
                    <PageTitle>
                      <span style={{ display: 'block', marginBottom: 36 }}>P.A.T.R.I.O.T.</span>
                    </PageTitle>
                    <motion.p
                      className={styles.subtitle}
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.45, ease: "easeOut", delay: 0.15 }}
                    >
                      Personalized Accounting & Tactical Resource Intelligence for Organized Tracking
                    </motion.p>
                    <form
                      className={styles.loginForm}
                      onSubmit={handleSubmit}
                      noValidate
                      aria-describedby={error ? "login-error" : undefined}
                      style={{
                        opacity: loading ? 0.6 : 1,
                        pointerEvents: loading ? 'none' : 'auto',
                        transition: 'opacity 0.3s ease'
                      }}
                    >
                      <TextBox
                        id="login-username"
                        value={identifier}
                        onChange={setIdentifier}
                        placeholder="Username"
                        type="text"
                        autoComplete="username"
                        autoFocus
                        maxLength={80}
                        aria-required="true"
                        aria-invalid={!!error && error.toLowerCase().includes('username')}
                      />
                      <PasswordTextBox
                        id="login-password"
                        value={password}
                        onChange={setPassword}
                        placeholder="Password"
                        autoComplete="current-password"
                        aria-required="true"
                        aria-invalid={!!error && error.toLowerCase().includes('password')}
                        aria-describedby={error ? "login-error" : undefined}
                      />
                      {error && (
                        <ShakeOnError trigger={error}>
                          <div
                            id="login-error"
                            role="alert"
                            aria-live="assertive"
                            style={{
                              color: "var(--danger)",
                              fontWeight: 700,
                              fontFamily: "'Share Tech Mono', 'Exo 2', monospace",
                              fontSize: 22,
                              letterSpacing: 2,
                              textShadow: "0 0 8px var(--danger), 0 0 22px var(--glow-danger)",
                              marginBottom: 8,
                              textAlign: "center",
                              filter: "drop-shadow(0 0 8px var(--glow-danger))"
                            }}
                          >
                            {error.toUpperCase()}
                          </div>
                        </ShakeOnError>
                      )}
                      {success && (
                        <div
                          role="status"
                          aria-live="polite"
                          style={{
                            color: "var(--success)",
                            fontWeight: 700,
                            fontFamily: "'Share Tech Mono', 'Exo 2', monospace",
                            fontSize: 22,
                            letterSpacing: 2,
                            textShadow: "0 0 8px var(--success), 0 0 22px var(--glow-success)",
                            marginBottom: 8,
                            textAlign: "center",
                            filter: "drop-shadow(0 0 8px var(--glow-success))"
                          }}
                        >
                          ACCESS GRANTED
                        </div>
                      )}

                      {/* Remember Me Checkbox */}
                      <Checkbox
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                        label="Remember Me"
                        variant="success"
                        icon="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                      />

                      <Button
                        type="submit"
                        disabled={loading || success}
                        aria-busy={loading}
                        style={{
                          cursor: (loading || success) ? 'not-allowed' : 'pointer',
                          marginTop: '6px'
                        }}
                      >
                        {loading ? "Logging in..." : "Login"}
                      </Button>
                    </form>
                    <div style={{ marginTop: 18, textAlign: "center", fontFamily: "'Exo 2', 'Exo2', sans-serif" }}>
                      <a
                        href="#"
                        style={{
                          color: "var(--primary)",
                          textDecoration: "underline",
                          fontSize: 15,
                          cursor: "pointer",
                          marginBottom: 8,
                          display: "inline-block",
                          fontFamily: "inherit"
                        }}
                        onClick={e => {
                          e.preventDefault();
                          triggerTransition(() => navigate("/reset-password"), "right");
                        }}
                      >
                        Forgot password?
                      </a>
                      <br />
                      <span style={{
                        color: "var(--text-secondary)",
                        fontSize: 15,
                        fontFamily: "inherit"
                      }}>
                        Don&apos;t have an account?{' '}
                        <a
                          href="#"
                          style={{
                            color: "var(--primary)",
                            textDecoration: "underline",
                            cursor: "pointer",
                            fontFamily: "inherit"
                          }}
                          onClick={e => {
                            e.preventDefault();
                            triggerTransition(() => navigate("/register", { state: { from: "/patriot-login" } }), "right");
                          }}
                        >
                          Register
                        </a>
                      </span>
                    </div>
                  </Card>
                </AnimatedCard>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PatriotLogin;
