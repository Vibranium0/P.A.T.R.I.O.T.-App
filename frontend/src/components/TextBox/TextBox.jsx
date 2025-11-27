import React from 'react';
import styles from './TextBox.module.css';

export default function TextBox({ value, onChange, placeholder = 'Bill Name', ...props }) {
    return (
        <div className={styles.textBoxContainer}>
            <input
                type="text"
                className={styles.textBox}
                value={value}
                onChange={e => onChange(e.target.value)}
                placeholder={placeholder}
                {...props}
            />
        </div>
    );
}
