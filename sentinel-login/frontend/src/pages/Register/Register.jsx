
import React, { useState, useRef, useEffect } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";
import { Helmet } from "react-helmet";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Register.module.css";
import logo from '../../assets/sentinel-login/Sentinel Systems.png';

import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";
import Card from "shared/ui/components/Card/Card";
import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";

const Register = () => {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const logoRef = useRef(null);
  const [logoStyle, setLogoStyle] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    function updateLogoMetrics() {
      if (logoRef.current) {
        const windowHeight = window.innerHeight;
        const style = {
          width: 'auto',
          height: 'auto',
          maxHeight: '85vh',
          maxWidth: '85vw',
        };
        setLogoStyle(style);
      }
    }
    updateLogoMetrics();
    window.addEventListener('resize', updateLogoMetrics);
    return () => window.removeEventListener('resize', updateLogoMetrics);
  }, []);

  function validateUsername(username) {
    return username && username.length >= 3;
  }

  function getPasswordStrength(password) {
    if (!password) return { label: '', color: '', glow: '' };
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    if (password.length >= 12) score++;
    if (score === 0) return { label: 'WEAK', color: 'var(--danger)', glow: 'var(--glow-danger)' };
    if (score === 1 || score === 2) return { label: 'MEDIUM', color: 'var(--warning)', glow: '0 0 8px var(--warning), 0 0 22px var(--warning)' };
    if (score >= 3) return { label: 'STRONG', color: 'var(--success)', glow: 'var(--glow-success)' };
    return { label: '', color: '', glow: '' };
  }

  function validatePassword(password) {
    return password && password.length >= 8;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Client-side validation
    if (!email || !username || !password) {
      setError("All fields are required.");
      return;
    }
    if (!validateUsername(username)) {
      setError("Username must be at least 3 characters.");
      return;
    }
    if (!validatePassword(password)) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password })
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess("Registration successful! Redirecting...");
        setTimeout(() => navigate("/app-select"), 1200);
      } else {
        setError(data.error || "Registration failed.");
        setSuccess("");
      }
    } catch (err) {
      setError("Network error. Try again.");
      setSuccess("");
    }
    setLoading(false);
  };


  return (
    <>
      <Helmet>
        <title>Sentinel Registration</title>
        <link rel="icon" type="image/png" href="/favicon-sentinel.png" />
      </Helmet>


      <div className={styles.background}>
        <div className={styles.logoContainer}>
          <img
            ref={logoRef}
            src={logo}
            alt="Sentinel Logo"
            className={styles.logo}
            draggable={false}
            style={logoStyle}
          />
        </div>
        {/* HUD Effects Layer moved to app.jsx for static rendering */}
        <div className={styles.formContainer}>
          <div className={styles.sentinelTitle}>SENTINEL SYSTEMS</div>
          <Card>
            <form onSubmit={handleSubmit} className={styles.registerForm} aria-describedby={error ? "register-error" : undefined}>
              <label htmlFor="register-email" style={{ width: '100%', textAlign: 'left', fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>Email
                <TextBox
                  id="register-email"
                  value={email}
                  onChange={setEmail}
                  placeholder="Email"
                  type="email"
                  autoComplete="email"
                  required
                  aria-required="true"
                  aria-invalid={!!error && error.toLowerCase().includes('email')}
                />
              </label>
              <label htmlFor="register-username" style={{ width: '100%', textAlign: 'left', fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>Username
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
                />
              </label>
              <label htmlFor="register-password" style={{ width: '100%', textAlign: 'left', fontWeight: 600, fontSize: 15, color: 'var(--text-primary)', position: 'relative' }}>Password
                <div style={{ position: 'relative', width: '100%' }}>
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
                </div>
                {/* Password Strength Meter */}
                {password && (
                  <div style={{
                    marginTop: 6,
                    fontWeight: 700,
                    fontFamily: "'Exo 2', 'Exo2', sans-serif",
                    fontSize: 15,
                    letterSpacing: 2,
                    textTransform: 'uppercase',
                    color: getPasswordStrength(password).color,
                    textShadow: `0 0 8px ${getPasswordStrength(password).color}, 0 0 22px ${getPasswordStrength(password).color}`,
                    filter: `drop-shadow(0 0 8px ${getPasswordStrength(password).glow})`,
                    transition: 'color 0.2s, filter 0.2s',
                  }}>
                    {getPasswordStrength(password).label}
                  </div>
                )}
              </label>
              {error && (
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
              <Button type="submit" disabled={loading}>
                {loading ? "Registering..." : "Register"}
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </>
  );
};

export default Register;
