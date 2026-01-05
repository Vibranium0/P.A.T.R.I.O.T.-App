import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { initBackgroundLogoRecalibration } from "../../../utils/background-logo-recalibration";
import styles from "./AuthLayout.module.css";

import HUDEffects from "../HUD/HUDEffects";
import HUDLayer from "../HUD/HUDLayer";

/**
 * AuthLayout - Shared layout for authentication pages (Login, Register, Reset Password)
 * 
 * Features:
 * - Background logo with orientation change detection
 * - HUD effects layer
 * - Centered form area
 * - Consistent sizing across all auth pages
 * - Safe area insets for notched devices
 * 
 * Props:
 * - logo: Logo image source (required)
 * - logoAlt: Alt text for logo (default: "Logo")
 * - title: Page title (e.g., "P.A.T.R.I.O.T." or "SENTINEL SYSTEMS")
 * - children: Form content (Card with form inside)
 * - transitionActive: Whether transition overlay is active (hides content during transition)
 */
const AuthLayout = ({ 
  logo, 
  logoAlt = "Logo",
  title,
  children,
  transitionActive = false
}) => {
  // Initialize background logo recalibration on mount
  useEffect(() => {
    const cleanup = initBackgroundLogoRecalibration();
    return cleanup;
  }, []);

  return (
    <div className={styles.authLayout}>
      {/* Background layer */}
      <div className={styles.background} />

      {/* Hide logo, form, and overlays during transition */}
      {!transitionActive && (
        <>
          {/* Background logo layer */}
          <div className={styles.logoLayer}>
            <img
              src={logo}
              alt={logoAlt}
              className={styles.logo}
              data-role="background-logo"
              draggable={false}
              aria-hidden="true"
            />
          </div>

          {/* HUD Effects Layer */}
          <div className={styles.hudEffectsLayer}>
            <HUDEffects />
            <HUDLayer />
          </div>

          {/* Content layer - form and title */}
          <div className={styles.contentLayer}>
            <div className={styles.contentWrapper}>
              {title && (
                <motion.h1
                  className={styles.title}
                  initial={{ opacity: 0, y: 32, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.45, ease: "easeOut" }}
                >
                  {title}
                </motion.h1>
              )}
              {children}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AuthLayout;
