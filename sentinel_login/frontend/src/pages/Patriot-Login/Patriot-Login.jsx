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
import Card from "shared/ui/components/Card/Card";
import ShakeOnError from "shared/ui/components/ShakeOnError";
import { PageTitle } from "shared/ui/components/PageTitle";

import { useTransitionOverlay } from "../../TransitionOverlayContext.jsx";

import HUDEffects from "shared/ui/components/HUD/HUDEffects";
import HUDLayer from "shared/ui/components/HUD/HUDLayer";


const PatriotLogin = () => {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  // Use app-level transition overlay
  const { triggerTransition, active: transitionActive } = useTransitionOverlay();
  const navigate = useNavigate();

  // Initialize background logo recalibration on mount
  useEffect(() => {
    const cleanup = initBackgroundLogoRecalibration();
    return cleanup;
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);
    setLoading(true);
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: identifier, password })
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        setSuccess(true);
        // Save token for authenticated requests
        localStorage.setItem("token", data.access_token);
        setTimeout(() => {
          window.location.href = "/dashboard";
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
      <div className={patriotTheme["page-theme-patriot"]}>
        <div className={styles.background}>
          {/* Hide logo, form, and overlays during transition */}
          {!transitionActive && (
            <>
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
              {/* HUD Effects Layer (cheese) */}
              <div className={styles.hudEffectsLayer}>
                <HUDEffects />
                <HUDLayer />
              </div>
              <div className={styles.centerOverlay}>
                <div className={styles.formLayer}>
                  <div className={styles.cardWrapper}>
                    <AnimatedCard>
                      <Card>
                        <PageTitle>P.A.T.R.I.O.T.</PageTitle>
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
                        >
                          <TextBox
                            value={identifier}
                            onChange={setIdentifier}
                            placeholder="Username"
                            type="text"
                            autoComplete="username"
                            required
                          />
                          <PasswordTextBox
                            value={password}
                            onChange={setPassword}
                            placeholder="Password"
                            autoComplete="current-password"
                            required
                          />
                          {error && (
                            <ShakeOnError trigger={error}>
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
                                {error.toUpperCase()}
                              </div>
                            </ShakeOnError>
                          )}
                          {success && (
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
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default PatriotLogin;
