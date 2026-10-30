import React from "react";

interface FilterChipProps {
  label: string;
  active?: boolean;
  onClick?: () => void;
  count?: number;
  className?: string;
  disabled?: boolean;
}

export const FilterChip: React.FC<FilterChipProps> = ({
  label,
  active = false,
  onClick,
  count,
  className = "",
  disabled = false,
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      data-testid={`filter-chip-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`}
      data-active={active ? "true" : "false"}
      className={`inline-flex items-center justify-center px-4 py-2.5 min-h-[48px] rounded-full text-sm font-medium transition-all duration-150 select-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0B6B61] disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      style={{
        backgroundColor: active ? "#0B6B61" : "#FFFFFF",
        color: active ? "#FFFFFF" : "#64748B",
        border: active ? "1px solid #0B6B61" : "1px solid #E2E8F0",
        boxShadow: active
          ? "0 2px 4px rgba(11, 107, 97, 0.16)"
          : "0 1px 2px rgba(0, 0, 0, 0.04)",
      }}
    >
      <span>{label}</span>
      {count !== undefined && (
        <span
          className="ml-2 px-1.5 py-0.5 text-xs font-bold rounded-full"
          style={{
            backgroundColor: active ? "rgba(255, 255, 255, 0.25)" : "#F1F5F9",
            color: active ? "#FFFFFF" : "#475569",
          }}
        >
          {count}
        </span>
      )}
    </button>
  );
};

export default FilterChip;

