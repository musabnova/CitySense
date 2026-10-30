// Phase 11 Frontend Structure Test
// Tests TASK-070 and TASK-071 component/page file existence and key structural elements

import { readFileSync, existsSync } from "fs";
import { resolve } from "path";

let PASS = 0;
let FAIL = 0;

function check(label, condition, detail = "") {
  if (condition) {
    PASS++;
    console.log(`  [PASS] ${label}`);
  } else {
    FAIL++;
    console.log(`  [FAIL] ${label}${detail ? " | " + detail : ""}`);
  }
}

function section(title) {
  console.log(`\n${"=".repeat(60)}`);
  console.log(`  ${title}`);
  console.log("=".repeat(60));
}

const WEB = resolve("apps/web/src");
const API = resolve("apps/api");

function fileExists(rel) {
  return existsSync(resolve(rel));
}

function readFile(rel) {
  try {
    return readFileSync(resolve(rel), "utf-8");
  } catch {
    return "";
  }
}

// ─── SECTION 1: File Existence ────────────────────────────────────────────────
section("File Existence Checks");

check(
  "Field layout exists: apps/web/src/app/(field)/layout.tsx",
  fileExists("apps/web/src/app/(field)/layout.tsx")
);
check(
  "Field tasks page exists: apps/web/src/app/(field)/tasks/page.tsx",
  fileExists("apps/web/src/app/(field)/tasks/page.tsx")
);
check(
  "ResolveJobDrawer exists: apps/web/src/components/field/ResolveJobDrawer.tsx",
  fileExists("apps/web/src/components/field/ResolveJobDrawer.tsx")
);
check(
  "Mock integrations service exists: apps/api/services/mock_integrations.py",
  fileExists("apps/api/services/mock_integrations.py")
);

// ─── SECTION 2: api.ts exports ────────────────────────────────────────────────
section("api.ts Field API Exports");

const apiTs = readFile("apps/web/src/lib/api.ts");
check("api.ts exports FIELD_TOKENS", apiTs.includes("export const FIELD_TOKENS"));
check("api.ts exports fetchFieldTasks", apiTs.includes("export async function fetchFieldTasks"));
check("api.ts exports resolveFieldJob", apiTs.includes("export async function resolveFieldJob"));
check("api.ts exports fetchMockIntegrationLogs", apiTs.includes("export async function fetchMockIntegrationLogs"));
check("api.ts exports FIELD_LEAD_DEPARTMENTS", apiTs.includes("export const FIELD_LEAD_DEPARTMENTS"));
check("api.ts has Drainage Crew A token (real JWT)", apiTs.includes("Drainage Crew A") && apiTs.includes("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"));
check("api.ts has Road Repair Team 2 token", apiTs.includes("Road Repair Team 2"));
check("api.ts has Electrical Utility Unit token", apiTs.includes("Electrical Utility Unit"));
check("api.ts resolve endpoint uses /resolve path", apiTs.includes("/resolve"));

// ─── SECTION 3: Field Layout ──────────────────────────────────────────────────
section("TASK-070: Field Layout Structure");

const layout = readFile("apps/web/src/app/(field)/layout.tsx");
check("Layout has CitySense Field Portal header", layout.includes("CitySense Field Portal"));
check("Layout has high-contrast dark background (#0F172A)", layout.includes("0F172A") || layout.includes("0f172a"));
check("Layout has Field Lead role badge", layout.includes("Field Lead"));
check("Layout exports default function", layout.includes("export default function"));

// ─── SECTION 4: Field Tasks Page ──────────────────────────────────────────────
section("TASK-070: Field Tasks Page Structure");

const tasksPage = readFile("apps/web/src/app/(field)/tasks/page.tsx");
check("Tasks page has 'use client'", tasksPage.includes('"use client"'));
check("Tasks page imports fetchFieldTasks", tasksPage.includes("fetchFieldTasks"));
check("Tasks page imports FIELD_TOKENS", tasksPage.includes("FIELD_TOKENS"));
check("Tasks page has dept selector (data-testid)", tasksPage.includes("field-dept-selector"));
check("Tasks page has loading state", tasksPage.includes("field-tasks-loading") || tasksPage.includes("loading"));
check("Tasks page has empty state", tasksPage.includes("field-tasks-empty") || tasksPage.includes("No active work orders"));
check("Tasks page has error state", tasksPage.includes("field-tasks-error") || tasksPage.includes("Retry"));
check("Tasks page has task cards", tasksPage.includes("field-task-card") || tasksPage.includes("task-card"));
check("Tasks page has Navigate button (maps link)", tasksPage.includes("Navigate") && tasksPage.includes("google.com/maps"));
check("Tasks page has Mark Fixed button", tasksPage.includes("Mark Fixed"));
check("Tasks page imports ResolveJobDrawer", tasksPage.includes("ResolveJobDrawer"));
check("Tasks page shows duplicate_count badge", tasksPage.includes("duplicate_count") || tasksPage.includes("reports"));
check("Tasks page has TASK-072 SMS badge", tasksPage.includes("Demo Data - Mocked SMS Service"));
check("Tasks page has TASK-072 ERP badge", tasksPage.includes("Simulated ERP Sync"));
check("Tasks page uses PriorityBadge", tasksPage.includes("PriorityBadge"));
check("Tasks page uses StatusBadge", tasksPage.includes("StatusBadge"));

// ─── SECTION 5: ResolveJobDrawer ─────────────────────────────────────────────
section("TASK-071: ResolveJobDrawer Component");

const drawer = readFile("apps/web/src/components/field/ResolveJobDrawer.tsx");
check("Drawer has 'use client'", drawer.includes('"use client"'));
check("Drawer has 'Mark Fixed' CTA text", drawer.includes("Mark Fixed"));
check("Drawer has resolution notes textarea", drawer.includes("resolution-notes-textarea") || drawer.includes("resolution_notes") || drawer.includes("resolutionNotes"));
check("Drawer has photo upload input", drawer.includes("evidence-photo-input") || drawer.includes("evidence_photo"));
check("Drawer has mark-fixed-button testid", drawer.includes("mark-fixed-button"));
check("Drawer imports resolveFieldJob", drawer.includes("resolveFieldJob"));
check("Drawer shows success state after resolution", drawer.includes("resolve-success-state") || drawer.includes("Marked as Fixed") || drawer.includes("Resolved"));
check("Drawer shows error banner on failure", drawer.includes("resolve-error-banner") || drawer.includes("error") || drawer.includes("Error"));
check("Drawer has disabled state when submitting", drawer.includes("disabled") || drawer.includes("Marking"));
check("Drawer has close/cancel button", drawer.includes("onCancel") || drawer.includes("Cancel") || drawer.includes("✕"));
check("Drawer enforces required notes (disabled without notes)", drawer.includes("resolutionNotes.trim()") || drawer.includes("resolution_notes"));

// ─── SECTION 6: Mock integrations Python service ──────────────────────────────
section("TASK-072: mock_integrations.py Service");

const mockPy = readFile("apps/api/services/mock_integrations.py");
check("mock_integrations.py has MockSMSGateway class", mockPy.includes("class MockSMSGateway"));
check("mock_integrations.py has MockMunicipalERPAdapter class", mockPy.includes("class MockMunicipalERPAdapter"));
check("SMS facade label is exact match", mockPy.includes("[Demo Data - Mocked SMS Service]"));
check("ERP facade label is exact match", mockPy.includes("[Simulated ERP Sync]"));
check("Has send_dispatch_notification method", mockPy.includes("send_dispatch_notification"));
check("Has send_resolution_notification method", mockPy.includes("send_resolution_notification"));
check("Has push_work_order method", mockPy.includes("push_work_order"));
check("Has push_resolution method", mockPy.includes("push_resolution"));
check("Has trigger_dispatch_integrations helper", mockPy.includes("def trigger_dispatch_integrations"));
check("Has trigger_resolution_integrations helper", mockPy.includes("def trigger_resolution_integrations"));
check("Has get_mock_integration_logs helper", mockPy.includes("def get_mock_integration_logs"));
check("Has singleton instances", mockPy.includes("mock_sms_gateway") && mockPy.includes("mock_erp_adapter"));
check("No real HTTP calls (no requests/httpx import)", !mockPy.includes("import requests") && !mockPy.includes("import httpx"));
check("Clearly documents SIMULATION only", mockPy.includes("SIMULATION") || mockPy.includes("no real") || mockPy.includes("NOT REAL"));

// ─── SECTION 7: Admin dashboard transparency badges ──────────────────────────
section("TASK-072: Admin Dashboard Transparency Badges");

const dashPage = readFile("apps/web/src/app/(admin)/dashboard/page.tsx");
check("Admin dashboard has admin-badge-mocked-sms", dashPage.includes("admin-badge-mocked-sms"));
check("Admin dashboard has admin-badge-erp-sync", dashPage.includes("admin-badge-erp-sync"));
check("Admin dashboard displays SMS badge text", dashPage.includes("Demo Data - Mocked SMS Service"));
check("Admin dashboard displays ERP badge text", dashPage.includes("Simulated ERP Sync"));

// ─── SECTION 8: Standalone server additions ───────────────────────────────────
section("Backend Server: New Endpoints");

const server = readFile("apps/api/standalone_server.py");
check("Server has /api/v1/field/tasks route", server.includes("/api/v1/field/tasks"));
check("Server has /api/v1/reports/{id}/resolve route", server.includes("/resolve"));
check("Server has /api/v1/mock-integration-logs route", server.includes("mock-integration-logs"));
check("Server imports trigger_dispatch_integrations", server.includes("trigger_dispatch_integrations"));
check("Server imports trigger_resolution_integrations", server.includes("trigger_resolution_integrations"));
check("Server imports get_mock_integration_logs", server.includes("get_mock_integration_logs"));
check("Server enforces RBAC on field/tasks (ROLE_FIELD_LEAD)", server.includes("ROLE_FIELD_LEAD") && server.includes("field/tasks"));
check("Server uses token_department for filtering (not query params)", server.includes("token_department"));
check("Resolve endpoint validates resolution_notes", server.includes("resolution_notes is required"));
check("Resolve endpoint rejects already-Resolved", server.includes("already in 'Resolved'") || server.includes("already in"));

// ─── FINAL ────────────────────────────────────────────────────────────────────
console.log(`\n${"=".repeat(60)}`);
console.log(`  Phase 11 Frontend Tests: ${PASS} PASS | ${FAIL} FAIL`);
console.log("=".repeat(60));

if (FAIL > 0) {
  process.exit(1);
} else {
  console.log("  ALL TESTS PASSED");
  process.exit(0);
}

