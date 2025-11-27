import React, { useState, useEffect } from "react";
import Card from "../../components/Card/Card";
import Button from "../../components/Button/Button";
import styles from "./ScheduleTab.module.css";

/*
  Client-side schedule generator.
  - bills: array
  - settings: { startDate, startBalance, bufferAmount, monthsToProject, currentAccountBalance }
*/
export default function ScheduleTab({ bills, settings, setSettings, scheduleStartDate, setScheduleStartDate }) {
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // try restore cached last schedule
    try {
      const cache = JSON.parse(localStorage.getItem("patriot_bills_schedules") || "[]");
      if (cache && cache.length) {
        setSchedule(cache[0]); // most recent
      }
    } catch { }
  }, []);

  // date helpers
  const addDays = (d, days) => {
    const nd = new Date(d);
    nd.setDate(nd.getDate() + days);
    return nd;
  };
  const addMonths = (d, months) => {
    const nd = new Date(d);
    const desired = nd.getDate();
    nd.setMonth(nd.getMonth() + months);

    // handle month-end rollover (e.g., Jan 31 + 1 month -> Feb 28)
    if (nd.getDate() !== desired) {
      nd.setDate(0); // last day of prev month
    }
    return nd;
  };

  const iso = (d) => new Date(d).toISOString().slice(0, 10);

  const generateSchedule = async () => {
    setError("");
    setLoading(true);
    setSchedule(null);

    if (!settings.startDate) {
      setError("Please set a Start Date in the Overview tab.");
      setLoading(false);
      return;
    }

    if (typeof settings.startBalance !== "number") {
      setError("Please set a numeric starting balance.");
      setLoading(false);
      return;
    }

    try {
      const months = Number(settings.monthsToProject || 3);
      const start = new Date(scheduleStartDate || settings.startDate);
      const end = addMonths(start, months);

      // Step 1: Calculate starting balance for scheduleStartDate
      const settingsDate = new Date(settings.startDate);
      let balance = Number(settings.startBalance || 0);
      // Gather all bill events between settingsDate and scheduleStartDate (exclusive)
      let interimEvents = [];
      bills.forEach((b) => {
        const nextDue = new Date(b.nextDue);
        if (isNaN(nextDue)) return;
        let occ = new Date(nextDue);
        // Fast-forward to first occurrence >= settingsDate
        while (occ < settingsDate) {
          switch (b.frequency) {
            case "monthly": occ = addMonths(occ, 1); break;
            case "biweekly": occ = addDays(occ, 14); break;
            case "weekly": occ = addDays(occ, 7); break;
            case "once": default: occ = addDays(occ, 99999); break;
          }
        }
        // Collect events between settingsDate and scheduleStartDate
        while (occ < start) {
          interimEvents.push({ date: new Date(occ), name: b.name, amount: Number(b.amount || 0) });
          switch (b.frequency) {
            case "monthly": occ = addMonths(occ, 1); break;
            case "biweekly": occ = addDays(occ, 14); break;
            case "weekly": occ = addDays(occ, 7); break;
            case "once": default: occ = addDays(occ, 99999); break;
          }
        }
      });
      // Sort and apply interim events to balance
      interimEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
      interimEvents.forEach(ev => {
        balance = Number((balance - ev.amount).toFixed(2));
      });
      // Step 2: Build schedule events from scheduleStartDate to end
      let events = [];
      bills.forEach((b) => {
        const nextDue = new Date(b.nextDue);
        if (isNaN(nextDue)) return;
        let occ = new Date(nextDue);
        // Fast-forward to first occurrence >= start
        while (occ < start) {
          switch (b.frequency) {
            case "monthly": occ = addMonths(occ, 1); break;
            case "biweekly": occ = addDays(occ, 14); break;
            case "weekly": occ = addDays(occ, 7); break;
            case "once": default: occ = addDays(occ, 99999); break;
          }
        }
        // Collect events within schedule window
        while (occ <= end) {
          events.push({ date: new Date(occ), name: b.name, amount: Number(b.amount || 0) });
          switch (b.frequency) {
            case "monthly": occ = addMonths(occ, 1); break;
            case "biweekly": occ = addDays(occ, 14); break;
            case "weekly": occ = addDays(occ, 7); break;
            case "once": default: occ = addDays(occ, 99999); break;
          }
        }
      });
      // Sort events by date
      events.sort((a, b) => new Date(a.date) - new Date(b.date));
      // Step 3: Build rows starting from scheduleStartDate and calculated balance
      const rows = [];
      // Add initial row for scheduleStartDate with starting balance
      rows.push({
        date: iso(start),
        name: "Starting Balance",
        amount: 0,
        balance,
        below_buffer: settings.bufferAmount && balance < Number(settings.bufferAmount || 0),
      });
      let lowest = balance;
      let currentAccountBalance = Number(settings.currentAccountBalance || settings.startBalance || 0);
      events.forEach((ev) => {
        balance = Number((balance - ev.amount).toFixed(2));
        lowest = Math.min(lowest, balance);
        rows.push({
          date: iso(ev.date),
          name: ev.name,
          amount: ev.amount,
          balance,
          below_buffer: settings.bufferAmount && balance < Number(settings.bufferAmount || 0),
        });
      });

      // compute expectedMinimum (lowest from expected column)
      const expectedMin = lowest;

      // compute actualMinimum from currentAccountBalance series:
      // Basic approach: assume actual starting balance = settings.currentAccountBalance (if given)
      let actualMin = null;
      if (settings.currentAccountBalance !== undefined && settings.currentAccountBalance !== null) {
        let actBal = Number(settings.currentAccountBalance || 0);
        actualMin = actBal;
        // apply events from today forward? We will apply all events >= today to actual starting balance
        const today = new Date();
        const futureEvents = rows.filter((r) => new Date(r.date) >= today);
        futureEvents.forEach((fe) => {
          actBal = Number((actBal - fe.amount).toFixed(2));
          actualMin = Math.min(actualMin, actBal);
        });
      }

      // extra payment needed to lift actualMin up to expectedMin (if actualMin < expectedMin)
      let extraPayment = 0;
      if (actualMin !== null && actualMin < expectedMin) {
        extraPayment = Number((expectedMin - actualMin).toFixed(2));
      }

      const result = {
        generated_at: new Date().toISOString(),
        start: iso(start),
        end: iso(end),
        entries: rows,
        lowest_balance: expectedMin,
        actual_minimum: actualMin,
        extra_payment_needed: extraPayment,
      };

      // cache schedules (keep last 3)
      try {
        const raw = JSON.parse(localStorage.getItem("patriot_bills_schedules") || "[]");
        const newCache = [result, ...raw].slice(0, 3);
        localStorage.setItem("patriot_bills_schedules", JSON.stringify(newCache));
      } catch { }

      setSchedule(result);
    } catch (err) {
      console.error(err);
      setError("Failed to generate schedule: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!schedule) return;
    const rows = [
      ["date", "name", "amount", "balance", "below_buffer"],
      ...schedule.entries.map((r) => [r.date, r.name, r.amount, r.balance, r.below_buffer ? 1 : 0]),
    ];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bills_schedule_${schedule.generated_at.slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.scheduleTabContainer}>
      {/* Removed Schedule Settings Card, now handled by modal in Bills.jsx */}
      <Card title="Generate Bills Schedule">
        <div className={styles.formRow}>
          <div>
            <label>Schedule start date</label>
            <input type="date" value={scheduleStartDate || ""} onChange={e => setScheduleStartDate(e.target.value)} />
          </div>
          {/* Removed Start balance input, now handled in schedule settings modal */}
          <div>
            <label>Months to project</label>
            <input type="number" min="1" max="24" value={settings.monthsToProject || 3} onChange={(e) => setSettings({ ...settings, monthsToProject: Number(e.target.value) })} />
          </div>
          <div>
            <label>Buffer amount</label>
            <input type="number" value={settings.bufferAmount || 0} onChange={(e) => setSettings({ ...settings, bufferAmount: Number(e.target.value) })} />
          </div>
          <div>
            <label>Current account balance</label>
            <input type="number" value={settings.currentAccountBalance || 0} onChange={(e) => setSettings({ ...settings, currentAccountBalance: Number(e.target.value) })} />
          </div>
        </div>

        <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
          <Button onClick={generateSchedule} disabled={loading}>{loading ? "Generating…" : "Generate Schedule"}</Button>
          <Button variant="secondary" onClick={() => {
            const raw = localStorage.getItem("patriot_bills_schedules");
            if (!raw) { alert("No cached schedules."); return; }
            try {
              const cache = JSON.parse(raw);
              if (!cache || cache.length === 0) return alert("No cached schedules.");
              setSchedule(cache[0]);
            } catch { alert("Failed to load cached schedules."); }
          }}>Load Last</Button>
          <Button variant="secondary" onClick={downloadCSV} disabled={!schedule}>Download CSV</Button>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        {schedule && (
          <div className={styles.results}>
            <div className={styles.resultsSummary}>
              <div>Range: {schedule.start} → {schedule.end}</div>
              <div>Lowest Expected Balance: ${schedule.lowest_balance}</div>
              <div>Actual Minimum: {schedule.actual_minimum === null ? "—" : `$${schedule.actual_minimum}`}</div>
              <div>Extra Payment Needed: ${schedule.extra_payment_needed}</div>
            </div>

            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Bill</th>
                  <th>Amount</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody>
                {schedule.entries.map((r, i) => (
                  <tr key={i} className={r.below_buffer ? styles.rowBelowBuffer : ""}>
                    <td>{r.date}</td>
                    <td>{r.name}</td>
                    <td>${r.amount}</td>
                    <td>${r.balance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
