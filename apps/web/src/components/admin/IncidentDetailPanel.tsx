"use client";

import React, { useState } from "react";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import ActionButton from "@/components/ui/ActionButton";
import ExplainablePriorityCard from "@/components/admin/ExplainablePriorityCard";
import DuplicateManager from "@/components/admin/DuplicateManager";
import { assignWorkOrder } from "@/lib/api";

export interface ReportItem {
  id: string;
  tracking_id: string;
  raw_description: string;
  user_category?: string;
  verified_category?: string;
  media_url?: string | null;
  latitude: number;
  longitude: number;
  formatted_address?: string;
  concise_summary?: string;
  is_duplicate: boolean;
  master_ticket_id?: string | null;
  duplicate_count: number;
  priority_rank: string;
  priority_score: number;
  priority_rationale?: string;
  lifecycle_status: string;
  assigned_department?: string | null;
  created_at?: string;
}

interface IncidentDetailPanelProps {
  report: ReportItem | null;
  onClose?: () => void;
  onRefresh?: () => void;
  className?: string;
}

const CREW_OPTIONS = [
  "Drainage Crew A",
  "Road Repair Team 2",
  "Electrical Utility Unit",
  "Public Works - Infrastructure Division",
  "Sanitation & Waste Rapid Response",
];

export const IncidentDetailPanel: React.FC<IncidentDetailPanelProps> = ({
  report,
  onClose,
  onRefresh,
  className = "",
}) => {
  const [selectedCrew, setSelectedCrew] = useState(CREW_OPTIONS[0]);
  const [assigning, setAssigning] = useState(false);
  const [assignSuccess, setAssignSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [photoZoom, setPhotoZoom] = useState(false);

  if (!report) {
    return (
      <div className={`p-6 text-center text-slate-400 flex flex-col items-center justify-center h-full space-y-2 ${className}`}>
        <span className="text-3xl">🗺️</span>
        <p className="text-sm font-medium">Select an incident pin or queue item to review detail and dispatch.</p>
      </div>
    );
  }

  const handleAssign = async () => {
    setAssigning(true);
    setErrorMsg(null);
    setAssignSuccess(false);

    try {
      await assignWorkOrder(report.id, selectedCrew, `Dispatched to ${selectedCrew} from Command Console`);
      setAssignSuccess(true);
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to dispatch work order.");
    } finally {
      setAssigning(false);
    }
  };

  return (
    <div
      data-testid="incident-detail-panel"
      className={`flex flex-col h-full overflow-y-auto p-5 space-y-4 bg-white ${className}`}
    >
      {/* Panel Top Header */}
      <div className="flex items-start justify-between border-b border-slate-100 pb-3">
        <div>
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Incident Detail
          </div>
          <div className="text-lg font-mono font-bold text-[#0B6B61]">
            {report.tracking_id}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={report.lifecycle_status} />
          {onClose && (
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center text-xs font-bold transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Title & Core Summary */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500">
            {report.verified_category || report.user_category || "General"}
          </span>
          <PriorityBadge priority={report.priority_rank as any} />
        </div>
        <h3 className="text-section font-bold text-[#1E293B]">
          {report.concise_summary || report.raw_description.slice(0, 80)}
        </h3>
        {report.formatted_address && (
          <p className="text-xs text-slate-500 flex items-center gap-1 pt-0.5">
            <span>📍</span>
            <span>{report.formatted_address}</span>
          </p>
        )}
      </div>

      {/* Citizen Photo Thumbnail with Zoom Trigger */}
      {report.media_url ? (
        <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-50 group">
          <img
            src={report.media_url}
            alt="Citizen evidence photo"
            className="w-full h-40 object-cover cursor-pointer group-hover:scale-102 transition-transform duration-200"
            onClick={() => setPhotoZoom(true)}
          />
          <button
            type="button"
            onClick={() => setPhotoZoom(true)}
            className="absolute bottom-2 right-2 bg-black/60 hover:bg-black/80 text-white text-[11px] px-2.5 py-1 rounded-full backdrop-blur-xs font-medium flex items-center gap-1"
          >
            <span>🔍</span>
            <span>Zoom</span>
          </button>
        </div>
      ) : (
        <div className="h-24 rounded-2xl border border-dashed border-slate-200 bg-slate-50 flex items-center justify-center text-xs text-slate-400">
          No photo evidence attached
        </div>
      )}

      {/* Photo Zoom Modal */}
      {photoZoom && report.media_url && (
        <div
          className="fixed inset-0 z-modal flex items-center justify-center bg-black/80 backdrop-blur-xs p-4"
          onClick={() => setPhotoZoom(false)}
        >
          <div className="relative max-w-2xl w-full bg-black rounded-3xl overflow-hidden border border-slate-700">
            <img src={report.media_url} alt="Enlarged photo" className="w-full max-h-[75vh] object-contain" />
            <button
              onClick={() => setPhotoZoom(false)}
              className="absolute top-4 right-4 bg-white/20 hover:bg-white/40 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Raw Description Body */}
      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs text-slate-700 space-y-1">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Citizen Description:
        </div>
        <p className="leading-relaxed">&ldquo;{report.raw_description}&rdquo;</p>
      </div>

      {/* Explainable Priority Breakdown */}
      <ExplainablePriorityCard
        priorityRank={report.priority_rank}
        priorityScore={Number(report.priority_score) || 75}
        priorityRationale={report.priority_rationale}
      />

      {/* Duplicate Correlation & Unlink Controls */}
      <DuplicateManager
        reportId={report.id}
        trackingId={report.tracking_id}
        isDuplicate={report.is_duplicate}
        masterTicketId={report.master_ticket_id}
        duplicateCount={report.duplicate_count}
        onRefresh={onRefresh}
      />

      {/* Departmental Work Order Dispatch Form */}
      <div className="p-4 bg-[#E1F2EF]/40 border border-[#A8DADC] rounded-2xl space-y-3 pt-3">
        <label className="block text-xs font-bold text-[#0B6B61] uppercase tracking-wider">
          Work Order Dispatch Allocation:
        </label>
        <select
          data-testid="crew-dropdown"
          value={selectedCrew}
          onChange={(e) => setSelectedCrew(e.target.value)}
          className="w-full p-2.5 text-xs font-medium text-slate-800 bg-white border border-[#A8DADC] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#0B6B61]"
        >
          {CREW_OPTIONS.map((crew) => (
            <option key={crew} value={crew}>
              {crew}
            </option>
          ))}
        </select>

        <ActionButton
          variant="primary"
          fullWidth
          isLoading={assigning}
          onClick={handleAssign}
          data-testid="assign-work-order-button"
        >
          {assigning ? "Dispatching..." : "Assign Work Order"}
        </ActionButton>

        {assignSuccess && (
          <p className="text-xs text-emerald-700 font-bold bg-emerald-50 p-2 rounded-xl border border-emerald-200 text-center">
            ✓ Work order assigned to {selectedCrew}!
          </p>
        )}
        {errorMsg && (
          <p className="text-xs text-red-700 font-medium bg-red-50 p-2 rounded-xl border border-red-200">
            {errorMsg}
          </p>
        )}
      </div>
    </div>
  );
};

export default IncidentDetailPanel;

