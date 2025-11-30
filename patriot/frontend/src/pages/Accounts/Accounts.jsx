
import React, { useState, useEffect } from "react";
import styles from "./Accounts.module.css";
import Card from "../../components/Card/Card";
import Button from "../../components/Button/Button";

export default function Accounts() {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);

    useEffect(() => {
        // Fetch accounts from backend API
        async function fetchAccounts() {
            setLoading(true);
            try {
                const res = await fetch("/api/financial-accounts/");
                const data = await res.json();
                setAccounts(data.accounts || []);
            } catch (err) {
                console.error("Failed to load accounts", err);
            }
            setLoading(false);
        }
        fetchAccounts();
    }, []);

    return (
        <div className={styles.wrapper}>
            <div className={styles.headerRow}>
                <div className={styles.addAccountButton}>
                    <Button onClick={() => setModalOpen(true)}>+ Add Account</Button>
                </div>
            </div>
            <Card title="Your Accounts" variant="default">
                {loading ? (
                    <div>Loading...</div>
                ) : accounts.length === 0 ? (
                    <div>No accounts found.</div>
                ) : (
                    <ul className={styles.accountList}>
                        {accounts.map(acc => (
                            <li key={acc.id} className={styles.accountRow}>
                                <div className={styles.accountName}>{acc.name}</div>
                                <div className={styles.accountType}>{acc.type}</div>
                                <div className={styles.accountBalance}>${Number(acc.balance || 0).toFixed(2)}</div>
                            </li>
                        ))}
                    </ul>
                )}
            </Card>
            <AccountCreateModal
                open={modalOpen}
                onClose={() => setModalOpen(false)}
                onCreate={newAcc => setAccounts(accs => [...accs, { ...newAcc, id: Date.now() }])}
            />
        </div>
    );
}

