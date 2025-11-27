import * as fundsApi from "../../api/funds.js";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Card from "../../components/Card/Card";
import Button from "../../components/Button/Button";
import styles from "./Funds.module.css";

export default function Funds() {
  const [funds, setFunds] = useState([]);
  const [selectedFund, setSelectedFund] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [txModalOpen, setTxModalOpen] = useState(false);

  const loadFunds = async () => {
    try {
      const res = await fundsApi.listFunds();
      setFunds(res.data || []);
    } catch (e) {
      console.error("Failed to load funds", e);
    }
  };

  useEffect(() => {
    loadFunds();
  }, []);

  return (
    <motion.main
      className={styles.funds}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className={styles.headerRow}>
        <div className={styles.headerActions}>
          <Button onClick={() => { setSelectedFund(null); setSettingsOpen(true); }}>
            + New Fund
          </Button>
        </div>
      </div>

      <div className={styles.grid}>
        <Card title="Summary" variant="default">
          <div className={styles.summary}>
            <div>Number of funds: <strong>{funds.length}</strong></div>
            <div>Total across funds: <strong>${funds.reduce((s, f) => s + (f.balance || 0), 0).toFixed(2)}</strong></div>
          </div>
        </Card>

        <Card title="Support Funds" variant="default">
          <FundList
            funds={funds.filter(f => f.type === "support")}
            onOpenSettings={(f) => { setSelectedFund(f); setSettingsOpen(true); }}
            onOpenTransaction={(f) => { setSelectedFund(f); setTxModalOpen(true); }}
          />
        </Card>

        <Card title="Other Funds" variant="default">
          <FundList
            funds={funds.filter(f => f.type !== "support")}
            onOpenSettings={(f) => { setSelectedFund(f); setSettingsOpen(true); }}
            onOpenTransaction={(f) => { setSelectedFund(f); setTxModalOpen(true); }}
          />
        </Card>
      </div>

      <SupportFundSettings
        open={settingsOpen}
        fund={selectedFund}
        onClose={() => { setSettingsOpen(false); loadFunds(); }}
      />

      <TransactionModal
        open={txModalOpen}
        fund={selectedFund}
        onClose={() => { setTxModalOpen(false); loadFunds(); }}
      />
    </motion.main>
  );
}
