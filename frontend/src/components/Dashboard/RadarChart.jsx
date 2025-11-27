import React from "react";

/**
 * Minimal SVG radar (spider) chart.
 * - data: [{name, value}] where value is percentage-ish (0-100)
 * - size: px of width/height
 * - color: optional fill stroke color
 *
 * This is intentionally lightweight and library-free.
 */

function normalize(data, max = 100) {
  const rad = (deg) => (deg * Math.PI) / 180;
  const total = data.length;
  const cx = 0;
  return data.map((d, i) => {
    const angle = (360 / total) * i - 90; // start at top
    const r = (d.value / max);
    return {
      ...d,
      x: Math.cos(rad(angle)) * r,
      y: Math.sin(rad(angle)) * r,
      angle,
    };
  });
}

export default function RadarChart({ data = [], size = 220, color = "rgba(47,143,255,0.25)" }) {
  const margin = 12;
  const chartSize = size;
  const cx = chartSize / 2;
  const cy = chartSize / 2;
  const maxRadius = (chartSize / 2) - margin;

  // build points scaled to radius
  const nodes = normalize(data, 100).map(n => ({
    ...n,
    px: cx + n.x * maxRadius,
    py: cy + n.y * maxRadius,
    labelX: cx + n.x * (maxRadius + 18),
    labelY: cy + n.y * (maxRadius + 18),
  }));

  // polygon points
  const polygonPoints = nodes.map(n => `${n.px},${n.py}`).join(" ");

  return (
    <svg width={chartSize} height={chartSize} viewBox={`0 0 ${chartSize} ${chartSize}`} role="img" aria-label="radar chart">
      {/* circular grid (3 rings) */}
      <g opacity="0.06" stroke="var(--text-secondary)" strokeWidth="1" fill="none">
        <circle cx={cx} cy={cy} r={maxRadius * 0.33} />
        <circle cx={cx} cy={cy} r={maxRadius * 0.66} />
        <circle cx={cx} cy={cy} r={maxRadius} />
      </g>

      {/* radial lines */}
      <g opacity="0.06" stroke="var(--text-secondary)" strokeWidth="1">
        {nodes.map((n, i) => (
          <line key={i} x1={cx} y1={cy} x2={n.px} y2={n.py} />
        ))}
      </g>

      {/* filled polygon */}
      <polygon
        points={polygonPoints}
        fill={color}
        stroke="var(--primary-blue)"
        strokeWidth="1.5"
        fillOpacity="0.35"
      />

      {/* nodes */}
      <g>
        {nodes.map((n, i) => (
          <circle key={i} cx={n.px} cy={n.py} r={4} fill="var(--primary-blue)" stroke="transparent" />
        ))}
      </g>

      {/* labels */}
      <g fontSize="10" fill="var(--text-secondary)" fontFamily="'Exo 2', sans-serif">
        {nodes.map((n, i) => (
          <text key={i} x={n.labelX} y={n.labelY} textAnchor={n.x < 0 ? "end" : "start"} dominantBaseline="middle">
            {n.name}
          </text>
        ))}
      </g>
    </svg>
  );
}
