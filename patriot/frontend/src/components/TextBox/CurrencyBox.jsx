import React from 'react';
import styles from './TextBox.module.css';

export default function CurrencyBox({ value, onChange, placeholder = '$0.00', ...props }) {
    // Format value as currency
    const formatCurrency = val => {
        if (val === '') return '';
        const num = parseFloat(val.replace(/[^\d.]/g, ''));
        if (isNaN(num)) return '';
        return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    };

    const handleChange = e => {
        const raw = e.target.value.replace(/[^\d.]/g, '');
        onChange(raw);
    };

    return (
        <div className={styles.currencyBoxContainer}>
            <input
                type="text"
                className={styles.currencyBox}
                value={formatCurrency(value)}
                onChange={handleChange}
                placeholder={placeholder}
                {...props}
            />
        </div>
    );
}
