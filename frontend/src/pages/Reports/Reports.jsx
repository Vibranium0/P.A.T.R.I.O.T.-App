import React from "react";
import { motion } from "framer-motion";
import styles from "./Reports.module.css";

const Reports = () => {
  return (
    <motion.main
      className={styles.reports}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Removed page title as requested */}
    </motion.main>
  );
};

export default Reports;
