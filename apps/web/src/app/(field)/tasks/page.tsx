"use client";

/**
 * TASK-070: Field Lead Simplified Task Queue View
 * ================================================
 * Mobile-friendly task queue for field maintenance leads (e.g. "Carlos").
 * - Displays only work orders assigned to the authenticated Field Lead's department.
 * - Department is extracted from the signed JWT token; query params cannot override it.
 * - Large touch targets optimized for outdoor field use.
 * - Shows: location, routing link, synthesized brief, consolidated report count.
 * - Integrates TASK-071 ResolveJobDrawer for in-situ resolution.
 * - Displays TASK-072 transparency badges: [Demo Data - Mocked SMS Service] / [Simulated ERP Sync]
 */

import React, { useCallback, useEffect, useState } from "react";
import { fetchFieldTasks, FIELD_TOKENS, FIELD_LEAD_DEPARTMENTS } from "@/lib/api";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { StatusBadge } from "@/components/ui/StatusBadge";
import ResolveJobDrawer from "@/components/field/ResolveJobDrawer";

// ─── Types ────────────────────────────────────────────────────────────────────
interface FieldTask {
  id: string;
  tracking_id: string;
  verified_category: string;
  concise_summary: string;
  formatted_address: string;
  latitude: number;
  longitude: number;
  priority_rank: string;
  priority_score: number;
  priority_rationale?: string;
  lifecycle_status: string;
  assigned_department: string;
  dispatch_timestamp?: string;
  duplicate_count: number;
  is_duplicate: boolean;
  media_url?: string | null;
  resolution_notes?: string | null;
  raw_description: string;
}

// ─── Priority colour helpers ──────────────────────────────────────────────────
const PRIORITY_COLORS: Record<string, string> = {
  "Priority 1": "border-l-[#C53030] bg-red-950/20",
  "Priority 2": "border-l-[#B45309] bg-amber-950/20",
  "Priority 3": "border-l-[#0D9488] bg-teal-950/20",
  "Priority 4": "border-l-slate-500 bg-slate-800/40",
};

// ─── Component ────────────────────────────────────────────────────────────────
export default function FieldTasksPage() {
  // Department / token selection (demo: field lead picks their crew)
  const [selectedDept, setSelectedDept] = useState<string>(FIELD_LEAD_DEPARTMENTS[0]);
  const token = FIELD_TOKENS[selectedDept];

  const [tasks, setTasks] = useState<FieldTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deptLabel, setDeptLabel] = useState<string>("");

  // Resolution drawer state
  const [resolvingTask, setResolvingTask] = useState<FieldTask | null>(null);

  // Last dispatch mock integration info
  const [lastMockEvent, setLastMockEvent] = useState<{ sms?: string; erp?: string } | null>(null);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFieldTasks(token);
      setTasks(data.tasks || []);
      setDeptLabel(data.department || selectedDept);
    } catch (err: any) {
      setError(err.message || "Failed to load work orders.");
    } finally {
      setLoading(false);
    }
  }, [token, selectedDept]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleResolved = () => {
    setResolvingTask(null);
    loadTasks(); // Refresh queue so resolved task disappears from active list
  };

  const openMapsNavigation = (lat: number, lon: number, address: string) => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&travelmode=driving`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="min-h-full pb-8" data-testid="field-tasks-page">
      {/* ── Department Selector (demo mode) ── */}
      <div className="px-5 pt-4 pb-3 bg-[#0F172A]/60 border-b border-slate-700/40">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
          Field Lead Identity (Demo)
        </div>
        <select
          data-testid="field-dept-selector"
          value={selectedDept}
          onChange={(e) => {
            setSelectedDept(e.target.value);
            setLastMockEvent(null);
          }}
          className="w-full p-3 rounded-xl bg-slate-700 border border-slate-600 text-white text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#0B6B61]"
        >
          {FIELD_LEAD_DEPARTMENTS.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>

        {/* TASK-072 Transparency Notice Badges */}
        <div className="flex flex-wrap gap-1.5 mt-2.5">
          <span
            data-testid="badge-mocked-sms"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] font-bold"
          >
            🔔 Demo Data - Mocked SMS Service
          </span>
          <span
            data-testid="badge-simulated-erp"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-[10px] font-bold"
          >
            🏗️ Simulated ERP Sync
          </span>
        </div>
      </div>

      {/* ── Queue Header ── */}
      <div className="px-5 py-3 flex items-center justify-between">
        <div>
          <div className="text-white font-bold text-base">
            {loading ? "Loading..." : `${tasks.length} Work Order${tasks.length !== 1 ? "s" : ""}`}
          </div>
          <div className="text-slate-400 text-xs font-medium mt-0.5">
            Dept: <span className="text-[#A8DADC] font-bold">{deptLabel || selectedDept}</span>
          </div>
        </div>
        <button
          onClick={loadTasks}
          className="w-9 h-9 rounded-full bg-slate-700 hover:bg-slate-600 text-slate-300 flex items-center justify-center text-sm transition-colors"
          title="Refresh"
        >
          ↻
        </button>
      </div>

      {/* ── Mock Event Banner (appears after a dispatch) ── */}
      {lastMockEvent && (
        <div className="mx-5 mb-3 p-3 rounded-2xl bg-emerald-900/30 border border-emerald-500/30 space-y-1">
          {lastMockEvent.sms && (
            <p className="text-[10px] text-emerald-400 font-semibold">
              📱 [Demo Data - Mocked SMS Service] {lastMockEvent.sms}
            </p>
          )}
          {lastMockEvent.erp && (
            <p className="text-[10px] text-purple-400 font-semibold">
              🏗️ [Simulated ERP Sync] {lastMockEvent.erp}
            </p>
          )}
        </div>
      )}

      {/* ── Loading State ── */}
      {loading && (
        <div
          data-testid="field-tasks-loading"
          className="flex flex-col items-center justify-center py-20 space-y-4"
        >
          <div className="w-10 h-10 border-3 border-[#0B6B61] border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 text-sm font-medium">Loading work orders...</p>
        </div>
      )}

      {/* ── Error State ── */}
      {!loading && error && (
        <div
          data-testid="field-tasks-error"
          className="mx-5 mt-4 p-5 rounded-2xl bg-red-900/20 border border-red-500/30 text-center space-y-3"
        >
          <div className="text-2xl">⚠️</div>
          <p className="text-red-300 text-sm font-semibold">{error}</p>
          <button
            onClick={loadTasks}
            className="px-5 py-2 rounded-full bg-red-700 hover:bg-red-600 text-white text-sm font-bold transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* ── Empty State ── */}
      {!loading && !error && tasks.length === 0 && (
        <div
          data-testid="field-tasks-empty"
          className="flex flex-col items-center justify-center py-24 space-y-4 text-center px-6"
        >
          <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center text-3xl">
            ✅
          </div>
          <div>
            <h3 className="text-white font-bold text-lg">No active work orders</h3>
            <p className="text-slate-400 text-sm mt-1">
              {selectedDept} has no assigned jobs right now. Check back later.
            </p>
          </div>
        </div>
      )}

      {/* ── Task Cards ── */}
      {!loading && !error && tasks.length > 0 && (
        <div className="px-4 space-y-3">
          {tasks.map((task) => (
            <div
              key={task.id}
              data-testid="field-task-card"
              className={`rounded-2xl border-l-4 bg-[#1E293B] border border-slate-700/60 overflow-hidden ${
                PRIORITY_COLORS[task.priority_rank] || PRIORITY_COLORS["Priority 4"]
              }`}
            >
              {/* Card Header */}
              <div className="p-4 pb-3 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <PriorityBadge priority={task.priority_rank as any} />
                      <StatusBadge status={task.lifecycle_status} />
                    </div>
                    <div className="font-mono text-[11px] text-slate-400 mt-1.5">
                      {task.tracking_id}
                    </div>
                  </div>
                  {task.duplicate_count > 1 && (
                    <div className="flex-shrink-0 px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-bold">
                      {task.duplicate_count} reports
                    </div>
                  )}
                </div>

                {/* Category & Summary */}
                <div>
                  <div className="text-[#A8DADC] text-xs font-bold">
                    {task.verified_category}
                  </div>
                  <p className="text-white text-sm font-medium mt-0.5 leading-snug line-clamp-2">
                    {task.concise_summary || task.raw_description.slice(0, 100)}
                  </p>
                </div>

                {/* Location */}
                <div className="flex items-center gap-1 text-slate-400 text-xs">
                  <span>📍</span>
                  <span className="truncate">{task.formatted_address}</span>
                </div>

                {/* Dispatch timestamp */}
                {task.dispatch_timestamp && (
                  <div className="text-[10px] text-slate-500">
                    Dispatched: {new Date(task.dispatch_timestamp).toLocaleString("en-IN", { dateStyle: "short", timeStyle: "short" })}
                  </div>
                )}

                {/* Priority Rationale */}
                {task.priority_rationale && (
                  <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-[10px] text-slate-300 leading-relaxed">
                    <span className="font-bold text-[#A8DADC]">AI Brief: </span>
                    {task.priority_rationale.slice(0, 120)}
                    {task.priority_rationale.length > 120 ? "…" : ""}
                  </div>
                )}

                {/* Resolution Notes (for resolved tasks) */}
                {task.lifecycle_status === "Resolved" && task.resolution_notes && (
                  <div className="p-2.5 rounded-xl bg-emerald-900/20 border border-emerald-500/30 text-[10px] text-emerald-300">
                    <span className="font-bold">✓ Resolved: </span>
                    {task.resolution_notes}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              {task.lifecycle_status !== "Resolved" && (
                <div className="px-4 pb-4 grid grid-cols-2 gap-2">
                  {/* Navigate Button */}
                  <button
                    type="button"
                    onClick={() => openMapsNavigation(task.latitude, task.longitude, task.formatted_address)}
                    className="py-3.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold transition-colors flex items-center justify-center gap-1.5 min-h-[52px]"
                  >
                    <span>🗺️</span>
                    <span>Navigate</span>
                  </button>

                  {/* Mark Fixed Button */}
                  <button
                    type="button"
                    data-testid={`resolve-btn-${task.tracking_id}`}
                    onClick={() => setResolvingTask(task)}
                    className="py-3.5 rounded-xl bg-emerald-700 hover:bg-emerald-600 active:scale-98 text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 min-h-[52px]"
                  >
                    <span>✓</span>
                    <span>Mark Fixed</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── TASK-071: Resolve Job Drawer ── */}
      {resolvingTask && (
        <ResolveJobDrawer
          reportId={resolvingTask.id}
          trackingId={resolvingTask.tracking_id}
          location={resolvingTask.formatted_address}
          summary={resolvingTask.concise_summary || resolvingTask.raw_description.slice(0, 100)}
          token={token}
          onResolved={handleResolved}
          onCancel={() => setResolvingTask(null)}
        />
      )}
    </div>
  );
}

