import React from "react";
import { motion } from "framer-motion";
import styles from "./HUDLayer.module.css";

export default function HUDLayer() {
  return (
    <div className={styles.hudContainer}>

      {/* ===========================
          1. Slow Scanning Lines
          =========================== */}
      {[...Array(4)].map((_, i) => (
        <motion.div
          key={`scan-${i}`}
          className={styles.scanLine}
          style={{ top: `${20 * i + 10}%` }}
          initial={{ x: "-20%" }}
          animate={{ x: "120%" }}
          transition={{
            duration: 6,
            delay: i * 1.2,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      ))}

      {/* ===========================
          2. Circuit Nodes (gentle glow pulses)
          =========================== */}
      {[...Array(10)].map((_, i) => (
        <motion.div
          key={`node-${i}`}
          className={styles.node}
          style={{
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`
          }}
          initial={{ opacity: 0.15 }}
          animate={{ opacity: 0.85 }}
          transition={{
            duration: 2.5 + Math.random() * 3,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut"
          }}
        />
      ))}

      {/* ===========================
          3. Subtle Corner Pulses
          =========================== */}
      <div className={styles.cornerPulseTL} />
      <div className={styles.cornerPulseTR} />
      <div className={styles.cornerPulseBL} />
      <div className={styles.cornerPulseBR} />

    </div>
  );
}
