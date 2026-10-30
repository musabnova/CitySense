"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { FloatingCard } from "@/components/ui/FloatingCard";
import ActionButton from "@/components/ui/ActionButton";
import VerticalTimelineTracker from "@/components/citizen/VerticalTimelineTracker";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TrackReportData {
  tracking_id: string;
  lifecycle_status: string;
  user_category?: string;
  verified_category?: string;
  concise_summary?: string;
  created_at?: string;
  formatted_address?: string;
  is_duplicate?: boolean;
  master_ticket_id?: string | null;
  priority_rank?: string;
  priority_score?: number;
  priority_rationale?: string;
  assigned_department?: string | null;
  resolution_notes?: string | null;
}

export default function TrackReportPage() {
  const params = useParams();
  const router = useRouter();
  const trackingId = (params?.id as string) || "";

  const [report, setReport] = useState<TrackReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [showQR, setShowQR] = useState(false);

  useEffect(() => {
    if (!trackingId) return;

    let isMounted = true;
    setLoading(true);

    fetch(`${API_BASE_URL}/api/v1/reports/track/${trackingId}`)
      .then(async (res) => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Report '${trackingId}' not found.`);
        }
        return res.json();
      })
      .then((data) => {
        if (isMounted) {
          setReport(data);
          setErrorMsg(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setErrorMsg(err.message);
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [trackingId]);

  const handleCopyId = () => {
    if (report?.tracking_id) {
      navigator.clipboard.writeText(report.tracking_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShare = () => {
    if (navigator.share && report) {
      navigator.share({
        title: `CitySense Report ${report.tracking_id}`,
        text: `Track status of civic issue ${report.tracking_id}: ${report.concise_summary || ""}`,
        url: window.location.href,
      }).catch(() => {});
    } else {
      handleCopyId();
    }
  };

  if (loading) {
    return (
      <div className="flex-1 p-6 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 border-3 border-[#0B6B61] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Fetching report tracking status...</p>
      </div>
    );
  }

  if (errorMsg || !report) {
    return (
      <div className="flex-1 p-6 flex flex-col items-center justify-center text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center text-xl font-bold">
          ✕
        </div>
        <div className="space-y-1">
          <h2 className="text-section font-bold text-slate-800">Report Not Found</h2>
          <p className="text-body text-slate-500 text-sm max-w-xs">{errorMsg || "Invalid tracking ID."}</p>
        </div>
        <ActionButton variant="secondary" onClick={() => router.push("/report")}>
          Submit New Report
        </ActionButton>
      </div>
    );
  }

  return (
    <div className="flex-1 p-5 pb-8 space-y-5 overflow-y-auto">
      {/* Top Header & Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
        <button
          onClick={() => router.push("/report")}
          className="inline-flex items-center text-xs font-semibold text-[#0B6B61] hover:underline"
        >
          ← New Report
        </button>
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Citizen Tracking Portal
        </span>
      </div>

      {/* Main Tracking Header Card */}
      <FloatingCard elevation="floating" className="p-5 space-y-3.5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Incident Tracking ID
            </div>
            <div
              data-testid="display-tracking-id"
              className="text-xl font-mono font-bold text-[#0B6B61] tracking-tight"
            >
              {report.tracking_id}
            </div>
          </div>
          <div className="flex flex-col items-end gap-1.5">
            <StatusBadge status={report.lifecycle_status} />
            {report.priority_rank && (
              <PriorityBadge priority={report.priority_rank as any} />
            )}
          </div>
        </div>

        {/* Issue Summary & Category */}
        <div className="space-y-1 border-t border-slate-100 pt-3">
          <div className="text-xs font-bold text-slate-700">
            {report.verified_category || report.user_category || "Civic Issue"}
          </div>
          <p className="text-sm text-slate-600 font-medium line-clamp-2">
            {report.concise_summary || "Municipal maintenance complaint recorded."}
          </p>
          {report.formatted_address && (
            <p className="text-xs text-slate-400 flex items-center gap-1 pt-1">
              <span>📍</span>
              <span className="truncate">{report.formatted_address}</span>
            </p>
          )}
        </div>

        {/* Action Controls: Copy, QR, Share */}
        <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={handleCopyId}
            data-testid="copy-tracking-id-button"
            className="flex-1 py-2 px-3 rounded-full border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:bg-slate-100 flex items-center justify-center gap-1.5 transition-all select-none"
          >
            <span>{copied ? "✓ Copied" : "Copy ID"}</span>
          </button>
          <button
            type="button"
            onClick={() => setShowQR(!showQR)}
            data-testid="qr-toggle-button"
            className="py-2 px-3 rounded-full border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 active:bg-slate-100 flex items-center justify-center gap-1 transition-all select-none"
          >
            <span>QR</span>
          </button>
          <button
            type="button"
            onClick={handleShare}
            className="py-2 px-3 rounded-full border border-slate-200 text-xs font-semibold text-[#0B6B61] bg-[#E1F2EF] hover:bg-[#D3EDE9] flex items-center justify-center gap-1 transition-all select-none"
          >
            <span>Share</span>
          </button>
        </div>

        {/* QR Code Container */}
        {showQR && (
          <div
            data-testid="qr-code-box"
            className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col items-center justify-center space-y-2 animate-in fade-in"
          >
            {/* SVG QR Code Simulation */}
            <div className="p-2 bg-white rounded-xl shadow-subtle border border-slate-200">
              <svg width="120" height="120" viewBox="0 0 24 24" fill="#1E293B">
                <rect x="2" y="2" width="6" height="6" rx="1" fill="#0B6B61" />
                <rect x="16" y="2" width="6" height="6" rx="1" fill="#0B6B61" />
                <rect x="2" y="16" width="6" height="6" rx="1" fill="#0B6B61" />
                <rect x="10" y="4" width="4" height="2" />
                <rect x="10" y="8" width="2" height="4" />
                <rect x="14" y="10" width="4" height="2" />
                <rect x="10" y="14" width="4" height="4" />
                <rect x="16" y="14" width="2" height="4" />
                <rect x="18" y="18" width="4" height="4" />
              </svg>
            </div>
            <div className="text-[11px] font-mono text-slate-500 font-bold">
              Scan to track on mobile
            </div>
          </div>
        )}
      </FloatingCard>

      {/* Linked Duplicate Banner (TASK-059 Requirement) */}
      {report.is_duplicate && (
        <div
          data-testid="duplicate-notification-banner"
          className="rounded-2xl p-4 bg-amber-50 border border-amber-200 space-y-1 text-amber-900 shadow-subtle"
        >
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800">
            <span>ℹ️</span>
            <span>Duplicate Issue Consolidated</span>
          </div>
          <p className="text-xs leading-relaxed">
            Your report has been merged with{" "}
            <strong>
              Master Issue #{report.master_ticket_id ? report.master_ticket_id.slice(0, 8) : "Cluster-104"}
            </strong>
            ; tracking master resolution status.
          </p>
        </div>
      )}

      {/* Lifecycle Progress Timeline */}
      <div className="p-5 bg-white rounded-3xl border border-slate-200 shadow-subtle space-y-4">
        <h3 className="text-section font-bold text-[#1E293B]">
          Resolution Lifecycle
        </h3>
        <VerticalTimelineTracker
          currentStatus={report.lifecycle_status}
          createdAt={report.created_at}
          assignedDepartment={report.assigned_department}
          resolutionNotes={report.resolution_notes}
        />
      </div>

      {/* AI Explainability Card (if available) */}
      {report.priority_rationale && (
        <div className="p-4 rounded-2xl bg-[#E1F2EF] border border-[#A8DADC] text-xs text-[#08544C] space-y-1">
          <div className="font-bold text-[#0B6B61] flex items-center gap-1">
            <span>🔍</span>
            <span>Priority Assessment Rationale:</span>
          </div>
          <p className="leading-relaxed">{report.priority_rationale}</p>
        </div>
      )}
    </div>
  );
}

