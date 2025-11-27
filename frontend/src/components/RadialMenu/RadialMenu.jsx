import React, { useState, useRef, useEffect } from "react";
import styles from "./RadialMenu.module.css";
import logo from "../../assets/logo.png";
import {
  HomeIcon,
  CreditCardIcon,
  ChartPieIcon,
  BanknotesIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  BuildingLibraryIcon,
  WalletIcon,
  ReceiptPercentIcon
} from "@heroicons/react/24/outline";
import { useNavigate } from "react-router-dom";

const RadialMenu = () => {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  const iconStyle = {
    color: "var(--trim-red)",
    filter: "drop-shadow(0 0 32px 8px var(--glow-silver)), drop-shadow(0 0 16px 4px var(--glow-silver))",
  };

  const menuItems = [
    { name: "Dashboard", icon: <HomeIcon width={28} style={iconStyle} />, path: "/dashboard" },
    { name: "Income", icon: <BanknotesIcon width={28} style={iconStyle} />, path: "/income" },
    { name: "Bills", icon: <CreditCardIcon width={28} style={iconStyle} />, path: "/bills" },
    { name: "Accounts", icon: <BuildingLibraryIcon width={28} style={iconStyle} />, path: "/accounts" },
    { name: "Funds", icon: <WalletIcon width={28} style={iconStyle} />, path: "/funds" },
    { name: "Debt", icon: <ReceiptPercentIcon width={28} style={iconStyle} />, path: "/debt" },
    { name: "Reports", icon: <ChartPieIcon width={28} style={iconStyle} />, path: "/reports" },
    { name: "Settings", icon: <Cog6ToothIcon width={28} style={iconStyle} />, path: "/settings" },
    { name: "Logout", icon: <ArrowRightOnRectangleIcon width={28} style={iconStyle} />, path: "/login" },
  ];

  // Close when clicking outside
  const onOutside = (e) => {
    if (menuRef.current && !menuRef.current.contains(e.target)) {
      setOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", onOutside);
    return () => document.removeEventListener("mousedown", onOutside);
  }, []);

  const handleNavigate = (path) => {
    setOpen(false);
    navigate(path);
  };

  return (
    <div ref={menuRef} className={styles.container}>
      {/* Half-circle menu */}
      <div className={`${styles.menu} ${open ? styles.open : ""}`}>
        {menuItems.map((item, index) => {
          const angle = -90 - 90 + (index * 180) / (menuItems.length - 1);
          const radius = 150; // Much larger for clear spacing

          return (
            <button
              key={item.name}
              className={styles.menuItem}
              style={{
                "--angle": `${angle}deg`,
                "--radius": `${radius}px`,
                "--delay": `${index * 0.05}s`,
              }}
              onClick={() => handleNavigate(item.path)}
            >
              {item.icon}
            </button>
          );
        })}
      </div>

      {/* Logo toggle button */}
      <button
        className={`${styles.logoButton} ${open ? styles.active : ""}`}
        onClick={() => setOpen(!open)}
      >
        <img src={logo} alt="PATRIOT logo" className={styles.logoImage} />
      </button>
    </div>
  );
};

export default RadialMenu;
