import React, { useState, useEffect } from "react";
import { initBackgroundLogoRecalibration } from "shared/utils/background-logo-recalibration";
import { Helmet } from "react-helmet";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./PasswordReset.module.css";
import sentinelTheme from "./SentinelTheme.module.css";
import logo from '../../assets/sentinel-login/Sentinel Systems.png';

import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";
import PasswordTextBox from "shared/ui/components/PasswordTextBox";
import SelectBox from "shared/ui/components/SelectBox";
import AnimatedCard from "shared/ui/components/AnimatedCard";
import { useTransitionOverlay } from "../../TransitionOverlayContext.jsx";
import ShakeOnError from "shared/ui/components/ShakeOnError";
import Card from "shared/ui/components/Card/Card";
import { PageTitle } from "shared/ui/components/PageTitle";
import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";

const PasswordReset = () => {
  const location = useLocation();
  // Default to /patriot-login if not provided
  const fromLogin = location.state?.from || "/patriot-login";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const [step, setStep] = useState(1); // Step 1: Enter username, Step 2: Answer security question and reset password

  const navigate = useNavigate();
  const { triggerTransition } = useTransitionOverlay();

  // Initialize background logo recalibration on mount
  useEffect(() => {
    const cleanup = initBackgroundLogoRecalibration();
    return cleanup;
  }, []);

  // Fetch security question when username is provided
  const handleFetchSecurityQuestion = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!username.trim()) {
      setError("Username is required");
      return;
    }
    
    if (username.trim().length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    setLoadingQuestion(true);
    
    try {
      const res = await fetch("/auth/password-reset/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: username.trim() })
      });
      
      const data = await res.json();
      
      if (res.ok && data.security_question) {
        setSecurityQuestion(data.security_question);
        setStep(2);
      } else {
        setError(data.error || "User not found or no security question set");
      }
    } catch (err) {
      console.error("Error fetching security question:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Client-side validation - check all fields and collect errors
    const missingFields = [];

    if (!password) {
      missingFields.push("New Password");
    } else if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (!confirmPassword) {
      missingFields.push("Confirm Password");
    } else if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!securityAnswer.trim()) {
      missingFields.push("Security Answer");
    } else if (securityAnswer.trim().length < 2) {
      setError("Security answer must be at least 2 characters");
      return;
    }

    // If there are missing fields, format the error message
    if (missingFields.length > 0) {
      setError(`Required fields: ${missingFields.join(", ")}`);
      return;
    }

    setLoading(true);
    
    try {
      const res = await fetch("/auth/password-reset/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          username: username.trim(), 
          new_password: password,
          security_answer: securityAnswer.trim()
        })
      });
      
      const data = await res.json();
      
      if (res.ok && data.message) {
        setSuccess("Password reset successful! Redirecting...");
        setTimeout(() => {
          triggerTransition(() => navigate(fromLogin), "left");
        }, 1500);
      } else {
        console.error("Password reset failed:", data);
        setError(data.error || "Password reset failed.");
      }
    } catch (err) {
      console.error("Password reset error:", err);
      setError(err.message || "Network error. Try again.");
    }
    setLoading(false);
  };

  // Password strength helper
  function getPasswordStrength(password) {
    if (!password) return { label: "", color: "#aaa", glow: "#222" };
    if (password.length < 6) return { label: "Weak", color: "#ef4444", glow: "#ef4444" };
    if (password.length < 10) return { label: "Medium", color: "#fbbf24", glow: "#fbbf24" };
    if (password.match(/[A-Z]/) && password.match(/[0-9]/) && password.length >= 10) {
      return { label: "Strong", color: "#21c55d", glow: "#21c55d" };
    }
    return { label: "Medium", color: "#fbbf24", glow: "#fbbf24" };
  }

  return (
    <>
      <div className={sentinelTheme["page-theme-sentinel"]}>
        <div className={styles.background}>
        <div className={styles.logoContainer}>
          <img
            src={logo}
            alt="Sentinel Logo"
            className={styles.logo}
            data-role="background-logo"
            draggable={false}
          />
        </div>
        <div className={styles.hudEffectsLayer}>
          <HUDEffects />
          <HUDLayer />
        </div>
        <div className={styles.formLayer}>
          <div className={styles.cardWrapper}>
              <AnimatedCard>
                <Card>
                  <PageTitle allowWrap>PASSWORD RESET</PageTitle>
                  
                  {step === 1 ? (
                    // Step 1: Enter username to fetch security question
                    <form 
                      onSubmit={handleFetchSecurityQuestion} 
                      noValidate
                      className={styles.passwordResetForm} 
                      aria-describedby={error ? "password-reset-error" : undefined}
                      style={{ 
                        opacity: loadingQuestion ? 0.6 : 1,
                        pointerEvents: loadingQuestion ? 'none' : 'auto',
                        transition: 'opacity 0.3s ease'
                      }}
                    >
                      <TextBox
                        id="password-reset-username"
                        value={username}
                        onChange={setUsername}
                        placeholder="Username"
                        type="text"
                        autoComplete="username"
                        autoFocus
                        maxLength={80}
                        aria-required="true"
                        aria-invalid={!!error && error.toLowerCase().includes('username')}
                      />
                      
                      {error && (
                        <ShakeOnError trigger={error}>
                          <div
                            id="password-reset-error"
                            role="alert"
                            aria-live="assertive"
                            style={{
                              color: '#ef4444',
                              fontSize: '14px',
                              textAlign: 'center',
                              padding: '8px',
                              borderRadius: '4px',
                              backgroundColor: 'rgba(239, 68, 68, 0.1)',
                              width: '100%'
                            }}
                          >
                            {error}
                          </div>
                        </ShakeOnError>
                      )}
                      
                      <Button
                        type="submit"
                        disabled={loadingQuestion}
                        aria-busy={loadingQuestion}
                        style={{
                          width: "100%",
                          cursor: loadingQuestion ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {loadingQuestion ? "Loading..." : "Continue"}
                      </Button>
                    </form>
                  ) : (
                    // Step 2: Answer security question and reset password
                    <form 
                      onSubmit={handleSubmit} 
                      noValidate
                      className={styles.passwordResetForm} 
                      aria-describedby={error ? "password-reset-error" : undefined}
                      style={{ 
                        opacity: loading ? 0.6 : 1,
                        pointerEvents: loading ? 'none' : 'auto',
                        transition: 'opacity 0.3s ease'
                      }}
                    >
                      {/* Display username (read-only) */}
                      <div style={{
                        width: '100%',
                        textAlign: 'left',
                        marginBottom: '-4px'
                      }}>
                        <div style={{
                          fontSize: '14px',
                          color: 'var(--text-secondary)',
                          marginBottom: '4px',
                          fontFamily: "'Exo 2', sans-serif",
                          letterSpacing: '0.5px'
                        }}>
                          Username
                        </div>
                        <div style={{
                          fontSize: '16px',
                          color: 'var(--text-primary)',
                          fontFamily: "'Exo 2', sans-serif",
                          fontWeight: 600,
                          padding: '8px 0'
                        }}>
                          {username}
                        </div>
                      </div>
                      
                      {/* Display security question (read-only) */}
                      <div style={{
                        width: '100%',
                        textAlign: 'left',
                        marginBottom: '4px'
                      }}>
                        <div style={{
                          fontSize: '14px',
                          color: 'var(--text-secondary)',
                          marginBottom: '4px',
                          fontFamily: "'Exo 2', sans-serif",
                          letterSpacing: '0.5px'
                        }}>
                          Security Question
                        </div>
                        <div style={{
                          fontSize: '16px',
                          color: 'var(--text-primary)',
                          fontFamily: "'Exo 2', sans-serif",
                          fontWeight: 600,
                          padding: '8px 0'
                        }}>
                          {securityQuestion}
                        </div>
                      </div>
                      
                      <TextBox
                        id="password-reset-security-answer"
                        value={securityAnswer}
                        onChange={setSecurityAnswer}
                        placeholder="Security Answer"
                        type="text"
                        autoComplete="off"
                        autoFocus
                        maxLength={255}
                        aria-required="true"
                        aria-invalid={!!error && error.toLowerCase().includes('security answer')}
                      />
                      
                      <div style={{ width: '100%' }}>
                        <PasswordTextBox
                          id="password-reset-password"
                          value={password}
                          onChange={setPassword}
                          placeholder="New Password"
                          autoComplete="new-password"
                          aria-required="true"
                          aria-invalid={!!error && error.toLowerCase().includes('password')}
                          aria-describedby={error ? "password-reset-error" : undefined}
                        />
                        {/* Password Strength Meter */}
                        {password && (
                          <div style={{
                            marginTop: 8,
                            marginBottom: 0,
                            fontWeight: 700,
                            fontFamily: "'Exo 2', 'Exo2', sans-serif",
                            fontSize: 15,
                            letterSpacing: 2,
                            textTransform: 'uppercase',
                            color: getPasswordStrength(password).color,
                            textShadow: `0 0 8px ${getPasswordStrength(password).color}, 0 0 22px ${getPasswordStrength(password).color}`,
                            filter: `drop-shadow(0 0 8px ${getPasswordStrength(password).glow})`,
                            transition: 'color 0.2s, filter 0.2s',
                            textAlign: 'left',
                            width: '100%',
                            paddingLeft: 0
                          }}>
                            {getPasswordStrength(password).label}
                          </div>
                        )}
                      </div>
                      
                      <div style={{ width: '100%' }}>
                        <PasswordTextBox
                          id="password-reset-confirm-password"
                          value={confirmPassword}
                          onChange={setConfirmPassword}
                          placeholder="Confirm New Password"
                          autoComplete="new-password"
                          aria-required="true"
                          aria-invalid={!!error && error.toLowerCase().includes('password')}
                        />
                        {/* Password match indicator */}
                        {confirmPassword && (
                          <div style={{
                            marginTop: 8,
                            marginBottom: 0,
                            fontWeight: 700,
                            fontFamily: "'Exo 2', 'Exo2', sans-serif",
                            fontSize: 15,
                            letterSpacing: 2,
                            textTransform: 'uppercase',
                            color: password === confirmPassword ? '#21c55d' : '#ef4444',
                            textShadow: `0 0 8px ${password === confirmPassword ? '#21c55d' : '#ef4444'}, 0 0 22px ${password === confirmPassword ? '#21c55d' : '#ef4444'}`,
                            filter: `drop-shadow(0 0 8px ${password === confirmPassword ? '#21c55d' : '#ef4444'})`,
                            transition: 'color 0.2s, filter 0.2s',
                            textAlign: 'left',
                            width: '100%',
                            paddingLeft: 0
                          }}>
                            {password === confirmPassword ? 'Match' : 'No Match'}
                          </div>
                        )}
                      </div>
                      
                      {error && (
                        <ShakeOnError trigger={error}>
                          <div
                            id="password-reset-error"
                            role="alert"
                            aria-live="assertive"
                            style={{
                              color: "var(--danger)",
                              fontWeight: 700,
                              fontFamily: "'Exo 2', 'Exo2', sans-serif",
                              fontSize: 22,
                              letterSpacing: 2,
                              textTransform: 'uppercase',
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
                            fontFamily: "'Exo 2', 'Exo2', sans-serif",
                            fontSize: 22,
                            letterSpacing: 2,
                            textTransform: 'uppercase',
                            textShadow: "0 0 8px var(--success), 0 0 22px var(--glow-success)",
                            marginBottom: 8,
                            textAlign: "center",
                            filter: "drop-shadow(0 0 8px var(--glow-success))"
                          }}
                        >
                          PASSWORD UPDATED
                        </div>
                      )}
                      
                      <Button type="submit" disabled={loading} style={{ marginBottom: 0 }}>
                        {loading ? "Resetting..." : "Reset Password"}
                      </Button>
                    </form>
                  )}
                  
                  <div style={{ textAlign: "center", fontFamily: "'Exo 2', 'Exo2', sans-serif", marginTop: '16px' }}>
                    {/* Back to Login with transition */}
                    <a
                      href="#"
                      style={{ color: "var(--primary)", textDecoration: "underline", fontSize: 15, cursor: "pointer", display: "inline-block", fontFamily: "inherit" }}
                      onClick={e => {
                        e.preventDefault();
                        triggerTransition(() => navigate(fromLogin), "left");
                      }}
                    >
                      Back to Login
                    </a>
                  </div>
            </Card>
          </AnimatedCard>
          </div>
        </div>
      </div>
      </div>
    </>
  );
}

export default PasswordReset;
