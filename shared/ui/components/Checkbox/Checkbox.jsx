import React from 'react';
import styles from './Checkbox.module.css';

/**
 * Reusable Checkbox component with customizable icon and styling
 * @param {boolean} checked - Whether the checkbox is checked
 * @param {function} onChange - Callback when checkbox state changes
 * @param {string} label - Label text to display
 * @param {string} icon - SVG path string for the checked icon
 * @param {string} variant - Color variant: 'primary', 'success', 'secondary', 'danger'
 * @param {string} ariaLabel - Accessibility label
 */
const Checkbox = ({ 
  checked = false, 
  onChange, 
  label = '', 
  icon = 'M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z', // Default star icon
  variant = 'success',
  ariaLabel
}) => {
  return (
    <label className={`${styles.checkboxLabel} ${styles[variant]}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className={styles.hiddenInput}
        aria-label={ariaLabel || label}
      />
      <div className={`${styles.checkboxBox} ${checked ? styles.checked : ''}`}>
        {checked && (
          <svg 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="currentColor"
            className={styles.icon}
          >
            <path d={icon} />
          </svg>
        )}
      </div>
      {label && (
        <span className={styles.label}>
          {label}
        </span>
      )}
    </label>
  );
};

export default Checkbox;
