import React from "react";
import styles from "./Layout.module.css";

import HUDLayer from "../HUD/HUDLayer.jsx";
import RadialMenu from "../RadialMenu/RadialMenu";
import TopSecretHeader from "../TopSecretHeader/TopSecretHeader.jsx";

function getPageTitle() {
  const path = window.location.pathname;
  if (path.startsWith("/dashboard")) return "Dashboard";
  if (path.startsWith("/income")) return "Income";
  if (path.startsWith("/bills")) return "Bills";
  if (path.startsWith("/funds")) return "Funds";
  if (path.startsWith("/accounts")) return "Accounts";
  if (path.startsWith("/reports")) return "Reports";
  if (path.startsWith("/settings")) return "Settings";
  if (path.startsWith("/login")) return "Login";
  if (path.startsWith("/register")) return "Register";
  return "";
}

export default function Layout({ children }) {
  const pageTitle = getPageTitle();
  return (
    <div className={styles.layoutWrapper}>
      {/* TOP SECRET HEADER */}
      <TopSecretHeader pageTitle={pageTitle} />

      {/* ===========================
          GLOBAL HUD OVERLAY (FX Layer)
         =========================== */}
      <HUDLayer />

      {/* ===========================
          MAIN CONTENT AREA
         =========================== */}
      <main className={styles.main}>
        {children}
      </main>

      {/* ===========================
          RADIAL MENU (Floating UI)
         =========================== */}
      <div className={styles.radialMenuWrapper}>
        <RadialMenu />
      </div>
    </div>
  );
}
