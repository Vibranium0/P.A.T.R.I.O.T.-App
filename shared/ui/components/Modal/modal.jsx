import React from "react";
import styles from "./Modal.module.css";
import Card from "../Card/Card";
import Button from "../Button/Button";

export default function Modal({ open, onSave, onCancel, title = "Modal Title", children }) {
    if (!open) return null;
    return (
        <div className={styles.overlay}>
            <Card title={title}>
                <div style={{ marginBottom: "1.5rem" }}>
                    {children}
                </div>
                <div className={styles.modalActions} style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                    <Button variant="danger" size="md" onClick={onCancel}>
                        Cancel
                    </Button>
                    {onSave && (
                        <Button variant="primary" size="md" onClick={onSave}>
                            Save
                        </Button>
                    )}
                </div>
            </Card>
        </div>
    );
}
