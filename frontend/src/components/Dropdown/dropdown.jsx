import React, { useState } from 'react';
import Button from '../Button/Button';
import styles from './dropdown.module.css';

export default function Dropdown({ options = [], selected, onSelect, label }) {
    const [open, setOpen] = useState(false);

    const handleSelect = (option) => {
        onSelect(option);
        setOpen(false);
    };

    return (
        <div className={styles.dropdownWrapper}>
            <Button
                variant="secondary"
                size="md"
                className={styles.dropdownButton}
                onClick={() => setOpen((prev) => !prev)}
                aria-haspopup="listbox"
                aria-expanded={open}
            >
                {selected || label || 'Select'}
                <span className={styles.arrow} />
            </Button>
            {open && (
                <ul className={styles.dropdownList} role="listbox">
                    {options.map((option) => (
                        <li
                            key={option}
                            className={styles.dropdownItem}
                            onClick={() => handleSelect(option)}
                            role="option"
                            aria-selected={selected === option}
                        >
                            {option}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
