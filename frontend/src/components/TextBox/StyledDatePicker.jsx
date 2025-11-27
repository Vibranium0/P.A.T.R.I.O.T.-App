import React from 'react';
import styles from './TextBox.module.css';

export default function StyledDatePicker({ value, onChange, placeholder = 'Date', ...props }) {
    // Default to today if no value
    const today = new Date();
    const initial = value ? value : today.toISOString().slice(0, 10);
    const [mm, setMm] = React.useState(initial ? initial.slice(5, 7) : '');
    const [dd, setDd] = React.useState(initial ? initial.slice(8, 10) : '');
    const [yyyy, setYyyy] = React.useState(initial ? initial.slice(0, 4) : '');
    const mmRef = React.useRef();
    const ddRef = React.useRef();
    const yyyyRef = React.useRef();

    // Move focus to next box when filled
    React.useEffect(() => {
        if (mm.length === 2) ddRef.current.focus();
    }, [mm]);
    React.useEffect(() => {
        if (dd.length === 2) yyyyRef.current.focus();
    }, [dd]);

    // Update value when all fields are filled
    React.useEffect(() => {
        if (mm.length === 2 && dd.length === 2 && yyyy.length === 4) {
            const iso = `${yyyy}-${mm}-${dd}`;
            onChange(iso);
        }
    }, [mm, dd, yyyy, onChange]);

    // Handle calendar selection
    const handleCalendarChange = date => {
        if (date) {
            setMm(String(date.getMonth() + 1).padStart(2, '0'));
            setDd(String(date.getDate()).padStart(2, '0'));
            setYyyy(String(date.getFullYear()));
            onChange(date.toISOString().slice(0, 10));
        } else {
            setMm(''); setDd(''); setYyyy('');
            onChange('');
        }
    };

    return (
        <div className={styles.dateInputBox}>
            <span className={styles.dateInputSpan}>
                <input
                    type="text"
                    maxLength={2}
                    value={mm}
                    onChange={e => setMm(e.target.value.replace(/[^\d]/g, ''))}
                    ref={mmRef}
                    className={`${styles.dateInputBox} ${styles.mm}`}
                    placeholder="MM"
                    autoFocus
                />
                <span>/</span>
                <input
                    type="text"
                    maxLength={2}
                    value={dd}
                    onChange={e => setDd(e.target.value.replace(/[^\d]/g, ''))}
                    ref={ddRef}
                    className={`${styles.dateInputBox} ${styles.dd}`}
                    placeholder="DD"
                />
                <span>/</span>
                <input
                    type="text"
                    maxLength={4}
                    value={yyyy}
                    onChange={e => setYyyy(e.target.value.replace(/[^\d]/g, ''))}
                    ref={yyyyRef}
                    className={`${styles.dateInputBox} ${styles.yyyy}`}
                    placeholder="YYYY"
                />
            </span>
        </div>
    );
}
