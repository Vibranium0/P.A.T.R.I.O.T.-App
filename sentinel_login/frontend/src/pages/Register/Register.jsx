import React, { useState, useRef, useEffect } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";
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
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const logoRef = useRef(null);
  const [logoStyle, setLogoStyle] = useState({});
  const navigate = useNavigate();
  const { triggerTransition } = useTransitionOverlay();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
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
        <div className={styles.hudEffectsLayer}>
          <HUDEffects />
          <HUDLayer />
        </div>
        <div className={styles.logoContainer}>
          <AnimatedCard>
            <img
              ref={logoRef}
              src={logo}
              alt="Sentinel Logo"
              className={styles.logo}
              draggable={false}
              style={logoStyle}
            />
          </AnimatedCard>
        </div>
        {/* HUD Effects Layer moved to app.jsx for static rendering */}
        <div className={styles.formContainer}>
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
              <form onSubmit={handleSubmit} className={styles.registerForm} aria-describedby={error ? "register-error" : undefined}>
                {/* Email field removed */}
                <TextBox
                  id="register-username"
                  value={username}
                  onChange={setUsername}
                  placeholder="Username"
                  type="text"
                  autoComplete="username"
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
                      zIndex: 2
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
                <TextBox
                  id="register-security-question"
                  value={securityQuestion}
                  onChange={setSecurityQuestion}
                  placeholder="Security Question (e.g. Your first pet's name?)"
                  type="text"
                  autoComplete="off"
                  required
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('security question')}
                  style={{ marginBottom: 16 }}
                />
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
    </>
  );
}

export default Register;
