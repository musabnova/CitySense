"use client";

import React, { useState } from "react";
import {
  PriorityBadge,
  StatusBadge,
  FilterChip,
  ActionButton,
  FloatingCard,
} from "@/components/ui";

export default function DesignSystemShowcase() {
  const [activeChip, setActiveChip] = useState("all");
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <main className="p-6 md:p-12 max-w-5xl mx-auto space-y-10">
      {/* Header */}
      <header className="space-y-2">
        <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-[#E1F2EF] text-[#0B6B61]">
          Phase 8: Design System & UI Component Library
        </div>
        <h1 className="text-display text-[#1E293B]">CitySense Design System</h1>
        <p className="text-body text-[#64748B]">
          Tokens, semantic priority badges, touch targets, and elevation hierarchy for the Civic AI Platform.
        </p>
      </header>

      {/* 1. Color Tokens Palette */}
      <section className="space-y-4">
        <h2 className="text-section text-[#1E293B]">1. Brand & Surface Tokens</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
            <div className="h-12 rounded-lg bg-[#0B6B61]" />
            <div className="text-micro font-bold text-[#1E293B]">Brand Teal Dark</div>
            <div className="text-micro text-[#64748B]">#0B6B61</div>
          </div>
          <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
            <div className="h-12 rounded-lg bg-[#E1F2EF] border border-[#A8DADC]" />
            <div className="text-micro font-bold text-[#1E293B]">Brand Teal Light</div>
            <div className="text-micro text-[#64748B]">#E1F2EF</div>
          </div>
          <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
            <div className="h-12 rounded-lg bg-[#08544C]" />
            <div className="text-micro font-bold text-[#1E293B]">Brand Teal Hover</div>
            <div className="text-micro text-[#64748B]">#08544C</div>
          </div>
          <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-subtle space-y-2">
            <div className="h-12 rounded-lg bg-[#A8DADC]" />
            <div className="text-micro font-bold text-[#1E293B]">Brand Teal Border</div>
            <div className="text-micro text-[#64748B]">#A8DADC</div>
          </div>
        </div>
      </section>

      {/* 2. Semantic Badges */}
      <section className="space-y-4">
        <h2 className="text-section text-[#1E293B]">2. Semantic Badges (WCAG Contrast &gt; 4.5:1)</h2>
        <div className="flex flex-wrap items-center gap-6 p-6 rounded-xl bg-white border border-slate-200 shadow-subtle">
          <div className="space-y-2">
            <div className="text-micro text-[#64748B]">Priority Badges</div>
            <div className="flex items-center gap-2">
              <PriorityBadge priority="High" />
              <PriorityBadge priority="Medium" />
              <PriorityBadge priority="Low" />
            </div>
          </div>
          <div className="h-10 w-px bg-slate-200 hidden sm:block" />
          <div className="space-y-2">
            <div className="text-micro text-[#64748B]">Lifecycle Status Badges</div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge status="Submitted" />
              <StatusBadge status="Under Review" />
              <StatusBadge status="Assigned" />
              <StatusBadge status="Resolved" />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Filter Chips & Touch Targets */}
      <section className="space-y-4">
        <h2 className="text-section text-[#1E293B]">3. Filter Chips (Min 48px Touch Targets)</h2>
        <div className="flex flex-wrap items-center gap-3 p-6 rounded-xl bg-white border border-slate-200 shadow-subtle">
          <FilterChip
            label="All open"
            count={12}
            active={activeChip === "all"}
            onClick={() => setActiveChip("all")}
          />
          <FilterChip
            label="High priority"
            count={3}
            active={activeChip === "high"}
            onClick={() => setActiveChip("high")}
          />
          <FilterChip
            label="Hotspots"
            count={2}
            active={activeChip === "hotspots"}
            onClick={() => setActiveChip("hotspots")}
          />
          <FilterChip
            label="Drainage"
            active={activeChip === "drainage"}
            onClick={() => setActiveChip("drainage")}
          />
          <FilterChip
            label="Road failure"
            active={activeChip === "roads"}
            onClick={() => setActiveChip("roads")}
          />
        </div>
      </section>

      {/* 4. Action Buttons (52px Height) */}
      <section className="space-y-4">
        <h2 className="text-section text-[#1E293B]">4. Action Buttons (52px Height)</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-6 rounded-xl bg-white border border-slate-200 shadow-subtle">
          <ActionButton variant="primary" fullWidth onClick={() => alert("Primary action clicked")}>
            Send report
          </ActionButton>
          <ActionButton variant="secondary" fullWidth onClick={() => alert("Secondary action clicked")}>
            Assign crew
          </ActionButton>
          <ActionButton variant="danger" fullWidth onClick={() => alert("Danger action clicked")}>
            De-escalate
          </ActionButton>
        </div>
      </section>

      {/* 5. Floating Card & Elevation Hierarchy */}
      <section className="space-y-4">
        <h2 className="text-section text-[#1E293B]">5. Floating Cards &amp; Z-Index Hierarchy</h2>
        <div className="relative min-h-[300px] p-6 rounded-xl bg-[#EAEFEA] border border-slate-300 overflow-hidden flex flex-col justify-between">
          {/* Simulated Map Canvas Layer (z-map = 1) */}
          <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
            <span className="text-3xl font-black text-slate-400 tracking-wider">
              MAP CANVAS LAYER (z-1)
            </span>
          </div>

          {/* Simulated Pins Layer (z-pins = 5) */}
          <div className="relative z-pins flex items-center gap-4">
            <span className="px-3 py-1 bg-red-600 text-white rounded-full text-xs font-bold shadow-md">
              Pin #1 (z-5)
            </span>
            <span className="px-3 py-1 bg-amber-500 text-white rounded-full text-xs font-bold shadow-md">
              Pin #2 (z-5)
            </span>
          </div>

          {/* Floating Card (z-floating = 10, shadow-floating, rounded-xl) */}
          <div className="relative z-floating max-w-md my-4">
            <FloatingCard elevation="floating" className="p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-micro font-bold text-[#0B6B61] tracking-wide uppercase">
                  Floating Card Panel (z-10)
                </span>
                <PriorityBadge priority="High" />
              </div>
              <h3 className="text-display text-[#1E293B] mb-1">
                Blocked drain, school gate
              </h3>
              <p className="text-subtitle text-[#64748B] mb-4">
                Ward 12 · 3 linked reports within 15 meters
              </p>
              <div className="flex items-center gap-3">
                <ActionButton
                  variant="primary"
                  className="flex-1"
                  onClick={() => setModalOpen(true)}
                >
                  Inspect Brief
                </ActionButton>
              </div>
            </FloatingCard>
          </div>

          {/* Z-Index Legend */}
          <div className="relative z-floating text-micro text-[#64748B] bg-white/80 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-200 inline-block self-start">
            Z-Index Scale: Map Canvas (z-1) &lt; Pins (z-5) &lt; Floating Sidebar (z-10) &lt; Popover (z-50) &lt; Modal/Sheet (z-100)
          </div>
        </div>
      </section>

      {/* Modal / Bottom Sheet Demo (z-modal = 100) */}
      {modalOpen && (
        <div className="fixed inset-0 z-modal flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-t-2xl sm:rounded-2xl max-w-lg w-full p-6 shadow-modal space-y-4 animate-in fade-in duration-200">
            <div className="flex items-center justify-between border-b pb-3 border-slate-100">
              <h3 className="text-section font-bold text-[#1E293B]">
                Action Brief Modal (z-100)
              </h3>
              <button
                onClick={() => setModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>
            <p className="text-body text-[#64748B]">
              This modal demonstrates z-100 elevation and shadow-modal, cleanly overlaying both the floating card panels and the underlying map canvas without clipping.
            </p>
            <div className="flex items-center gap-2 pt-2">
              <ActionButton variant="primary" fullWidth onClick={() => setModalOpen(false)}>
                Confirm &amp; Close
              </ActionButton>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

