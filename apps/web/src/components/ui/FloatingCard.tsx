import React from "react";

export type FloatingCardElevation = "subtle" | "floating" | "modal";

interface FloatingCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  elevation?: FloatingCardElevation;
  className?: string;
  zIndex?: "map" | "pins" | "floating" | "popover" | "modal" | number;
}

export const FloatingCard: React.FC<FloatingCardProps> = ({
  children,
  elevation = "floating",
  className = "",
  zIndex = "floating",
  style,
  ...props
}) => {
  let shadowStyle = "0px 8px 24px rgba(0, 0, 0, 0.08)";
  if (elevation === "subtle") {
    shadowStyle = "0px 2px 8px rgba(0, 0, 0, 0.04)";
  } else if (elevation === "modal") {
    shadowStyle = "0px -4px 32px rgba(0, 0, 0, 0.12)";
  }

  let zIndexVal = 10;
  if (typeof zIndex === "number") {
    zIndexVal = zIndex;
  } else if (zIndex === "map") {
    zIndexVal = 1;
  } else if (zIndex === "pins") {
    zIndexVal = 5;
  } else if (zIndex === "floating") {
    zIndexVal = 10;
  } else if (zIndex === "popover") {
    zIndexVal = 50;
  } else if (zIndex === "modal") {
    zIndexVal = 100;
  }

  return (
    <div
      {...props}
      data-testid="floating-card"
      data-elevation={elevation}
      className={`bg-white rounded-xl border border-slate-100 overflow-hidden transition-shadow duration-200 ${className}`}
      style={{
        borderRadius: "24px",
        boxShadow: shadowStyle,
        zIndex: zIndexVal,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export default FloatingCard;

