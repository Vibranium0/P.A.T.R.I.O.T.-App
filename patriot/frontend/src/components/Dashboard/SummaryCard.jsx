import React from "react";
import { motion } from "framer-motion";
import styles from "./SummaryCard.module.css";

/**
 * SummaryCard: small KPI card
 * Props:
 *  - label (string)
 *  - value (number)
 *  - prefix (string)
 */
export default function SummaryCard({ label, value, prefix = "" }) {
  return (
    <motion.div
      className={styles.card}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      whileHover={{ translateY: -4 }}
    >
      <div className={styles.label}>{label}</div>
      <div className={styles.value}>
        <span className={styles.prefix}>{prefix}</span>
        <span className={styles.amount}>{value.toLocaleString()}</span>
      </div>
    </motion.div>
  );
}
