import React from 'react';
import styles from './TopSecretHeader.module.css';

export default function TopSecretHeader({ pageTitle }) {
    return (
        <header className={styles.header}>
            <span className={styles.title}>P.A.T.R.I.O.T.</span>
            {pageTitle && (
                <span className={styles.pageTitle}>{pageTitle}</span>
            )}
        </header>
    );
}
