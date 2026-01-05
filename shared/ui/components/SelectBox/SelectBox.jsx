import React, { useState, useRef, useEffect } from "react";
import { FiChevronDown } from "react-icons/fi";
import styles from "./SelectBox.module.css";

const SelectBox = ({ 
  id,
  value, 
  onChange, 
  options = [], 
  placeholder = "Select an option",
  required = false,
  disabled = false,
  ariaLabel,
  ariaInvalid,
  ariaRequired,
  style = {},
  ...props 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (option) => {
    const syntheticEvent = {
      target: { value: option }
    };
    onChange(syntheticEvent);
    setIsOpen(false);
  };

  const displayValue = value || placeholder;
  const hasValue = Boolean(value);

  return (
    <div 
      ref={wrapperRef}
      className={styles.selectBoxWrapper} 
      style={style}
    >
      <button
        id={id}
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        aria-label={ariaLabel}
        aria-invalid={ariaInvalid}
        aria-required={ariaRequired}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        className={`${styles.selectBox} ${hasValue ? styles.hasValue : ''}`}
        {...props}
      >
        <span className={styles.displayText}>{displayValue}</span>
        <FiChevronDown className={`${styles.icon} ${isOpen ? styles.iconOpen : ''}`} />
      </button>
      
      {isOpen && !disabled && (
        <ul className={styles.optionsList} role="listbox">
          {options.map((option, index) => {
            const optionValue = typeof option === 'string' ? option : option.value;
            const optionLabel = typeof option === 'string' ? option : option.label;
            
            return (
              <li
                key={index}
                className={`${styles.option} ${value === optionValue ? styles.optionSelected : ''}`}
                onClick={() => handleSelect(optionValue)}
                role="option"
                aria-selected={value === optionValue}
              >
                {optionLabel}
              </li>
            );
          })}
        </ul>
      )}
      
      {/* Hidden input for form validation */}
      {required && (
        <input
          type="text"
          value={value}
          required
          tabIndex={-1}
          aria-hidden="true"
          style={{
            position: 'absolute',
            opacity: 0,
            height: 0,
            width: 0,
            pointerEvents: 'none'
          }}
        />
      )}
    </div>
  );
};

export default SelectBox;
