import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import styles from "./LoginAnimation.module.css";
import logo from "../../assets/logo.png";

const LoginAnimation = ({ onComplete }) => {
  const [stage, setStage] = useState("init"); // init → access

  useEffect(() => {
    const timer1 = setTimeout(() => setStage("access"), 2200);
    const timer2 = setTimeout(() => onComplete(), 3800);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [onComplete]);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        className={styles.overlay}
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.9, ease: "easeInOut" }}
      >
        {/* Scanline layer */}
        <div className={styles.scanlines} />

        <div className={styles.center}>
          {/* Logo boot-up */}
          <motion.img
            src={logo}
            alt="PATRIOT logo"
            className={styles.logo}
            initial={{ scale: 0.65, opacity: 0 }}
            animate={{
              scale: [0.65, 1.15, 1],
              opacity: 1,
              filter: [
                "drop-shadow(0 0 4px rgba(47,143,255,0.4))",
                "drop-shadow(0 0 22px rgba(47,143,255,0.9))",
                "drop-shadow(0 0 10px rgba(47,143,255,0.6))",
              ]
            }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
          />

          {/* Boot message */}
          <motion.p
            key={stage}
            className={`${styles.text} ${
              stage === "access" ? styles.accentGreen : ""
            }`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {stage === "init" ? "INITIALIZING SYSTEM..." : "ACCESS GRANTED"}
          </motion.p>

          {/* Loading bar */}
          <motion.div
            className={styles.loadBar}
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ duration: 2.2, ease: "easeInOut" }}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LoginAnimation;
