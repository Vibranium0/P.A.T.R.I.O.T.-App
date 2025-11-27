import React from "react";
import styles from "../../styles/hud.module.css";

const HUDEffects = () => {
  const lines = Array.from({ length: 4 });

  return (
    <div className={styles.hudContainer}>
      {lines.map((_, i) => (
        <div
          key={i}
          className={styles.hudLineFlow}
          style={{
            top: `${25 * i + 10}%`,
            animationDelay: `${i * 0.8}s`,
          }}
        />
      ))}
    </div>
  );
};

export default HUDEffects;
