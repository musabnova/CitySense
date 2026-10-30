"use client";

import React from "react";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { ReportItem } from "./IncidentDetailPanel";

interface FixFirstQueueProps {
  reports: ReportItem[];
  selectedReportId?: string;
  onSelectReport: (report: ReportItem) => void;
  className?: string;
}

export const FixFirstQueue: React.FC<FixFirstQueueProps> = ({
  reports,
  selectedReportId,
  onSelectReport,
  className = "",
}) => {
  // Sort reports: Priority 1 first, then 2, 3, 4; then by score descending
  const sortedReports = [...reports].sort((a, b) => {
    const rankWeight: Record<string, number> = {
      "Priority 1": 1,
      "Priority 2": 2,
      "Priority 3": 3,
      "Priority 4": 4,
    };
    const wa = rankWeight[a.priority_rank] || 5;
    const wb = rankWeight[b.priority_rank] || 5;
    if (wa !== wb) return wa - wb;
    return (Number(b.priority_score) || 0) - (Number(a.priority_score) || 0);
  });

  return (
    <div
      data-testid="fix-first-queue"
      className={`flex flex-col h-full bg-white rounded-2xl border border-slate-200/90 shadow-floating overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-white">
        <div>
          <h2 className="text-section font-bold text-[#1E293B] flex items-center gap-2">
            <span>Fix first</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-[#C53030] font-bold">
              {reports.filter((r) => r.priority_rank === "Priority 1").length} Critical
            </span>
          </h2>
          <p className="text-[11px] text-slate-400">Ward 12 Prioritized Intake Queue</p>
        </div>
        <span className="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
          {reports.length} total
        </span>
      </div>

      {/* List items */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 divide-y divide-slate-50">
        {sortedReports.map((report) => {
          const isSelected = selectedReportId === report.id;
          const isP1 = report.priority_rank === "Priority 1";

          return (
            <div
              key={report.id}
              data-testid={`queue-card-${report.id}`}
              onClick={() => onSelectReport(report)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer select-none space-y-2 ${
                isSelected
                  ? "bg-[#E1F2EF]/60 border-[#0B6B61] shadow-subtle ring-1 ring-[#0B6B61]"
                  : "bg-white hover:bg-slate-50/80 border-slate-200/80 shadow-2xs"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  {report.verified_category || report.user_category || "General"}
                </span>
                <PriorityBadge priority={report.priority_rank as any} />
              </div>

              <h4 className="text-sm font-bold text-[#1E293B] line-clamp-2">
                {report.concise_summary || report.raw_description.slice(0, 70)}
              </h4>

              {/* Context Badges: Near School / Duplicates */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[10px]">
                {report.formatted_address && (
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-medium truncate max-w-[150px]">
                    {report.formatted_address}
                  </span>
                )}
                {report.duplicate_count > 1 && (
                  <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 font-bold border border-amber-200">
                    {report.duplicate_count} reports
                  </span>
                )}
                {isP1 && (
                  <span className="px-2 py-0.5 rounded-md bg-red-50 text-red-700 font-bold border border-red-200">
                    Near sensitive POI
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FixFirstQueue;

