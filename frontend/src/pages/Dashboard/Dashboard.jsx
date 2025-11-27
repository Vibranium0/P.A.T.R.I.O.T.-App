import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import Layout from "../../components/Layout/Layout";
import Card from "../../components/Card/Card";
import SummaryCard from "../../components/Dashboard/SummaryCard";
import RadarChart from "../../components/Dashboard/RadarChart";
import Modal from "../../components/Modal/Modal";
import Button from "../../components/Button/Button";
import styles from "./Dashboard.module.css";

/**
 * Dashboard page (Phase 9 - cinematic UI)
 * - Uses theme CSS variables from your colors/effects files
 * - Minimal local state; designed to be wired to /api endpoints easily
 */

const demoSummary = {
  income: 2600,
  biweeklyTotal: 1300,
  expenses: 600,
  cash: 120,
  savings: 580,
  bills: 900, // example total bills
  transfers: 400, // example total transfers to funds
};

const billsByCategory = [
  { name: "Rent/Mortgage", value: 40 },
  { name: "Utilities", value: 10 },
  { name: "Subscriptions", value: 8 },
  { name: "Insurance", value: 12 },
  { name: "Other", value: 30 },
];

const debtByCategory = [
  { name: "Credit Card", value: 55 },
  { name: "Student Loan", value: 25 },
  { name: "Auto Loan", value: 20 },
];

const Dashboard = () => {
  // derive formatted summary array for rendering
  const summaryItems = useMemo(() => ([
    // ...existing code...
    { label: "Total (biweekly)", value: demoSummary.biweeklyTotal, prefix: "$", key: "total" },
    { label: "Expenses", value: demoSummary.expenses, prefix: "$", key: "expenses" },
    { label: "Cash", value: demoSummary.cash, prefix: "$", key: "cash" },
    { label: "Savings", value: demoSummary.savings, prefix: "$", key: "savings" },
    { label: "Surplus", value: demoSummary.income - demoSummary.bills - demoSummary.transfers, prefix: "$", key: "surplus" },
  ]), []);

  const [modalOpen, setModalOpen] = useState(false);
  const [selected, setSelected] = React.useState('Option 1');
  const [plainText, setPlainText] = React.useState('');
  const [currency, setCurrency] = React.useState('');
  const [date, setDate] = React.useState('');
  const options = ['Option 1', 'Option 2', 'Option 3'];

  const handleOpenModal = () => setModalOpen(true);
  const handleCloseModal = () => setModalOpen(false);

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: "easeOut" }}
        className={styles.page}
      >
        {/* Top row summary KPI cards */}
        <div className={styles.summaryRow}>
          {summaryItems.map(item => (
            <SummaryCard
              key={item.key}
              label={item.label}
              value={item.value}
              prefix={item.prefix}
            />
          ))}
        </div>

        {/* Modal Demo Button */}
        <div style={{ margin: "2rem 0", textAlign: "center" }}>
          <button
            style={{
              padding: "0.7rem 1.5rem",
              fontSize: "1.1rem",
              borderRadius: "0.7rem",
              background: "var(--primary-blue)",
              color: "white",
              border: "none",
              boxShadow: "var(--shadow-base)",
              cursor: "pointer"
            }}
            onClick={handleOpenModal}
          >
            Open Modal Demo
          </button>
        </div>

        {/* Modal Demo */}
        <Modal
          open={modalOpen}
          onSave={() => {/* Save logic here */ }}
          onCancel={handleCloseModal}
        >
          <h2 style={{ marginBottom: "1rem" }}>Demo Modal</h2>
          <p>This is what your new modal looks like!</p>
          <button
            style={{
              marginTop: "1.5rem",
              padding: "0.5rem 1.2rem",
              borderRadius: "0.5rem",
              background: "var(--primary-blue)",
              color: "white",
              border: "none",
              cursor: "pointer"
            }}
            onClick={handleCloseModal}
          >
            Close
          </button>
        </Modal>

        {/* Main content grid */}
        <div className={styles.grid}>
          <Card title="Bills by Category" hover>
            <div className={styles.chartRow}>
              <RadarChart data={billsByCategory} size={300} />
              <div className={styles.legend}>
                <p className={styles.legendIntro}>Projected distribution of bills</p>
                <ul>
                  {billsByCategory.map((b) => (
                    <li key={b.name}><strong>{b.name}</strong>: {b.value}%</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>

          <Card title="Debt Breakdown" hover>
            <div className={styles.chartRow}>
              <RadarChart data={debtByCategory} size={300} color="rgba(185,192,201,0.25)" />
              <div className={styles.legend}>
                <p className={styles.legendIntro}>Current debt exposure</p>
                <ul>
                  {debtByCategory.map((b) => (
                    <li key={b.name}><strong>{b.name}</strong>: {b.value}%</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>

          <Card title="Recent Activity" hover>
            <div className={styles.activityList}>
              {/* Replace with live data later */}
              <div className={styles.activityRow}>
                <div>Paycheck</div>
                <div className={styles.activityAmount}>+ $1,300</div>
              </div>
              <div className={styles.activityRow}>
                <div>Groceries — Walmart</div>
                <div className={styles.activityAmount}>- $62.23</div>
              </div>
              <div className={styles.activityRow}>
                <div>Autopay — Electricity</div>
                <div className={styles.activityAmount}>- $72.12</div>
              </div>
              <div className={styles.activityRow}>
                <div>Transfer to Savings</div>
                <div className={styles.activityAmount}>- $150.00</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Button Demo Section */}
        <div style={{ display: 'flex', gap: '1rem', margin: '2rem 0' }}>
          <Button variant="primary" size="md">primary</Button>
          <Button variant="secondary" size="md">secondary</Button>
          <Button variant="danger" size="md">danger</Button>
          <Button variant="ghost" size="md">ghost</Button>
        </div>
      </motion.div>
    </Layout>
  );
};

export default Dashboard;
