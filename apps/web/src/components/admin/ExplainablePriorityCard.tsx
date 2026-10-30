"use client";

import React from "react";

interface ExplainablePriorityCardProps {
  priorityRank?: string;
  priorityScore?: number;
  factors?: Array<{ name: string; points: number; detail: string }>;
  priorityRationale?: string;
  className?: string;
}

export const ExplainablePriorityCard: React.FC<ExplainablePriorityCardProps> = ({
  priorityRank = "Priority 1",
  priorityScore = 85,
  factors = [],
  priorityRationale,
  className = "",
}) => {
  // Default additive factors if none provided
  const displayFactors = factors.length > 0 ? factors : [
    { name: "poi_proximity", points: 40, detail: "Near a school / critical POI" },
    { name: "linked_duplicates", points: 20, detail: "Linked duplicate reports (velocity)" },
    { name: "hazard_keywords", points: 15, detail: "Hazard keywords & photo evidence confirmed" },
    { name: "recency", points: 5, detail: "Reported today (< 24h intake)" },
  ];

  return (
    <div
      data-testid="explainable-priority-card"
      className={`rounded-2xl p-4 bg-[#F8FAFC] border border-slate-200/90 space-y-3 ${className}`}
    >
      <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
        <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
          <span>⚡</span>
          <span>Why {priorityRank}?</span>
        </span>
        <span className="text-xs font-mono font-bold text-[#0B6B61] bg-[#E1F2EF] px-2 py-0.5 rounded-full">
          Score: {priorityScore}/100
        </span>
      </div>

      {/* Additive Factor Breakdown */}
      <div className="space-y-1.5 text-xs">
        {displayFactors.map((f, i) => (
          <div key={i} className="flex items-center justify-between text-slate-600">
            <span className="flex items-center gap-1.5 truncate">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0B6B61]" />
              <span className="truncate">{f.detail}</span>
            </span>
            <span className="font-mono font-bold text-slate-700 ml-2">
              +{f.points}
            </span>
          </div>
        ))}
      </div>

      {/* Rationale text if present */}
      {priorityRationale && (
        <p className="text-[11px] text-slate-500 italic border-t border-slate-200/60 pt-2 leading-relaxed">
          &ldquo;{priorityRationale}&rdquo;
        </p>
      )}

      {/* Mandatory Disclaimer */}
      <div className="pt-2 border-t border-slate-200/60 text-[10px] text-slate-500 font-medium flex items-center gap-1">
        <span>⚠️</span>
        <span data-testid="officer-confirm-disclaimer">
          AI can misread photos. An officer confirms.
        </span>
      </div>
    </div>
  );
};

export default ExplainablePriorityCard;

