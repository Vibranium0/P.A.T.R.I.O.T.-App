import React, { useEffect, useState } from "react";
import styles from "./Bills.module.css";
import OverviewTab from "./OverviewTab";
import ScheduleTab from "./ScheduleTab";
import Card from "../../components/Card/Card";
import { FiSettings } from "react-icons/fi";
import Button from "../../components/Button/Button";


export default function Bills() {
  // Load bills from localStorage or default
  const loadBills = () => {
    // ...existing code...
    try {
      const raw = localStorage.getItem("patriot_bills");
      if (!raw) return [];
      return JSON.parse(raw);
    } catch {
      return [];
    }
  };

  const loadSettings = () => {
    try {
      const raw = localStorage.getItem("patriot_bills_settings");
      if (!raw) {
        return {
          startDate: "",
          startBalance: 0,
          bufferAmount: 0,
          monthsToProject: 3,
          currentAccountBalance: 0,
        };
      }
      return JSON.parse(raw);
    } catch {
      return {
        startDate: "",
        startBalance: 0,
        bufferAmount: 0,
        monthsToProject: 3,
        currentAccountBalance: 0,
      };
    }
  };

  const [bills, setBills] = useState(loadBills());
  const [settings, setSettings] = useState(loadSettings());
  const [activeTab, setActiveTab] = useState("overview");
  const [scheduleStartDate, setScheduleStartDate] = useState("");

  useEffect(() => {
    localStorage.setItem("patriot_bills", JSON.stringify(bills));
  }, [bills]);

  useEffect(() => {
    localStorage.setItem("patriot_bills_settings", JSON.stringify(settings));
  }, [settings]);

  // helpers for child tabs to mutate state
  const addBill = (bill) => setBills((s) => [...s, { ...bill, id: Date.now() }]);
  const updateBill = (id, patch) =>
    setBills((s) => s.map((b) => (b.id === id ? { ...b, ...patch } : b)));
  const deleteBill = (id) => setBills((s) => s.filter((b) => b.id !== id));
  const replaceBills = (newBills) => setBills(newBills);

  return (
    <div className={styles.wrapper}>
      <div className={styles.tabRow}>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            className={`${styles.tabButton} ${activeTab === "overview" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === "schedule" ? styles.tabActive : ""}`}
            onClick={() => setActiveTab("schedule")}
          >
            Schedule
          </button>
        </div>
        {activeTab === "schedule" && (
          <button className={styles.settingsButton} title="Settings" onClick={() => setSettingsDialogOpen(true)}>
            <FiSettings className={styles.settingsIcon} />
          </button>
        )}
      </div>
      {activeTab === "overview" && (
        <OverviewTab
          bills={bills}
          addBill={addBill}
          updateBill={updateBill}
          deleteBill={deleteBill}
          settings={settings}
          setSettings={setSettings}
          replaceBills={replaceBills}
        />
      )}
      {activeTab === "schedule" && (
        <>
          <ScheduleTab
            bills={bills}
            settings={settings}
            setSettings={setSettings}
            scheduleStartDate={scheduleStartDate}
            setScheduleStartDate={setScheduleStartDate}
          />
        </>
      )}
    </div>
  );
}
