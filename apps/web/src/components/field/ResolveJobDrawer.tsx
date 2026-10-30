"use client";

/**
 * TASK-071: Field Job Resolution & Photo Evidence Logging Component
 * ==================================================================
 * Allows field workers to:
 *   1. Upload a completion/repair evidence photo
 *   2. Enter resolution notes (required)
 *   3. Click "Mark Fixed" to update status to Resolved in PostgreSQL
 * On success, the parent refreshes the task queue and citizen tracking reflects "Resolved".
 */

import React, { useRef, useState } from "react";
import { resolveFieldJob } from "@/lib/api";

export interface ResolveJobDrawerProps {
  /** The report UUID or tracking_id */
  reportId: string;
  trackingId: string;
  /** The address/location of the work order */
  location?: string;
  /** Summary of the issue */
  summary?: string;
  /** JWT auth token for Field Lead role */
  token: string;
  /** Called after successful resolution to refresh the task queue */
  onResolved?: () => void;
  /** Called to dismiss the drawer without action */
  onCancel?: () => void;
}

export default function ResolveJobDrawer({
  reportId,
  trackingId,
  location,
  summary,
  token,
  onResolved,
  onCancel,
}: ResolveJobDrawerProps) {
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [evidencePhotoFile, setEvidencePhotoFile] = useState<File | null>(null);
  const [evidencePhotoPreview, setEvidencePhotoPreview] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setEvidencePhotoFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setEvidencePhotoPreview(reader.result as string);
      reader.readAsDataURL(file);
    } else {
      setEvidencePhotoPreview(null);
    }
  };

  const handleMarkFixed = async () => {
    setError(null);

    if (!resolutionNotes.trim()) {
      setError("Resolution notes are required before marking as fixed.");
      return;
    }

    setSubmitting(true);

    // In this architecture evidence photos are stored as data-URLs (no file storage backend).
    // A real implementation would upload to S3/GCS and store the URL.
    const evidencePhotoUrl = evidencePhotoPreview || "";

    try {
      await resolveFieldJob(reportId, resolutionNotes.trim(), evidencePhotoUrl, token);
      setSuccess(true);
      // Refresh parent queue after a short delay so UI feedback is visible
      setTimeout(() => {
        onResolved?.();
      }, 1200);
    } catch (err: any) {
      setError(err.message || "Failed to mark job as fixed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div
        data-testid="resolve-success-state"
        className="fixed inset-0 z-50 flex items-end justify-center pointer-events-none"
      >
        <div className="w-full max-w-md pointer-events-auto bg-[#1E293B] rounded-t-3xl p-6 pb-10 shadow-2xl border-t border-emerald-500/30">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center text-3xl">
              ✅
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">Job Marked as Fixed!</h3>
              <p className="text-slate-400 text-sm mt-1">
                Ticket <span className="font-mono text-emerald-400">{trackingId}</span> is now{" "}
                <span className="font-bold text-emerald-400">Resolved</span>.
              </p>
              <p className="text-slate-500 text-xs mt-2">
                The citizen tracking page will reflect this update immediately.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    // Bottom drawer panel, fixed to viewport bottom
    <div
      data-testid="resolve-job-drawer"
      className="fixed inset-0 z-50 flex items-end justify-center"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Drawer Panel */}
      <div className="relative w-full max-w-md bg-[#1E293B] rounded-t-3xl shadow-2xl border-t border-slate-600/60 pb-10">
        {/* Grab Handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-10 h-1 rounded-full bg-slate-600" />
        </div>

        {/* Header */}
        <div className="px-5 pb-4 border-b border-slate-700/60">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Resolution Report
              </div>
              <div className="text-white font-mono font-bold text-base mt-0.5">
                {trackingId}
              </div>
            </div>
            <button
              onClick={onCancel}
              className="w-8 h-8 rounded-full bg-slate-700 hover:bg-slate-600 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold transition-colors"
            >
              ✕
            </button>
          </div>
          {location && (
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
              <span>📍</span>
              <span className="truncate">{location}</span>
            </p>
          )}
          {summary && (
            <p className="text-xs text-slate-300 mt-1 line-clamp-2">{summary}</p>
          )}
        </div>

        {/* Form Body */}
        <div className="px-5 pt-4 space-y-4">
          {/* Evidence Photo Upload */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
              Completion Evidence Photo
              <span className="ml-1 text-slate-500 font-normal normal-case">(optional but recommended)</span>
            </label>

            {evidencePhotoPreview ? (
              <div className="relative rounded-2xl overflow-hidden border border-slate-600 bg-slate-800">
                <img
                  src={evidencePhotoPreview}
                  alt="Evidence preview"
                  className="w-full h-44 object-cover"
                />
                <button
                  type="button"
                  onClick={() => {
                    setEvidencePhotoFile(null);
                    setEvidencePhotoPreview(null);
                    if (fileInputRef.current) fileInputRef.current.value = "";
                  }}
                  className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/60 text-white text-xs font-bold flex items-center justify-center"
                >
                  ✕
                </button>
                <div className="absolute bottom-2 left-2 bg-emerald-500/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                  ✓ Photo Attached
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full h-32 rounded-2xl border-2 border-dashed border-slate-600 hover:border-[#0B6B61] bg-slate-800/60 flex flex-col items-center justify-center gap-2 text-slate-400 hover:text-[#A8DADC] transition-all active:scale-98"
              >
                <span className="text-2xl">📸</span>
                <span className="text-xs font-semibold">Tap to upload completion photo</span>
              </button>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handlePhotoChange}
              className="hidden"
              data-testid="evidence-photo-input"
            />
          </div>

          {/* Resolution Notes */}
          <div className="space-y-2">
            <label
              htmlFor="resolution-notes"
              className="block text-xs font-bold text-slate-300 uppercase tracking-wider"
            >
              Resolution Notes <span className="text-red-400">*</span>
            </label>
            <textarea
              id="resolution-notes"
              data-testid="resolution-notes-textarea"
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              placeholder="Describe what was done to fix the issue (e.g. 'Cleared blocked drain channel, installed debris filter screen...')"
              rows={4}
              className="w-full p-3.5 rounded-2xl bg-slate-800 border border-slate-600 focus:border-[#0B6B61] focus:ring-2 focus:ring-[#0B6B61]/30 text-white text-sm placeholder-slate-500 focus:outline-none resize-none leading-relaxed"
              maxLength={1000}
            />
            <div className="text-right text-[10px] text-slate-500">
              {resolutionNotes.length}/1000
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div
              data-testid="resolve-error-banner"
              className="p-3 rounded-2xl bg-red-900/30 border border-red-500/40 text-red-300 text-xs font-medium"
            >
              ⚠️ {error}
            </div>
          )}

          {/* Mark Fixed CTA */}
          <button
            type="button"
            data-testid="mark-fixed-button"
            onClick={handleMarkFixed}
            disabled={submitting || !resolutionNotes.trim()}
            className="w-full py-4 rounded-2xl font-bold text-base text-white transition-all select-none
              bg-emerald-600 hover:bg-emerald-500 active:scale-98
              disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
              flex items-center justify-center gap-2 shadow-lg"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Marking as Fixed...</span>
              </>
            ) : (
              <>
                <span>✓</span>
                <span>Mark Fixed</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

