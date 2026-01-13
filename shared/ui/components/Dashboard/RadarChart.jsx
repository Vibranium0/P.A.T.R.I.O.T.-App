import React from "react";
import {
  HomeIcon,
  BoltIcon,
  CalendarIcon,
  DocumentCurrencyDollarIcon,
  BanknotesIcon,
  CreditCardIcon,
  AcademicCapIcon,
  TruckIcon
} from "@heroicons/react/24/outline";

/**
 * Minimal SVG radar (spider) chart.
 * - data: [{name, value}] where value is percentage-ish (0-100)
 * - size: px of width/height
 * - color: optional fill stroke color
 *
 * This is intentionally lightweight and library-free.
 */

function degToRad(deg) {
  return (deg * Math.PI) / 180;
}

// Pass an `icons` prop: array of React elements (Heroicons)
export default function RadarChart({ data = [], size = 220, color = "var(--primary)", icons = [] }) {
  const margin = 12;
  // Add extra padding for icons so they don't get cut off
  const iconPad = 36;
  const chartSize = size + iconPad * 2;
  const cx = chartSize / 2;
  const cy = chartSize / 2;
  const maxRadius = (size / 2) - margin;
  const total = data.length;
  // Find the largest value in the data for scaling
  const maxValue = data.length > 0 ? Math.max(...data.map(d => d.value)) : 1;

  // All wedges use primary color and glow
  const palette = ['var(--primary)'];
  const glowPalette = ['var(--glow-primary)'];

  // Each slice: equal angle, radius proportional to value
  const angleStep = 360 / total;

  return (
    <svg width={chartSize} height={chartSize} viewBox={`0 0 ${chartSize} ${chartSize}`} role="img" aria-label="radial bar chart">
      <defs>
        {glowPalette.map((glow, i) => (
          <filter id={`wedge-glow-${i}`} key={i} x="-40%" y="-40%" width="180%" height="180%">
            <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor={glow} floodOpacity="1" />
          </filter>
        ))}
      </defs>
      {/* background grid */}
      <g opacity="0.12" stroke="var(--accent-light)" strokeWidth="1" fill="none">
        <circle cx={cx} cy={cy} r={maxRadius * 0.33} />
        <circle cx={cx} cy={cy} r={maxRadius * 0.66} />
        <circle cx={cx} cy={cy} r={maxRadius} />
      </g>

      {/* slices with glow and icons */}
      {data.map((d, i) => {
        const startAngle = -90 + i * angleStep;
        const endAngle = startAngle + angleStep;
        const valueRadius = (d.value / maxValue) * maxRadius;
        // Arc path for slice (from center out, arc, back to center)
        const x1 = cx + Math.cos(degToRad(startAngle)) * valueRadius;
        const y1 = cy + Math.sin(degToRad(startAngle)) * valueRadius;
        const x2 = cx + Math.cos(degToRad(endAngle)) * valueRadius;
        const y2 = cy + Math.sin(degToRad(endAngle)) * valueRadius;
        const largeArcFlag = angleStep > 180 ? 1 : 0;
        const pathData = [
          `M ${cx} ${cy}`,
          `L ${x1} ${y1}`,
          `A ${valueRadius} ${valueRadius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
          'Z',
        ].join(' ');
        const fill = palette[i % palette.length];
        const filterId = `wedge-glow-${i % glowPalette.length}`;
        // Icon position: just outside the outermost circle, centered on wedge
        const midAngle = startAngle + angleStep / 2;
        const iconRadius = maxRadius + 28;
        // Use cx/cy for all calculations to ensure perfect centering
        const iconX = cx + Math.cos(degToRad(midAngle)) * iconRadius;
        const iconY = cy + Math.sin(degToRad(midAngle)) * iconRadius;
        return (
          <g key={i}>
            <path d={pathData} fill={fill} fillOpacity="0.7" stroke="var(--secondary)" strokeWidth="2" filter={`url(#${filterId})`} />
            {icons[i] && (
              <g transform={`translate(${iconX - 14},${iconY - 14})`}>
                {React.cloneElement(icons[i], { width: 28, height: 28, style: { color: 'var(--secondary)', filter: 'drop-shadow(0 0 8px var(--glow-primary))' } })}
              </g>
            )}
          </g>
        );
      })}

      {/* No labels: use external legend for slice identification */}
    </svg>
  );
}
