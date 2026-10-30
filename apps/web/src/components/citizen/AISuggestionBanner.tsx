"use client";

import React, { useState } from "react";

interface AISuggestionBannerProps {
  detectedCategory?: string;
  detectedPriority?: string;
  similarReportsCount?: number;
  explanation?: string;
  className?: string;
}

export const AISuggestionBanner: React.FC<AISuggestionBannerProps> = ({
  detectedCategory = "Drainage",
  detectedPriority = "High",
  similarReportsCount = 2,
  explanation = "High priority due to standing flood water proximity to pedestrian school gate (+40 pts) and 2 nearby correlated citizen reports.",
  className = "",
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      data-testid="ai-suggestion-banner"
      className={`rounded-xl p-3.5 border transition-all ${className}`}
      style={{
        backgroundColor: "#E1F2EF",
        borderColor: "#A8DADC",
      }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#0B6B61]">
            <svg
              className="w-3.5 h-3.5 text-[#0B6B61]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
            <span>
              AI Suggestion: {detectedCategory} ({detectedPriority})
            </span>
          </div>

          <p className="text-xs text-[#08544C]">
            {similarReportsCount} similar reports nearby.{" "}
            <button
              type="button"
              onClick={() => setShowTooltip(!showTooltip)}
              data-testid="ai-why-trigger"
              className="font-bold underline cursor-pointer hover:text-[#0B6B61] focus:outline-none"
            >
              [Why?]
            </button>
          </p>
        </div>
      </div>

      {/* Plain-Language Explainability Dropdown */}
      {showTooltip && (
        <div
          data-testid="ai-explanation-box"
          className="mt-2.5 p-2.5 bg-white/90 rounded-lg text-xs text-slate-700 border border-[#A8DADC] shadow-subtle animate-in fade-in duration-150"
        >
          <div className="font-bold text-[#0B6B61] mb-1">Explainable AI Scoring:</div>
          <div>{explanation}</div>
        </div>
      )}

      {/* Mandatory PRD Disclaimer */}
      <div className="mt-2 pt-1.5 border-t border-[#A8DADC]/60 flex items-center justify-between text-[11px] text-[#08544C]/80">
        <span data-testid="ai-disclaimer">
          Demo data. AI suggestions can be wrong.
        </span>
      </div>
    </div>
  );
};

export default AISuggestionBanner;

