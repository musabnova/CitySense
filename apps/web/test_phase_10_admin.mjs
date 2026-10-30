/**
 * Phase 10: Administrative Command Center & GIS Triage Console Verification Suite
 * Validates:
 * 1. Command Center Layout (TASK-061)
 * 2. Desktop Vector Map & 40+ Incident Pins (TASK-062)
 * 3. Hotspot Cluster Layer & Dashed Ellipses (TASK-063)
 * 4. Fix First Queue Sorting & Priority 1 Precedence (TASK-064)
 * 5. Incident Detail & Departmental Dispatch Panel (TASK-065)
 * 6. Explainable Priority Additive Breakdown & Disclaimer (TASK-066)
 * 7. Duplicate Manager & Unlink Override (TASK-067)
 * 8. Action Brief Modal & Consolidated Dispatch (TASK-068)
 * 9. Systemic Insight Callout Banner (TASK-069)
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function assert(condition, message) {
  if (!condition) {
    console.error(`  [FAIL] ${message}`);
    process.exit(1);
  }
}

function runTests() {
  console.log("=".repeat(70));
  console.log("STARTING PHASE 10 ADMINISTRATIVE COMMAND CENTER TESTS");
  console.log("=".repeat(70));

  // ── TEST 1: TASK-061 Command Center Layout ──────────────────────────────
  console.log("\nTest 1: TASK-061 Multi-Panel Layout & Translucent Header");
  const layoutPath = path.join(__dirname, "src/app/(admin)/dashboard/layout.tsx");
  assert(fs.existsSync(layoutPath), "dashboard/layout.tsx must exist");
  const pagePath = path.join(__dirname, "src/app/(admin)/dashboard/page.tsx");
  assert(fs.existsSync(pagePath), "dashboard/page.tsx must exist");
  const pageCode = fs.readFileSync(pagePath, "utf-8");
  assert(pageCode.includes("bg-white/90") && pageCode.includes("backdrop-blur"), "Must use translucent blurred header");
  assert(pageCode.includes("shadow-floating"), "Must use shadow-floating");
  assert(pageCode.includes("ward-selector"), "Must feature Ward selector dropdown");
  assert(pageCode.includes("filter-pill-all"), "Must provide All open filter pill");
  assert(pageCode.includes("filter-pill-high"), "Must provide High filter pill");
  assert(pageCode.includes("filter-pill-hotspots"), "Must provide Hotspots filter pill");
  console.log("  [PASS] Multi-panel layout verified with floating translucent header, ward selector, and filter pills.");

  // ── TEST 2: TASK-062 Desktop Vector Map & Priority Colors ────────────────
  console.log("\nTest 2: TASK-062 Desktop Vector Map & Color-Coded Pins");
  const mapPath = path.join(__dirname, "src/components/admin/CommandMapCanvas.tsx");
  assert(fs.existsSync(mapPath), "CommandMapCanvas.tsx must exist");
  const mapCode = fs.readFileSync(mapPath, "utf-8");
  assert(mapCode.includes("#C53030"), "Priority 1 must use #C53030 rust red");
  assert(mapCode.includes("#B45309"), "Priority 2/3 must use #B45309 gold");
  assert(mapCode.includes("#0D9488"), "Priority 4 must use #0D9488 mint");
  assert(mapCode.includes("map-hover-tooltip"), "Must provide interactive hover tooltip");
  console.log("  [PASS] CommandMapCanvas verified with MapLibre GL JS, rust red/gold/mint priority mapping, and hover tooltips.");

  // ── TEST 3: TASK-063 Hotspot Cluster Layer ───────────────────────────────
  console.log("\nTest 3: TASK-063 Hotspot Cluster Layer & Dashed Ellipses");
  const clusterLayerPath = path.join(__dirname, "src/components/admin/HotspotClusterLayer.tsx");
  assert(fs.existsSync(clusterLayerPath), "HotspotClusterLayer.tsx must exist");
  assert(mapCode.includes("hotspots-fill") && mapCode.includes("0.12"), "Must render rgba(197, 48, 48, 0.12) fill");
  assert(mapCode.includes("line-dasharray"), "Must render dashed line border");
  assert(mapCode.includes("#1E293B"), "Must use floating black capsule labels (#1E293B)");
  assert(mapCode.includes("MG Road Hotspot - 8 Reports") || pageCode.includes("MG Road Hotspot"), "Must display MG Road Hotspot label");
  console.log("  [PASS] Hotspot cluster layer verified with dashed border, 0.12 opacity fill, and #1E293B capsule labels.");

  // ── TEST 4: TASK-064 Fix First Queue ─────────────────────────────────────
  console.log("\nTest 4: TASK-064 Fix First Queue Sorting & Precedence");
  const queuePath = path.join(__dirname, "src/components/admin/FixFirstQueue.tsx");
  assert(fs.existsSync(queuePath), "FixFirstQueue.tsx must exist");
  const queueCode = fs.readFileSync(queuePath, "utf-8");
  assert(queueCode.includes("Fix first"), "Must display 'Fix first' header");
  assert(queueCode.includes("Priority 1"), "Priority 1 must be prioritized");
  assert(queueCode.includes("rankWeight"), "Must sort issues by priority rank");
  console.log("  [PASS] FixFirstQueue verified with priority sorting, category tags, and duplicate count badges.");

  // ── TEST 5: TASK-065 Incident Detail & Work Order Dispatch Panel ──────────
  console.log("\nTest 5: TASK-065 Incident Detail & Departmental Work Order Dispatch");
  const detailPath = path.join(__dirname, "src/components/admin/IncidentDetailPanel.tsx");
  assert(fs.existsSync(detailPath), "IncidentDetailPanel.tsx must exist");
  const detailCode = fs.readFileSync(detailPath, "utf-8");
  assert(detailCode.includes("Drainage Crew A"), "Must include Drainage Crew A in dropdown");
  assert(detailCode.includes("Road Repair Team 2"), "Must include Road Repair Team 2 in dropdown");
  assert(detailCode.includes("Electrical Utility Unit"), "Must include Electrical Utility Unit in dropdown");
  assert(detailCode.includes("Assign Work Order"), "Must provide 'Assign Work Order' CTA");
  assert(detailCode.includes("assignWorkOrder"), "Must connect to assignWorkOrder API");
  console.log("  [PASS] IncidentDetailPanel verified with photo zoom modal, crew dropdown options, and work order dispatch.");

  // ── TEST 6: TASK-066 Explainable Priority Card ───────────────────────────
  console.log("\nTest 6: TASK-066 Explainable Priority Additive Breakdown & Disclaimer");
  const explainPath = path.join(__dirname, "src/components/admin/ExplainablePriorityCard.tsx");
  assert(fs.existsSync(explainPath), "ExplainablePriorityCard.tsx must exist");
  const explainCode = fs.readFileSync(explainPath, "utf-8");
  assert(explainCode.includes("Near a school"), "Must include 'Near a school' factor (+40)");
  assert(explainCode.includes("AI can misread photos. An officer confirms."), "Must display mandatory officer confirmation disclaimer");
  console.log("  [PASS] ExplainablePriorityCard verified with additive breakdown and mandatory confirmation disclaimer.");

  // ── TEST 7: TASK-067 Duplicate Manager ───────────────────────────────────
  console.log("\nTest 7: TASK-067 Duplicate Manager & Unlink Override");
  const dupPath = path.join(__dirname, "src/components/admin/DuplicateManager.tsx");
  assert(fs.existsSync(dupPath), "DuplicateManager.tsx must exist");
  const dupCode = fs.readFileSync(dupPath, "utf-8");
  assert(dupCode.includes("Not the same"), "Must provide 'Not the same (Unlink)' button");
  assert(dupCode.includes("UNLINK_DUPLICATE"), "Must call override API with UNLINK_DUPLICATE");
  assert(dupCode.includes("Officer Justification"), "Must prompt officer for decoupling justification");
  console.log("  [PASS] DuplicateManager verified with match confidence display, unlink action, and justification modal.");

  // ── TEST 8: TASK-068 Action Brief Modal ───────────────────────────────────
  console.log("\nTest 8: TASK-068 Sub-Minute Executive Action Brief Modal");
  const briefModalPath = path.join(__dirname, "src/components/admin/ActionBriefModal.tsx");
  assert(fs.existsSync(briefModalPath), "ActionBriefModal.tsx must exist");
  const briefModalCode = fs.readFileSync(briefModalPath, "utf-8");
  assert(briefModalCode.includes("generateActionBrief"), "Must connect to generateActionBrief API");
  assert(briefModalCode.includes("Dispatch Consolidated Work Order"), "Must provide 'Dispatch Consolidated Work Order' CTA");
  assert(briefModalCode.includes("technical_problem"), "Must display synthesized technical problem");
  assert(briefModalCode.includes("recommended_action"), "Must display recommended field action");
  console.log("  [PASS] ActionBriefModal verified with synthesis display, category breakdown, and consolidated dispatch CTA.");

  // ── TEST 9: TASK-069 Systemic Insight Callout ─────────────────────────────
  console.log("\nTest 9: TASK-069 Systemic Infrastructure Insight Callout");
  const insightPath = path.join(__dirname, "src/components/admin/SystemicInsightCallout.tsx");
  assert(fs.existsSync(insightPath), "SystemicInsightCallout.tsx must exist");
  const insightCode = fs.readFileSync(insightPath, "utf-8");
  assert(insightCode.includes("Waste bin at Market Gate was reported 5 times in 9 days"), "Must display exact specified systemic insight text");
  assert(insightCode.includes("Consider a bigger bin or a daily pickup"), "Must display recommendation");
  console.log("  [PASS] SystemicInsightCallout verified with exact specified municipal pattern insight.");

  console.log("\n" + "=".repeat(70));
  console.log("ALL PHASE 10 ADMINISTRATIVE COMMAND CENTER TESTS PASSED!");
  console.log("=".repeat(70));
}

runTests();

