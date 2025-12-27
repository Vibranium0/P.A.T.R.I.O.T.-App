import React, { useState } from "react";
import { Helmet } from "react-helmet";
import patriotTheme from "./PatriotLoginTheme.module.css";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Patriot-Login.module.css";
import logo from '../../assets/patriot/logo.png';
import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";
import Card from "shared/ui/components/Card/Card";
import LoginAnimation from "shared/ui/components/LoginAnimation/LoginAnimation";

import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";

const PatriotLogin = () => {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);
    setLoading(true);
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: identifier, email: identifier, password })
    });
    // ...existing code...
  };
  return (
    <>
      <Helmet>
        <title>Patriot Login</title>
        <link rel="icon" type="image/png" href="/favicon-patriot.png" />
      </Helmet>
      <div className={patriotTheme["page-theme-patriot"]}>
        <div className={styles.background}>
          <div className={styles.logoLayer}>
            <img
              src={logo}
              alt="Sentinel Logo"
              className={styles.logo}
              draggable={false}
              aria-hidden="true"
            />
          </div>
          {/* HUD Effects Layer (cheese) */}
          <div className={styles.hudEffectsLayer}>
            <HUDEffects />
            <HUDLayer />
          </div>
          <div className={styles.centerOverlay}>
            <div className={styles.formLayer}>
              <div className={styles.cardWrapper}>
                <h1 className={styles.patriotTitle}>P.A.T.R.I.O.T.</h1>
                <Card>
                  <form
                    className={styles.loginForm}
                    onSubmit={handleSubmit}
                  >
                    <TextBox
                      value={identifier}
                      onChange={setIdentifier}
                      placeholder="Username or Email"
                      type="text"
                      autoComplete="username"
                      required
                    />
                    <TextBox
                      value={password}
                      onChange={setPassword}
                      placeholder="Password"
                      type="password"
                      autoComplete="current-password"
                      required
                    />
                    {error && (
                      <div
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
                        {error}
                      </div>
                    )}
                    {success && !showAnimation && (
                      <div
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
                    <Button type="submit" disabled={loading || success}>
                      {loading ? "Logging in..." : "Login"}
                    </Button>
                  </form>
                  <div style={{ marginTop: 18, textAlign: "center", fontFamily: "'Exo 2', 'Exo2', sans-serif" }}>
                    <a
                      href="#"
                      style={{ color: "var(--primary)", textDecoration: "underline", fontSize: 15, cursor: "pointer", marginBottom: 8, display: "inline-block", fontFamily: "inherit" }}
                      onClick={e => { e.preventDefault(); /* TODO: navigate to forgot password page */ }}
                    >
                      Forgot password?
                    </a>
                    <br />
                    <span style={{ color: "var(--text-secondary)", fontSize: 15, fontFamily: "inherit" }}>
                      Don&apos;t have an account?{' '}
                      <a
                        href="#"
                        style={{ color: "var(--primary)", textDecoration: "underline", cursor: "pointer", fontFamily: "inherit" }}
                        onClick={e => { e.preventDefault(); navigate("/register"); }}
                      >
                        Register
                      </a>
                    </span>
                  </div>
                </Card>
              </div>
            </div>
          </div>
          {showAnimation && <LoginAnimation onComplete={() => { }} />}
        </div>
      </div>
    </>
  );
};

export default PatriotLogin;
