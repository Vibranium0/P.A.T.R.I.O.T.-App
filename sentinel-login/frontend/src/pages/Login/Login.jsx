

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import styles from "./Login.module.css";
import logo from '../../assets/patriot/logo.png';
import Button from "shared/ui/components/Button/Button";
import TextBox from "shared/ui/components/TextBox/TextBox";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      if (res.ok && data.access_token) {
        // Save token (optional: localStorage/sessionStorage)
        localStorage.setItem("token", data.access_token);
        navigate("/dashboard");
      } else {
        setError(data.error || "Login failed. Check credentials.");
      }
    } catch (err) {
      setError("Network error. Try again.");
    }
    setLoading(false);
  };


  return (
    <div className={styles.background}>
      <img
        src={logo}
        alt="Sentinel Logo"
        className={styles.logo}
        draggable={false}
      />
      <form onSubmit={handleSubmit} style={{ position: "relative", zIndex: 3, maxWidth: 400, margin: "0 auto", paddingTop: 100 }}>
        <h2>Login</h2>
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
      </form>
    </div>
  );
};

export default Login;
