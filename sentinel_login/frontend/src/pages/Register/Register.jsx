import React, { useState, useEffect } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";
import { initBackgroundLogoRecalibration } from "shared/utils/background-logo-recalibration";
import { Helmet } from "react-helmet";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Register.module.css";
import logo from '../../assets/sentinel-login/Sentinel Systems.png';

import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";
import AnimatedCard from "shared/ui/components/AnimatedCard";
import { useTransitionOverlay } from "../../TransitionOverlayContext.jsx";
import ShakeOnError from "shared/ui/components/ShakeOnError";
import Card from "shared/ui/components/Card/Card";
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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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

    // Client-side validation
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (!securityQuestion) {
      setError("Please select a security question");
      return;
    }

    if (securityAnswer.trim().length < 2) {
      setError("Security answer must be at least 2 characters");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, security_question: securityQuestion, security_answer: securityAnswer })
      });
      const data = await res.json();
      if (res.ok && data.message) {
        setSuccess("Registration successful! Redirecting...");
        setTimeout(() => {
          triggerTransition(() => navigate(fromLogin), "left");
        }, 1500);
      } else {
        setError(data.error || "Registration failed.");
      }
    } catch (err) {
      setError("Network error. Try again.");
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
              <motion.div
                className={styles.sentinelTitle}
                initial={{ opacity: 0, y: 32, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.45, ease: "easeOut" }}
              >
                SENTINEL SYSTEMS
              </motion.div>
              <AnimatedCard>
                <Card>
                  <form 
                    onSubmit={handleSubmit} 
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
                  required
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('username')}
                  style={{ marginBottom: 16 }}
                />
                <div style={{ position: 'relative', width: '100%', marginBottom: 16 }}>
                  <TextBox
                    id="register-password"
                    value={password}
                    onChange={setPassword}
                    placeholder="Password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="new-password"
                    required
                    aria-required="true"
                    aria-invalid={!!error && error.toLowerCase().includes('password')}
                    aria-describedby={error ? "register-error" : undefined}
                    style={{ paddingRight: 38 }}
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    onClick={() => setShowPassword(v => !v)}
                    style={{
                      position: 'absolute',
                      right: 8,
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      margin: 0,
                      cursor: 'pointer',
                      color: 'var(--text-secondary)',
                      fontSize: 22,
                      zIndex: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 24,
                      height: 24,
                      lineHeight: 1
                    }}
                    tabIndex={0}
                  >
                    {showPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
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
                <div style={{ position: 'relative', width: '100%', marginBottom: 16 }}>
                  <TextBox
                    id="register-confirm-password"
                    value={confirmPassword}
                    onChange={setConfirmPassword}
                    placeholder="Confirm Password"
                    type={showConfirmPassword ? "text" : "password"}
                    autoComplete="new-password"
                    required
                    aria-required="true"
                    aria-invalid={!!error && error.toLowerCase().includes('password')}
                    style={{ paddingRight: 38 }}
                  />
                  <button
                    type="button"
                    aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                    onClick={() => setShowConfirmPassword(v => !v)}
                    style={{
                      position: 'absolute',
                      right: 8,
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      margin: 0,
                      cursor: 'pointer',
                      color: 'var(--text-secondary)',
                      fontSize: 22,
                      zIndex: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 24,
                      height: 24,
                      lineHeight: 1
                    }}
                    tabIndex={0}
                  >
                    {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
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
                <select
                  id="register-security-question"
                  value={securityQuestion}
                  onChange={(e) => setSecurityQuestion(e.target.value)}
                  required
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('security question')}
                  style={{
                    width: '100%',
                    height: '2.75rem',
                    padding: '0.75rem 0.75rem',
                    marginBottom: 16,
                    background: 'none',
                    border: '1px solid var(--accent-light)',
                    borderRadius: '0.5rem',
                    boxShadow: 'var(--glow-soft)',
                    color: securityQuestion ? 'var(--text-primary)' : 'var(--text-secondary)',
                    fontFamily: "'Exo 2', 'Exo2', sans-serif",
                    fontSize: '15px',
                    fontWeight: securityQuestion ? 600 : 400,
                    letterSpacing: '0.05em',
                    opacity: securityQuestion ? 1 : 0.55,
                    cursor: 'pointer',
                    transition: 'border-color 0.18s, box-shadow 0.18s, color 0.18s, opacity 0.18s',
                    outline: 'none'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = 'var(--primary)';
                    e.target.style.boxShadow = '0 0 0 2px var(--primary), 0 0 12px var(--primary), var(--glow-soft)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'var(--accent-light)';
                    e.target.style.boxShadow = 'var(--glow-soft)';
                  }}
                >
                  <option value="" disabled>Select a security question</option>
                  {securityQuestions.map((q, idx) => (
                    <option key={idx} value={q} style={{ background: 'var(--card-bg, #0f1621)', color: 'var(--text-primary, #fff)' }}>{q}</option>
                  ))}
                </select>
                <TextBox
                  id="register-security-answer"
                  value={securityAnswer}
                  onChange={setSecurityAnswer}
                  placeholder="Security Answer"
                  type="text"
                  autoComplete="off"
                  required
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('security answer')}
                  style={{ marginBottom: 16 }}
                />
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
    </>
  );
}

export default Register;
