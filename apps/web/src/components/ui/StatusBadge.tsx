import React from "react";

export type ReportLifecycleStatus = "Submitted" | "Under Review" | "Assigned" | "Resolved";

interface StatusBadgeProps {
  status: ReportLifecycleStatus | string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = "" }) => {
  const norm = status.toLowerCase();

  let bg = "#F1F5F9";
  let color = "#334155";
  let border = "#CBD5E1";
  let label = status;

  if (norm === "submitted") {
    bg = "#F1F5F9";
    color = "#334155";
    border = "#CBD5E1";
    label = "Submitted";
  } else if (norm === "under review" || norm === "under_review") {
    bg = "#FEF3C7";
    color = "#B45309";
    border = "#FDE68A";
    label = "Under Review";
  } else if (norm === "assigned") {
    bg = "#E1F2EF";
    color = "#0B6B61";
    border = "#A8DADC";
    label = "Assigned";
  } else if (norm === "resolved") {
    bg = "#DCFCE7";
    color = "#15803D";
    border = "#BBF7D0";
    label = "Resolved";
  }

  return (
    <span
      data-testid={`status-badge-${norm.replace(/\s+/g, "-")}`}
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${className}`}
      style={{
        backgroundColor: bg,
        color: color,
        border: `1px solid ${border}`,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full mr-1.5"
        style={{ backgroundColor: color }}
      />
      {label}
    </span>
  );
};

export default StatusBadge;

