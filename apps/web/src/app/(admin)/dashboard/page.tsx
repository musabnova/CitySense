"use client";

import React, { useEffect, useState } from "react";
import CommandMapCanvas from "@/components/admin/CommandMapCanvas";
import FixFirstQueue from "@/components/admin/FixFirstQueue";
import IncidentDetailPanel, { ReportItem } from "@/components/admin/IncidentDetailPanel";
import ActionBriefModal, { ClusterItem } from "@/components/admin/ActionBriefModal";
import SystemicInsightCallout from "@/components/admin/SystemicInsightCallout";
import { fetchAllReports, fetchSpatialHotspots } from "@/lib/api";

export default function AdminDashboardPage() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [hotspots, setHotspots] = useState<ClusterItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States: 'all', 'high', 'hotspots'
  const [activeFilter, setActiveFilter] = useState<"all" | "high" | "hotspots">("all");
  const [selectedWard, setSelectedWard] = useState("Ward 12");

  // Selection States
  const [selectedReport, setSelectedReport] = useState<ReportItem | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<ClusterItem | null>(null);
  const [actionBriefOpen, setActionBriefOpen] = useState(false);

  // Load Reports & Hotspots from API
  const loadData = async () => {
    try {
      setLoading(true);
      const [reportsData, hotspotsData] = await Promise.all([
        fetchAllReports(),
        fetchSpatialHotspots().catch(() => []),
      ]);
      setReports(reportsData);
      setHotspots(hotspotsData);
      // Auto-select first report if none selected
      if (!selectedReport && reportsData.length > 0) {
        setSelectedReport(reportsData[0]);
      }
    } catch (err) {
      console.warn("Failed to load command center data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter Reports based on active pill
  const filteredReports = reports.filter((r) => {
    if (activeFilter === "high") {
      return r.priority_rank === "Priority 1";
    }
    if (activeFilter === "hotspots") {
      // Show reports that are part of hotspot corridor or have duplicates
      return (
        r.duplicate_count > 1 ||
        r.is_duplicate ||
        (r.tracking_id && r.tracking_id.includes("HOT"))
      );
    }
    return true; // 'all'
  });

  const handleSelectCluster = (cluster: ClusterItem) => {
    setSelectedCluster(cluster);
    setActionBriefOpen(true);
  };

  return (
    <div className="relative w-full h-full flex flex-col overflow-hidden">
      {/* ── 1. Floating Translucent Navigation Header (z-floating) ── */}
      <header
        data-testid="command-header"
        className="absolute top-4 left-6 right-6 z-floating bg-white/90 backdrop-blur-md rounded-2xl shadow-floating border border-slate-200/80 px-6 py-3 flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-[#0B6B61] text-white flex items-center justify-center font-bold text-sm shadow-subtle">
              CS
            </div>
            <div>
              <h1 className="text-sm font-bold text-[#1E293B] leading-none">
                CitySense Command Center
              </h1>
              <p className="text-[10px] text-slate-400 font-medium">
                From Complaints to Action · GIS Triage Console
              </p>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-200 hidden md:block" />

          {/* Ward Selector Dropdown */}
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-100/80 px-3 py-1.5 rounded-full border border-slate-200">
            <span className="text-slate-400">Jurisdiction:</span>
            <select
              data-testid="ward-selector"
              value={selectedWard}
              onChange={(e) => setSelectedWard(e.target.value)}
              className="bg-transparent font-bold text-[#0B6B61] focus:outline-none cursor-pointer"
            >
              <option value="Ward 12">Ward 12 (Central District)</option>
              <option value="Ward 11">Ward 11 (North Zone)</option>
              <option value="Ward 10">Ward 10 (East Zone)</option>
            </select>
          </div>
        </div>

        {/* Segmented Filter Pills */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            data-testid="filter-pill-all"
            onClick={() => setActiveFilter("all")}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all select-none cursor-pointer ${
              activeFilter === "all"
                ? "bg-[#0B6B61] text-white shadow-subtle"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            All open · {reports.length}
          </button>
          <button
            type="button"
            data-testid="filter-pill-high"
            onClick={() => setActiveFilter("high")}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all select-none cursor-pointer ${
              activeFilter === "high"
                ? "bg-[#C53030] text-white shadow-subtle"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            High · {reports.filter((r) => r.priority_rank === "Priority 1").length}
          </button>
          <button
            type="button"
            data-testid="filter-pill-hotspots"
            onClick={() => setActiveFilter("hotspots")}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all select-none cursor-pointer ${
              activeFilter === "hotspots"
                ? "bg-amber-600 text-white shadow-subtle"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            Hotspots · {hotspots.length}
          </button>
        </div>

        {/* TASK-072: Mock Integration Transparency Badges */}
        <div className="hidden lg:flex items-center gap-1.5">
          <span
            data-testid="admin-badge-mocked-sms"
            className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-[10px] font-bold"
          >
            🔔 Demo Data - Mocked SMS Service
          </span>
          <span
            data-testid="admin-badge-erp-sync"
            className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-purple-50 border border-purple-200 text-purple-700 text-[10px] font-bold"
          >
            🏗️ Simulated ERP Sync
          </span>
        </div>
      </header>

      {/* ── 2. Full-Screen Desktop GIS Map Canvas (z-map = 1) ── */}
      <div className="flex-1 w-full h-full relative">
        <CommandMapCanvas
          reports={filteredReports}
          hotspots={hotspots}
          selectedReport={selectedReport}
          onSelectReport={setSelectedReport}
          onSelectCluster={handleSelectCluster}
          className="w-full h-full"
        />

        {/* ── 3. Floating Left Sidebar: "Fix First" Queue (z-floating = 10) ── */}
        <div className="absolute top-24 left-6 bottom-24 z-floating w-80 md:w-88 pointer-events-auto">
          <FixFirstQueue
            reports={filteredReports}
            selectedReportId={selectedReport?.id}
            onSelectReport={setSelectedReport}
            className="w-full h-full"
          />
        </div>

        {/* ── 4. Floating Right Sidebar: Incident Detail & Dispatch Panel (z-floating = 10) ── */}
        {selectedReport && (
          <div className="absolute top-24 right-6 bottom-24 z-floating w-88 md:w-96 rounded-2xl shadow-floating border border-slate-200/90 overflow-hidden bg-white pointer-events-auto">
            <IncidentDetailPanel
              report={selectedReport}
              onClose={() => setSelectedReport(null)}
              onRefresh={loadData}
              className="w-full h-full"
            />
          </div>
        )}

        {/* ── 5. Systemic Insight Callout Banner (Bottom Center) ── */}
        <SystemicInsightCallout />
      </div>

      {/* ── 6. Action Brief Modal (z-modal = 100) ── */}
      <ActionBriefModal
        cluster={selectedCluster}
        isOpen={actionBriefOpen}
        onClose={() => setActionBriefOpen(false)}
        onDispatched={loadData}
      />
    </div>
  );
}

