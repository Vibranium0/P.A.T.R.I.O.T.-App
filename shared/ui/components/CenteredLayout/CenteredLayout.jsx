import React from "react";
import styles from "./CenteredLayout.module.css";

/**
 * CenteredLayout - Mobile-safe centered container
 * 
 * Uses svh units and flexbox for reliable centering on all devices,
 * including iPadOS and mobile Safari with dynamic browser chrome.
 * 
 * Props:
 * - children: Content to be centered
 * - className: Additional CSS classes to apply to the wrapper
 * - contentClassName: Additional CSS classes to apply to the content container
 * - enableScroll: Whether to allow scrolling for overflow content (default: true)
 * - fullViewport: Whether to fill the full viewport height (default: true)
 */
const CenteredLayout = ({ 
  children, 
  className = "", 
  contentClassName = "",
  enableScroll = true,
  fullViewport = true 
}) => {
  const wrapperClass = `${styles.centeredWrapper} ${fullViewport ? styles.fullHeight : ""} ${enableScroll ? styles.scrollable : ""} ${className}`.trim();
  const contentClass = `${styles.centeredContent} ${contentClassName}`.trim();

  return (
    <div className={wrapperClass}>
      <div className={contentClass}>
        {children}
      </div>
    </div>
  );
};

export default CenteredLayout;
