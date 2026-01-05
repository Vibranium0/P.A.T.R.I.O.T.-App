import { motion } from "framer-motion";
import styles from "./PageTitle.module.css";

export const PageTitle = ({ children, allowWrap = false }) => {
  return (
    <motion.h1
      className={styles.pageTitle}
      style={{ whiteSpace: allowWrap ? 'normal' : 'nowrap' }}
      initial={{ opacity: 0, y: 32, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
    >
      {children}
    </motion.h1>
  );
};
