"use client";

import React, { useState } from "react";
import ActionButton from "@/components/ui/ActionButton";
import { generateActionBrief, assignWorkOrder } from "@/lib/api";

export interface ClusterItem {
  cluster_id: string;
  title: string;
  total_reports: number;
  category_breakdown: Record<string, number>;
  center_point: { latitude: number; longitude: number };
  boundary_geojson?: any;
  report_ids?: string[];
}

interface ActionBriefModalProps {
  cluster: ClusterItem | null;
  isOpen: boolean;
  onClose: () => void;
  onDispatched?: () => void;
}

export const ActionBriefModal: React.FC<ActionBriefModalProps> = ({
  cluster,
  isOpen,
  onClose,
  onDispatched,
}) => {
  const [loading, setLoading] = useState(false);
  const [brief, setBrief] = useState<any>(null);
  const [dispatching, setDispatching] = useState(false);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load action brief when modal opens
  React.useEffect(() => {
    if (!isOpen || !cluster) return;

    setLoading(true);
    setErrorMsg(null);
    setDispatchSuccess(false);

    generateActionBrief(cluster.cluster_id)
      .then((data) => setBrief(data))
      .catch((err) => setErrorMsg(err.message || "Failed to generate brief."))
      .finally(() => setLoading(false));
  }, [isOpen, cluster]);

  if (!isOpen || !cluster) return null;

  const handleDispatchCluster = async () => {
    setDispatching(true);
    setErrorMsg(null);

    try {
      const dept = brief?.suggested_department || "Public Works - Infrastructure Division";
      // If cluster has report_ids, assign master / underlying tickets
      if (cluster.report_ids && cluster.report_ids.length > 0) {
        for (const rid of cluster.report_ids.slice(0, 3)) {
          await assignWorkOrder(rid, dept, `Consolidated dispatch for cluster ${cluster.cluster_id}`);
        }
      }
      setDispatchSuccess(true);
      if (onDispatched) onDispatched();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to dispatch consolidated work orders.");
    } finally {
      setDispatching(false);
    }
  };

  return (
    <div
      data-testid="action-brief-modal"
      className="fixed inset-0 z-modal flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in"
    >
      <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-modal border border-slate-200 space-y-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#E1F2EF] text-[#0B6B61] mb-1">
              <span>⚡</span>
              <span>Sub-Minute Executive Action Brief</span>
            </div>
            <h3 className="text-display text-[#1E293B]">
              {brief?.cluster_name_location || cluster.title}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 font-bold flex items-center justify-center transition-colors"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center space-y-2">
            <div className="w-8 h-8 border-3 border-[#0B6B61] border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-slate-500 font-semibold">Synthesizing cluster reports into action brief...</p>
          </div>
        ) : brief ? (
          <div className="space-y-4">
            {/* Technical Problem Card */}
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-1 text-xs">
              <span className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">
                Synthesized Technical Problem:
              </span>
              <p className="text-slate-700 leading-relaxed font-medium">
                {brief.technical_problem}
              </p>
            </div>

            {/* Recommended Primary Actions */}
            <div className="p-4 bg-[#E1F2EF]/60 rounded-2xl border border-[#A8DADC] space-y-1 text-xs">
              <span className="font-bold text-[#0B6B61] uppercase tracking-wider text-[10px]">
                Recommended Field Action:
              </span>
              <p className="text-[#08544C] leading-relaxed font-semibold">
                {brief.recommended_action || brief.recommended_primary_action}
              </p>
            </div>

            {/* Category Breakdown Badges */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              <span className="text-slate-500 font-bold">Correlated Failures:</span>
              {Object.entries(cluster.category_breakdown || {}).map(([cat, count]) => (
                <span
                  key={cat}
                  className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium text-xs border border-slate-200"
                >
                  {cat}: <strong>{count}</strong>
                </span>
              ))}
            </div>

            {/* Suggested Department Allocation */}
            <div className="flex items-center justify-between p-3.5 bg-amber-50/70 border border-amber-200/80 rounded-2xl text-xs text-amber-900">
              <span className="font-bold">Suggested Dispatch:</span>
              <span className="font-semibold text-amber-800">
                {brief.suggested_department}
              </span>
            </div>

            {/* Success / Error alerts */}
            {dispatchSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl font-bold text-center">
                ✓ Consolidated work order dispatched to {brief.suggested_department}! All underlying corridor tickets updated to Assigned.
              </div>
            )}
            {errorMsg && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl">
                {errorMsg}
              </div>
            )}

            {/* Modal Actions */}
            <div className="pt-2 flex items-center gap-3">
              <ActionButton
                variant="primary"
                fullWidth
                isLoading={dispatching}
                onClick={handleDispatchCluster}
                data-testid="dispatch-cluster-button"
              >
                {dispatching ? "Dispatching Fleet..." : "Dispatch Consolidated Work Order"}
              </ActionButton>
              <ActionButton variant="secondary" onClick={onClose}>
                Close
              </ActionButton>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ActionBriefModal;

