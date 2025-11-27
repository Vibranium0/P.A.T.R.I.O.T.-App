import React from "react";
import { motion } from "framer-motion";
import styles from "./Card.module.css";

export default function Card({
  title = "",
  icon = null,
  children,
  footer = null,
  variant = "default",     // "default", "warning", "danger", "success"
  hover = true,
  onClick = null,
}) {
  return (
    <motion.div
      className={`${styles.card} ${styles[variant]} ${hover ? styles.hoverable : ""}`}
      onClick={onClick}
      whileHover={hover ? { scale: 1.02 } : {}}
      whileTap={hover ? { scale: 0.98 } : {}}
    >
      {/* HEADER */}
      {(title || icon) && (
        <div className={styles.header}>
          {icon && <span className={styles.icon}>{icon}</span>}
          {title && <h3 className={styles.title}>{title}</h3>}
        </div>
      )}

      {/* CONTENT */}
      <div className={styles.content}>
        {children}
      </div>

      {/* OPTIONAL FOOTER */}
      {footer && (
        <div className={styles.footer}>
          {footer}
        </div>
      )}
    </motion.div>
  );
}
