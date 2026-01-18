
import React, { useEffect, useState } from "react";
import styles from "./Income.module.css";
import Card from "../../../../../shared/ui/components/Card/Card";
import Button from "../../../../../shared/ui/components/Button/Button";
import Modal from "../../../../../shared/ui/components/Modal/modal";
import TextBox from "../../../../../shared/ui/components/TextBox/TextBox";
import CurrencyBox from "../../../../../shared/ui/components/TextBox/CurrencyBox";
import StyledDatePicker from "../../../../../shared/ui/components/TextBox/StyledDatePicker";
import { motion } from "framer-motion";
import Dropdown from "../../../../../shared/ui/components/Dropdown/dropdown";
import apiClient from "../../api/client";

export default function Income() {
  const [funds, setFunds] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [depositTo, setDepositTo] = useState("");
  const [incomeList, setIncomeList] = useState([]);
  const [summary, setSummary] = useState({ total: 0, bySource: {} });
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    source: "",
    amount: "",
    date: "",
    supportIncluded: false,
  });
  const [incomeName, setIncomeName] = useState("");
  const [incomeAmount, setIncomeAmount] = useState("");
  const [incomeDate, setIncomeDate] = useState("");
  const [incomeSource, setIncomeSource] = useState("");
  const [showNewSourceInput, setShowNewSourceInput] = useState(false);
  const [newSource, setNewSource] = useState("");

  // Load income records + summary from backend
  const loadIncome = async () => {
    try {
      const res = await apiClient.get("/income/income");
      setIncomeList(res.data.data || []);

      const summaryRes = await apiClient.get("/income/income/summary");
      setSummary(summaryRes.data.data || { total: 0, bySource: {} });
    } catch (err) {
      console.error("Failed to load income", err);
    }
  };

  useEffect(() => {
    loadIncome();
    // Load funds for Deposit To dropdown
    apiClient.get("/funds/")
      .then((res) => {
        if (Array.isArray(res.data)) {
          setFunds(res.data);
        }
      })
      .catch((err) => console.error("Failed to load funds", err));

    // Load accounts for Deposit To dropdown
    apiClient.get("/accounts/list")
      .then((res) => {
        if (Array.isArray(res.data)) {
          setAccounts(res.data);
        }
      })
      .catch((err) => console.error("Failed to load accounts", err));
  }, []);

  const submitIncome = async () => {
    try {
      await apiClient.post("/income/income", form);
      setForm({ source: "", amount: "", date: "", supportIncluded: false });
      loadIncome();
    } catch (err) {
      console.error("Failed to submit income", err);
    }
  };

  const deleteIncome = async (id) => {
    try {
      await apiClient.delete(`/income/income/${id}`);
      loadIncome();
    } catch (err) {
      console.error("Failed to delete income", err);
    }
  };

  // Build dropdown options from summary.bySource
  const sourceOptions = [
    ...Object.keys(summary.bySource),
    "Add new source..."
  ];

  // Handler for dropdown selection
  const handleSourceSelect = (option) => {
    if (option === "Add new source...") {
      setShowNewSourceInput(true);
    } else {
      setIncomeSource(option);
      setShowNewSourceInput(false);
    }
  };

  // Handler for adding new source
  const handleAddSource = async () => {
    // Save new source to backend (or local file if required)
    // For now, just add to summary.bySource for demo
    setSummary((prev) => ({
      ...prev,
      bySource: { ...prev.bySource, [newSource]: 0 }
    }));
    setIncomeSource(newSource);
    setShowNewSourceInput(false);
    setNewSource("");
  };

  return (
    <motion.main
      className={styles.wrapper}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Page title is now standardized in TopSecretHeader via Layout */}

      {/* SUMMARY */}
      <div className={styles.summaryGrid}>
        <Card title="Total Income" variant="success">
          <p className={styles.summaryValue}>${summary.total}</p>
          <Button
            onClick={() => setModalOpen(true)}
            style={{ marginTop: "1rem" }}
          >
            Add Income
          </Button>
        </Card>

        <Card title="Sources" variant="default">
          {Object.entries(summary.bySource).map(([source, amt]) => (
            <p key={source} className={styles.sourceRow}>
              <span>{source}</span>
              <span>${amt}</span>
            </p>
          ))}
        </Card>
      </div>

      {/* INCOME LIST */}
      <Card title="Income Records" variant="default">
        <div className={styles.list}>
          {incomeList.length === 0 ? (
            <p className={styles.empty}>No income records yet.</p>
          ) : (
            incomeList.map((i) => (
              <div key={i.id} className={styles.row}>
                <div>
                  <p className={styles.source}>{i.source}</p>
                  <p className={styles.date}>
                    {new Date(i.date).toLocaleDateString()}
                  </p>
                </div>
                <p className={styles.amount}>${i.amount}</p>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => deleteIncome(i.id)}
                >
                  Delete
                </Button>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Log Income Modal */}
      <Modal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onSave={() => {/* Add save logic here */ }}
        title="Log Income"
      >
        <TextBox
          value={incomeName}
          onChange={setIncomeName}
          placeholder="Income Name"
        />
        <CurrencyBox
          value={incomeAmount}
          onChange={setIncomeAmount}
          placeholder="$0.00"
        />
        <StyledDatePicker
          value={incomeDate}
          onChange={setIncomeDate}
          placeholder="Date"
        />
        <Dropdown
          options={[
            ...funds.map((f) => `Fund: ${f.name}`),
            ...accounts.map((a) => `Account: ${a.name}`)
          ]}
          selected={depositTo}
          onSelect={setDepositTo}
          label="Deposit To"
        />
        <Dropdown
          options={sourceOptions}
          selected={incomeSource}
          onSelect={handleSourceSelect}
          label="Source"
        />
        {showNewSourceInput && (
          <div style={{ marginTop: "0.7rem", display: "flex", gap: "0.5rem" }}>
            <TextBox
              value={newSource}
              onChange={setNewSource}
              placeholder="New Source Name"
            />
            <Button variant="primary" size="sm" onClick={handleAddSource}>
              Add
            </Button>
          </div>
        )}
      </Modal>
    </motion.main>
  );
}