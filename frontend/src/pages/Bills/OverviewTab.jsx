import React, { useMemo, useState } from "react";
import Button from "../../components/Button/Button";
import styles from "./Bills.module.css";

/**
 * Overview tab - list bills, add new, quick controls.
 * Props:
 *  - bills, addBill, updateBill, deleteBill, settings, setSettings, replaceBills
 */
export default function OverviewTab({
    bills,
    addBill,
    updateBill,
    deleteBill,
    settings,
    setSettings,
    replaceBills,
}) {
    const [form, setForm] = useState({
        name: "",
        amount: "",
        nextDue: "",
        frequency: "monthly",
        autopay: false,
    });
    const [editBill, setEditBill] = useState(null);
    const [showCreate, setShowCreate] = useState(false);

    const totals = useMemo(() => {
        const total = bills.reduce((s, b) => s + Number(b.amount || 0), 0);
        const unpaid = bills.filter((b) => !b.paid).reduce((s, b) => s + Number(b.amount || 0), 0);
        const paid = total - unpaid;
        return { total, paid, unpaid };
    }, [bills]);

    function handleAdd(e) {
        e.preventDefault();
        if (!form.name || !form.amount || !form.nextDue) return;
        addBill({
            name: form.name,
            amount: Number(form.amount),
            nextDue: form.nextDue,
            frequency: form.frequency,
            autopay: form.autopay,
            paid: false,
        });
        setForm({ name: "", amount: "", nextDue: "", frequency: "monthly", autopay: false });
        setShowCreate(false);
    }

    function handleEditSave(e) {
        e.preventDefault();
        if (!editBill.name || !editBill.amount || !editBill.nextDue) return;
        updateBill(editBill.id, {
            name: editBill.name,
            amount: Number(editBill.amount),
            nextDue: editBill.nextDue,
            frequency: editBill.frequency,
            autopay: editBill.autopay,
        });
        setEditBill(null);
    }

    function handleEditDelete() {
        deleteBill(editBill.id);
        setEditBill(null);
    }

    const togglePaid = (id) => {
        const b = bills.find((x) => x.id === id);
        if (!b) return;
        updateBill(id, { paid: !b.paid });
    };

    // settings handlers
    const handleSettingsChange = (patch) => setSettings({ ...settings, ...patch });

    const resetSettings = () => {
        if (!window.confirm("Reset bills settings and cache? This cannot be undone.")) return;
        localStorage.removeItem("patriot_bills_settings");
        localStorage.removeItem("patriot_bills_schedules");
        // reload defaults
        setSettings({
            startDate: "",
            startBalance: 0,
            bufferAmount: 0,
            monthsToProject: 3,
            currentAccountBalance: 0,
        });
    };

    // Option: import last N months of transactions - replaced by simple UI for now
    const importSample = () => {
        // example: replace bills from old file if needed
        if (!window.confirm("Replace all bills with sample dataset?")) return;
        replaceBills([
            { id: Date.now() + 1, name: "Rent", amount: 1200, nextDue: "2025-02-01", frequency: "monthly", paid: false },
            { id: Date.now() + 2, name: "Electric", amount: 85, nextDue: "2025-02-05", frequency: "monthly", paid: false },
        ]);
    };

    return (
        <div className={styles.overviewContainer}>
            <div className={styles.summaryGrid}>
                <Card title="Total Bills"><p className={styles.summaryAmount}>${totals.total}</p></Card>
                <Card title="Paid" variant="success"><p className={styles.summaryAmount}>${totals.paid}</p></Card>
                <Card title="Unpaid" variant="warning"><p className={styles.summaryAmount}>${totals.unpaid}</p></Card>
            </div>

            <Card title="Manage Bills">
                <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", marginBottom: "0.5rem" }}>
                    <Button variant="primary" onClick={() => setShowCreate(true)}>
                        Create Bill
                    </Button>
                </div>
                <div className={styles.billList}>
                    {bills.length === 0 && <p className={styles.muted}>No bills yet — add one below.</p>}
                    {bills.map((bill) => (
                        <div
                            key={bill.id}
                            className={styles.billRow}
                            style={{ cursor: "pointer" }}
                            onClick={e => {
                                // Prevent opening modal if paid button is clicked
                                if (e.target.closest("button")) return;
                                setEditBill({ ...bill });
                            }}
                        >
                            <div className={styles.billInfo}>
                                <p className={styles.billName}>{bill.name}</p>
                                <p className={styles.billDue}>Next: {new Date(bill.nextDue).toLocaleDateString()}</p>
                            </div>
                            <p className={styles.billAmount}>${bill.amount}</p>
                            <Button
                                size="sm"
                                variant={bill.paid ? "success" : "secondary"}
                                onClick={e => {
                                    e.stopPropagation();
                                    togglePaid(bill.id);
                                }}
                            >
                                {bill.autopay ? "AUTO PAY" : bill.paid ? "PAID" : "MARK PAID"}
                            </Button>
                        </div>
                    ))}
                </div>
            </Card>

        </div>
    );
}
