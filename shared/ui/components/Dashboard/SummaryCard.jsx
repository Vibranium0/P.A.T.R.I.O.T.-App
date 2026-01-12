import React from "react";
import Card from "../Card/Card";
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
    <Card hover variant="default">
      <div className={styles.label}>{label}</div>
      <div className={styles.value}>
        <span className={styles.prefix}>{prefix}</span>
        <span className={styles.amount}>{value.toLocaleString()}</span>
      </div>
    </Card>
  );
}
