"use client";

import React, { useState } from "react";
import { overrideReport } from "@/lib/api";

interface DuplicateManagerProps {
  reportId: string;
  trackingId: string;
  isDuplicate?: boolean;
  masterTicketId?: string | null;
  duplicateCount?: number;
  onRefresh?: () => void;
  className?: string;
}

export const DuplicateManager: React.FC<DuplicateManagerProps> = ({
  reportId,
  trackingId,
  isDuplicate = false,
  masterTicketId = null,
  duplicateCount = 1,
  onRefresh,
  className = "",
}) => {
  const [unlinking, setUnlinking] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const [reason, setReason] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleUnlink = async () => {
    if (!reason.trim() || reason.trim().length < 5) {
      setErrorMsg("Please provide at least 5 characters for justification.");
      return;
    }

    setUnlinking(true);
    setErrorMsg(null);

    try {
      await overrideReport(reportId, "UNLINK_DUPLICATE", reason.trim());
      setSuccessMsg("Report unlinked successfully.");
      setShowPrompt(false);
      setReason("");
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to unlink duplicate report.");
    } finally {
      setUnlinking(false);
    }
  };

  const hasDuplicates = isDuplicate || (duplicateCount && duplicateCount > 1) || masterTicketId;

  return (
    <div
      data-testid="duplicate-manager"
      className={`rounded-2xl p-4 bg-white border border-slate-200/90 shadow-subtle space-y-3 ${className}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
          <span>👥</span>
          <span>Duplicate Correlation</span>
        </span>
        {hasDuplicates ? (
          <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
            {isDuplicate ? "Child Duplicate" : `${duplicateCount} Linked Tickets`}
          </span>
        ) : (
          <span className="text-xs text-slate-400 bg-slate-50 px-2 py-0.5 rounded-full">
            Unique Issue
          </span>
        )}
      </div>

      {/* Duplicate Summary Info */}
      <div className="text-xs text-slate-600 leading-relaxed">
        {isDuplicate ? (
          <p>
            Linked with Master Ticket{" "}
            <span className="font-mono font-bold text-[#0B6B61]">
              #{masterTicketId ? masterTicketId.slice(0, 8) : "1038"}
            </span>{" "}
            (82% semantic match, 35m spatial radius).
          </p>
        ) : duplicateCount > 1 ? (
          <p>
            Master ticket with {duplicateCount - 1} linked duplicates. Aggregated priority impact score (+{Math.min(30, (duplicateCount - 1) * 10)} pts).
          </p>
        ) : (
          <p className="text-slate-400">
            No active spatial or semantic duplicates detected within 50m.
          </p>
        )}
      </div>

      {/* Unlink Action Trigger */}
      {isDuplicate && !showPrompt && (
        <div className="pt-1 flex items-center justify-between">
          <button
            type="button"
            data-testid="unlink-button"
            onClick={() => setShowPrompt(true)}
            className="text-xs font-bold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-3 py-1.5 rounded-full transition-colors cursor-pointer select-none"
          >
            Not the same (Unlink)
          </button>
        </div>
      )}

      {/* Override Justification Dialog */}
      {showPrompt && (
        <div className="pt-2 border-t border-slate-100 space-y-2 animate-in fade-in">
          <label className="block text-[11px] font-bold text-slate-600">
            Officer Justification for Decoupling:
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g. Distinct failure point on opposite sidewalk..."
            className="w-full p-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#0B6B61]"
          />
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={unlinking}
              onClick={handleUnlink}
              className="px-3 py-1 bg-[#0B6B61] text-white text-xs font-bold rounded-lg hover:bg-[#08544C] disabled:opacity-50"
            >
              {unlinking ? "Unlinking..." : "Confirm Unlink"}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowPrompt(false);
                setErrorMsg(null);
              }}
              className="px-3 py-1 text-slate-500 text-xs font-medium hover:text-slate-800"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {errorMsg && (
        <p className="text-[11px] text-red-600 bg-red-50 p-1.5 rounded-lg border border-red-200">
          {errorMsg}
        </p>
      )}

      {successMsg && (
        <p className="text-[11px] text-emerald-700 bg-emerald-50 p-1.5 rounded-lg border border-emerald-200">
          {successMsg}
        </p>
      )}
    </div>
  );
};

export default DuplicateManager;

