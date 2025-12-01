import React, { forwardRef } from "react";
import styles from "./Button.module.css";
import classNames from "classnames";

const VALID_VARIANTS = ["primary", "secondary", "danger", "ghost", "success", "secondarySuccess"];
const VALID_SIZES = ["sm", "md", "lg"];

const Button = forwardRef(
  (
    {
      variant = "primary",
      size = "md",
      pulse = false,
      icon = false,
      children,
      onClick,
      className,
      ...props
    },
    ref
  ) => {
    const safeVariant = VALID_VARIANTS.includes(variant)
      ? variant
      : "primary";

    const safeSize = VALID_SIZES.includes(size)
      ? size
      : "md";

    const buttonClass = classNames(
      styles.button,
      styles[safeVariant],
      styles[safeSize],
      styles.glowHover,
      pulse && styles.glowPulse,
      icon && styles.iconButton,
      className
    );

    return (
      <button ref={ref} className={buttonClass} onClick={onClick} {...props}>
        {children}
      </button>
    );
  }
);

export default Button;
