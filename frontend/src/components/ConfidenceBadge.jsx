import React from "react";

/**
 * ConfidenceBadge
 * Visualizes the Reasoning Agent's Confidence Score -- the project's
 * headline innovation. Color + label shift with the score so judges can
 * immediately see when the twin is guessing vs. genuinely confident.
 */
export default function ConfidenceBadge({ score, size = "md" }) {
  const pct = Math.round(score * 100);
  let color = "text-red-400 border-red-400/40 bg-red-400/10";
  let label = "Low confidence";
  if (pct >= 75) {
    color = "text-cyan border-cyan/40 bg-cyan/10";
    label = "High confidence";
  } else if (pct >= 45) {
    color = "text-amber border-amber/40 bg-amber/10";
    label = "Moderate confidence";
  }

  const sizeCls = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1";

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-mono ${color} ${sizeCls}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {pct}% · {label}
    </span>
  );
}
