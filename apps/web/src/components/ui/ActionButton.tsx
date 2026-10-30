import React from "react";

export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

interface ActionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant;
  fullWidth?: boolean;
  isLoading?: boolean;
  icon?: React.ReactNode;
  className?: string;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  children,
  variant = "primary",
  fullWidth = false,
  isLoading = false,
  icon,
  className = "",
  disabled,
  ...props
}) => {
  let bg = "#0B6B61";
  let color = "#FFFFFF";
  let border = "none";
  let hoverClass = "hover:bg-[#08544C]";

  if (variant === "primary") {
    bg = "#0B6B61";
    color = "#FFFFFF";
    border = "none";
    hoverClass = "hover:bg-[#08544C] active:bg-[#06403A]";
  } else if (variant === "secondary") {
    bg = "#FFFFFF";
    color = "#0B6B61";
    border = "1.5px solid #0B6B61";
    hoverClass = "hover:bg-[#E1F2EF] active:bg-[#C9E7E2]";
  } else if (variant === "danger") {
    bg = "#FCE8E2";
    color = "#C53030";
    border = "1px solid rgba(197, 48, 48, 0.2)";
    hoverClass = "hover:bg-[#F9D2C7] active:bg-[#F5BCAD]";
  } else if (variant === "ghost") {
    bg = "transparent";
    color = "#64748B";
    border = "none";
    hoverClass = "hover:bg-slate-100 active:bg-slate-200";
  }

  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center h-[52px] min-h-[48px] px-6 rounded-full font-bold text-center text-sm md:text-base transition-all duration-150 select-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#0B6B61] disabled:opacity-50 disabled:cursor-not-allowed ${
        fullWidth ? "w-full" : ""
      } ${hoverClass} ${className}`}
      style={{
        backgroundColor: bg,
        color: color,
        border: border,
        boxShadow: variant === "primary" ? "0 4px 12px rgba(11, 107, 97, 0.2)" : undefined,
      }}
    >
      {isLoading ? (
        <span className="inline-flex items-center">
          <svg
            className="animate-spin -ml-1 mr-2.5 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Processing...
        </span>
      ) : (
        <span className="inline-flex items-center justify-center">
          {icon && <span className="mr-2 inline-flex items-center">{icon}</span>}
          {children}
        </span>
      )}
    </button>
  );
};

export default ActionButton;

