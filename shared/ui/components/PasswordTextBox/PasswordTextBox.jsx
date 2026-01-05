import React, { useState } from 'react';
import { FiEye, FiEyeOff } from 'react-icons/fi';
import styles from './PasswordTextBox.module.css';

export default function PasswordTextBox({ 
    value, 
    onChange, 
    placeholder = 'Password',
    id,
    autoComplete = 'current-password',
    ...props 
}) {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div className={styles.passwordContainer}>
            <input
                id={id}
                type={showPassword ? "text" : "password"}
                className={styles.passwordInput}
                value={value}
                onChange={e => onChange(e.target.value)}
                placeholder={placeholder}
                autoComplete={autoComplete}
                autoCapitalize="off"
                autoCorrect="off"
                spellCheck="false"
                {...props}
            />
            <button
                type="button"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword(v => !v)}
                className={styles.toggleButton}
                tabIndex={0}
            >
                {showPassword ? <FiEyeOff /> : <FiEye />}
            </button>
        </div>
    );
}
