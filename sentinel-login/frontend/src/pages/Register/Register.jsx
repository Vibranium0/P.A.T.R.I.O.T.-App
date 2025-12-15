import React from "react";
import { motion } from "framer-motion";
import styles from "./Register.module.css";

const Register = () => {
  return (
    <motion.main
      className={styles.register}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <h1>Welcome to P.A.T.R.I.O.T.</h1>
    </motion.main>
  );
};

export default Register;
