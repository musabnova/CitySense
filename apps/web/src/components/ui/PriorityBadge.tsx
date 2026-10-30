import React from "react";

export type PriorityLevel = "High" | "Medium" | "Low" | "Priority 1" | "Priority 2" | "Priority 3" | "Priority 4";

interface PriorityBadgeProps {
  priority: PriorityLevel;
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, className = "" }) => {
  // Normalize priority string
  const normalized = priority.toLowerCase();
  const isHigh = normalized === "high" || normalized === "priority 1";
  const isMed = normalized === "medium" || normalized === "priority 2" || normalized === "priority 3";

  if (isHigh) {
    return (
      <span
        data-testid="priority-badge-high"
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold transition-colors ${className}`}
        style={{
          backgroundColor: "#FCE8E2",
          color: "#C53030",
          border: "1px solid rgba(197, 48, 48, 0.2)",
        }}
      >
        High
      </span>
    );
  }

  if (isMed) {
    return (
      <span
        data-testid="priority-badge-med"
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold transition-colors ${className}`}
        style={{
          backgroundColor: "#FEF3C7",
          color: "#B45309",
          border: "1px solid rgba(180, 83, 9, 0.2)",
        }}
      >
        Medium
      </span>
    );
  }

  // Low / Routine (uses accessible #0F766E text on #E6FFFA background for 5.23:1 WCAG AA contrast)
  return (
    <span
      data-testid="priority-badge-low"
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold transition-colors ${className}`}
      style={{
        backgroundColor: "#E6FFFA",
        color: "#0F766E",
        border: "1px solid rgba(13, 148, 136, 0.3)",
      }}
    >
      Low
    </span>
  );
};

export default PriorityBadge;
