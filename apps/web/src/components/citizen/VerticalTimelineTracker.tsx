"use client";

import React from "react";
import { ReportLifecycleStatus } from "@/components/ui/StatusBadge";

export interface TimelineStep {
  status: ReportLifecycleStatus;
  label: string;
  description: string;
  timestamp?: string | null;
}

const DEFAULT_STEPS: TimelineStep[] = [
  {
    status: "Submitted",
    label: "Report Submitted",
    description: "Citizen report logged and queued for AI classification.",
  },
  {
    status: "Under Review",
    label: "Under Review",
    description: "Multi-factor priority calculated and duplicate checks performed.",
  },
  {
    status: "Assigned",
    label: "Dispatched to Department",
    description: "Work order assigned to municipal field crew.",
  },
  {
    status: "Resolved",
    label: "Resolved & Inspected",
    description: "Remediation verified by ward supervisor.",
  },
];

interface VerticalTimelineTrackerProps {
  currentStatus: string;
  createdAt?: string | null;
  assignedDepartment?: string | null;
  resolutionNotes?: string | null;
  className?: string;
}

export const VerticalTimelineTracker: React.FC<VerticalTimelineTrackerProps> = ({
  currentStatus,
  createdAt,
  assignedDepartment,
  resolutionNotes,
  className = "",
}) => {
  const normStatus = currentStatus.toLowerCase();

  const getStepState = (stepIndex: number): "completed" | "active" | "upcoming" => {
    let currentIndex = 0;
    if (normStatus === "under review" || normStatus === "under_review") currentIndex = 1;
    else if (normStatus === "assigned") currentIndex = 2;
    else if (normStatus === "resolved") currentIndex = 3;

    if (stepIndex < currentIndex) return "completed";
    if (stepIndex === currentIndex) return "active";
    return "upcoming";
  };

  const getStepTimestamp = (index: number) => {
    if (index === 0 && createdAt) {
      try {
        return new Date(createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      } catch (_) {
        return createdAt;
      }
    }
    return null;
  };

  return (
    <div data-testid="vertical-timeline-tracker" className={`space-y-6 ${className}`}>
      {DEFAULT_STEPS.map((step, index) => {
        const state = getStepState(index);
        const isLast = index === DEFAULT_STEPS.length - 1;
        const timeStr = getStepTimestamp(index);

        return (
          <div key={step.status} className="relative flex items-start gap-3.5 group">
            {/* Vertical Connecting Line */}
            {!isLast && (
              <div
                className="absolute left-[11px] top-6 bottom-[-16px] w-[2px] transition-colors"
                style={{
                  backgroundColor: state === "completed" ? "#0B6B61" : "#E2E8F0",
                }}
              />
            )}

            {/* Circular Timeline Node */}
            <div className="relative z-10 flex-shrink-0 mt-0.5">
              {state === "completed" && (
                <div
                  data-testid="timeline-node-completed"
                  className="w-6 h-6 rounded-full bg-[#0B6B61] flex items-center justify-center text-white text-[11px] shadow-subtle"
                >
                  ✓
                </div>
              )}
              {state === "active" && (
                <div
                  data-testid="timeline-node-active"
                  className="w-6 h-6 rounded-full bg-white border-2 border-[#0B6B61] flex items-center justify-center shadow-subtle"
                >
                  <div className="w-2 h-2 rounded-full bg-[#0B6B61] animate-ping" />
                </div>
              )}
              {state === "upcoming" && (
                <div
                  data-testid="timeline-node-upcoming"
                  className="w-6 h-6 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                </div>
              )}
            </div>

            {/* Step Content */}
            <div className="flex-1 space-y-0.5 pb-2">
              <div className="flex items-center justify-between">
                <span
                  className={`text-sm font-bold ${
                    state === "upcoming" ? "text-slate-400" : "text-[#1E293B]"
                  }`}
                >
                  {step.label}
                </span>
                {timeStr && (
                  <span className="text-[11px] text-slate-500 font-medium">
                    {timeStr}
                  </span>
                )}
              </div>

              <p
                className={`text-xs ${
                  state === "upcoming" ? "text-slate-400" : "text-[#64748B]"
                }`}
              >
                {index === 2 && assignedDepartment
                  ? `Assigned to ${assignedDepartment}.`
                  : index === 3 && resolutionNotes
                  ? `Resolution notes: ${resolutionNotes}`
                  : step.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default VerticalTimelineTracker;

