"use client";

import React, { useState } from "react";

interface SystemicInsightCalloutProps {
  className?: string;
}

export const SystemicInsightCallout: React.FC<SystemicInsightCalloutProps> = ({
  className = "",
}) => {
  const [minimized, setMinimized] = useState(false);

  return (
    <div
      data-testid="systemic-insight-callout"
      className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-floating transition-all duration-200 max-w-xl w-[92%] sm:w-auto ${className}`}
    >
      <div className="bg-white shadow-floating rounded-xl p-3.5 sm:p-4 border border-slate-200 flex items-start gap-3 backdrop-blur-md">
        <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0 text-sm font-bold">
          💡
        </div>

        <div className="flex-1 space-y-0.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-[#0B6B61] uppercase tracking-wider">
              Systemic Infrastructure Insight
            </span>
            <button
              type="button"
              onClick={() => setMinimized(!minimized)}
              className="text-slate-400 hover:text-slate-600 text-xs font-bold p-1"
            >
              {minimized ? "Expand" : "✕"}
            </button>
          </div>

          {!minimized && (
            <p className="text-xs text-slate-700 font-medium leading-relaxed">
              <strong>Insight:</strong> Waste bin at Market Gate was reported 5 times in 9 days. Consider a bigger bin or a daily pickup.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemicInsightCallout;

