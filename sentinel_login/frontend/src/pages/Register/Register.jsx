import React, { useState, useEffect } from "react";
import { initBackgroundLogoRecalibration } from "shared/utils/background-logo-recalibration";
import { Helmet } from "react-helmet";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Register.module.css";
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

const Register = () => {
  const location = useLocation();
  // Default to /patriot-login if not provided
  const fromLogin = location.state?.from || "/patriot-login";
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");

  // Predefined security questions for consistency
  const securityQuestions = [
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What is your favorite book?",
    "What was your childhood nickname?"
  ];
  const navigate = useNavigate();
  const { triggerTransition } = useTransitionOverlay();

  // Initialize background logo recalibration on mount
  useEffect(() => {
    const cleanup = initBackgroundLogoRecalibration();
    return cleanup;
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Client-side validation - check all fields and collect errors
    const missingFields = [];
    
    if (!username.trim()) {
      missingFields.push("Username");
    } else if (username.trim().length < 3) {
      setError("Username must be at least 3 characters");
      return;
    }

    if (!password) {
      missingFields.push("Password");
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

    if (!securityQuestion) {
      missingFields.push("Security Question");
    }

    if (!securityAnswer.trim()) {
      missingFields.push("Security Answer");
    } else if (securityAnswer.trim().length < 2) {
      setError("Security answer must be at least 2 characters");
      return;
    }

    // If there are missing fields, format the error message
    if (missingFields.length > 0) {
      if (missingFields.length === 5) {
        setError("All fields are required");
      } else {
        setError(`Required fields: ${missingFields.join(", ")}`);
      }
      return;
    }

    setLoading(true);
    console.log("Submitting registration with:", {
      username,
      password: "***",
      security_question: securityQuestion,
      security_answer: securityAnswer
    });
    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, security_question: securityQuestion, security_answer: securityAnswer })
      });
      const data = await res.json();
      console.log("Registration response:", { status: res.status, data });
      if (res.ok && data.message) {
        setSuccess("Registration successful! Redirecting...");
        setTimeout(() => {
          triggerTransition(() => navigate(fromLogin), "left");
        }, 1500);
      } else {
        console.error("Registration failed:", data);
        setError(data.error || "Registration failed.");
      }
    } catch (err) {
      console.error("Registration error:", err);
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

        <div className={styles.formLayer}>
          <div className={styles.cardWrapper}>
              <AnimatedCard>
                <Card>
                  <PageTitle allowWrap>SENTINEL SYSTEMS</PageTitle>
                  <form 
                    onSubmit={handleSubmit} 
                    noValidate
                    className={styles.registerForm} 
                    aria-describedby={error ? "register-error" : undefined}
                    style={{ 
                      opacity: loading ? 0.6 : 1,
                      pointerEvents: loading ? 'none' : 'auto',
                      transition: 'opacity 0.3s ease'
                    }}
                  >
                {/* Email field removed */}
                <TextBox
                  id="register-username"
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
                <div style={{ width: '100%' }}>
                  <PasswordTextBox
                    id="register-password"
                    value={password}
                    onChange={setPassword}
                    placeholder="Password"
                    autoComplete="new-password"
                    aria-required="true"
                    aria-invalid={!!error && error.toLowerCase().includes('password')}
                    aria-describedby={error ? "register-error" : undefined}
                  />
                  {/* Password Strength Meter - now inside password field container for minimal gap */}
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
                    id="register-confirm-password"
                    value={confirmPassword}
                    onChange={setConfirmPassword}
                    placeholder="Confirm Password"
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
                <SelectBox
                  id="register-security-question"
                  value={securityQuestion}
                  onChange={(e) => setSecurityQuestion(e.target.value)}
                  options={securityQuestions}
                  placeholder="Select a Security Question"
                  ariaRequired="true"
                  ariaInvalid={!!error && error.toLowerCase().includes('security question')}
                />
                <TextBox
                  id="register-security-answer"
                  value={securityAnswer}
                  onChange={setSecurityAnswer}
                  placeholder="Security Answer"
                  type="text"
                  autoComplete="off"
                  maxLength={255}
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('security answer')}
                />
                {error && (
                  <ShakeOnError trigger={error}>
                    <div
                      id="register-error"
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
                    {success === 'Registration successful! Redirecting...' ? 'WELCOME TO SENTINEL' : success.toUpperCase()}
                  </div>
                )}
                <Button type="submit" disabled={loading} style={{ marginBottom: 0 }}>
                  {loading ? "Registering..." : "Register"}
                </Button>
                <div style={{ textAlign: "center", fontFamily: "'Exo 2', 'Exo2', sans-serif" }}>
                  {/* Back to Login with transition */}
                  <a
                    href="#"
                    style={{ color: "var(--primary)", textDecoration: "underline", fontSize: 15, cursor: "pointer", marginBottom: 8, display: "inline-block", fontFamily: "inherit" }}
                    onClick={e => {
                      e.preventDefault();
                      triggerTransition(() => navigate(fromLogin), "left");
                    }}
                  >
                    Back to Login
                  </a>
                </div>
              </form>
            </Card>
          </AnimatedCard>
          </div>
        </div>
      </div>
      </div>
    </>
  );
}

export default Register;
