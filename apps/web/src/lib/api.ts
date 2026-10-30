// CitySense Admin API Client with RBAC Dispatcher Authentication
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Pre-signed development dispatcher token (role: Dispatcher)
export const DISPATCHER_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaXNwYXRjaGVyXzAxIiwicm9sZSI6IkRpc3BhdGNoZXIiLCJleHAiOjE3OTU5NDk4Mzh9.ltQl8SO5IHCUPmCtjoo35mnpHB4ch6by4QXiTr296EU";

export const getAuthHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${DISPATCHER_TOKEN}`,
});

export async function fetchSpatialReports(params?: {
  lifecycle_status?: string;
  priority_rank?: string;
  ward_id?: string;
}) {
  const query = new URLSearchParams();
  if (params?.lifecycle_status) query.set("lifecycle_status", params.lifecycle_status);
  if (params?.priority_rank) query.set("priority_rank", params.priority_rank);
  if (params?.ward_id) query.set("ward_id", params.ward_id);

  const res = await fetch(`${API_BASE_URL}/api/v1/spatial/reports?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch spatial reports: ${res.status}`);
  return res.json();
}

export async function fetchSpatialHotspots() {
  const res = await fetch(`${API_BASE_URL}/api/v1/spatial/hotspots`);
  if (!res.ok) throw new Error(`Failed to fetch spatial hotspots: ${res.status}`);
  return res.json();
}

export async function fetchAllReports(params?: {
  lifecycle_status?: string;
  priority_rank?: string;
  category?: string;
}) {
  const query = new URLSearchParams();
  if (params?.lifecycle_status) query.set("lifecycle_status", params.lifecycle_status);
  if (params?.priority_rank) query.set("priority_rank", params.priority_rank);
  if (params?.category) query.set("category", params.category);

  const res = await fetch(`${API_BASE_URL}/api/v1/reports?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch reports: ${res.status}`);
  return res.json();
}

export async function fetchReportDetail(reportId: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}`);
  if (!res.ok) throw new Error(`Failed to fetch report detail: ${res.status}`);
  return res.json();
}

export async function assignWorkOrder(
  reportId: string,
  departmentName: string,
  justification: string = "Dispatched from Admin Command Console"
) {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/assign`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      department_name: departmentName,
      justification,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Assignment failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function overrideReport(
  reportId: string,
  action: "SET_PRIORITY" | "UNLINK_DUPLICATE",
  justification: string,
  newPriority?: string
) {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/override`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      action,
      justification,
      new_priority: newPriority,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Override failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function generateActionBrief(clusterId: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/clusters/${clusterId}/action-brief`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Action brief failed with HTTP ${res.status}`);
  }
  return res.json();
}

// ─── TASK-070: Field Lead Pre-signed Tokens ────────────────────────────────────
// Each token encodes role="Field Lead" and the specific department in JWT payload.
// Department-based access is enforced server-side from the token, not from URL params.

export const FIELD_TOKENS: Record<string, string> = {
  "Drainage Crew A":
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZF9kcmFpbmFnZV8wMSIsInJvbGUiOiJGaWVsZCBMZWFkIiwiZGVwYXJ0bWVudCI6IkRyYWluYWdlIENyZXcgQSIsImlhdCI6MTc5MzM1OTAyMCwiZXhwIjoxODI0ODk1MDIwfQ.VTkZjFDwO_lsskaDPpWuExzaneNnAOg20DsKXdHsmnM",
  "Road Repair Team 2":
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZF9yb2FkXzAxIiwicm9sZSI6IkZpZWxkIExlYWQiLCJkZXBhcnRtZW50IjoiUm9hZCBSZXBhaXIgVGVhbSAyIiwiaWF0IjoxNzkzMzU5MDIwLCJleHAiOjE4MjQ4OTUwMjB9.4MsUP08j5SATxB9PNbMfy6so9ieNBHVEyxpJfrGcGN0",
  "Electrical Utility Unit":
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZF9lbGVjdHJpY2FsXzAxIiwicm9sZSI6IkZpZWxkIExlYWQiLCJkZXBhcnRtZW50IjoiRWxlY3RyaWNhbCBVdGlsaXR5IFVuaXQiLCJpYXQiOjE3OTMzNTkwMjAsImV4cCI6MTgyNDg5NTAyMH0.qKURtFyY4867XUdn22Mztky10M9BB4qZ2IblTfUAuxg",
};

export const FIELD_LEAD_DEPARTMENTS = Object.keys(FIELD_TOKENS);

export const getFieldAuthHeaders = (token: string) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

// ─── TASK-070: Field Tasks API ────────────────────────────────────────────────
export async function fetchFieldTasks(token: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/field/tasks`, {
    headers: getFieldAuthHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch field tasks: ${res.status}`);
  }
  return res.json();
}

// ─── TASK-071: Field Job Resolution ──────────────────────────────────────────
export async function resolveFieldJob(
  reportId: string,
  resolutionNotes: string,
  evidencePhotoUrl: string,
  token: string
) {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/resolve`, {
    method: "POST",
    headers: getFieldAuthHeaders(token),
    body: JSON.stringify({
      resolution_notes: resolutionNotes,
      evidence_photo_url: evidencePhotoUrl,
      justification: "Field crew marked job as resolved via Field Portal",
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Resolution failed with HTTP ${res.status}`);
  }
  return res.json();
}

// ─── TASK-072: Mock Integration Logs ─────────────────────────────────────────
export async function fetchMockIntegrationLogs() {
  const res = await fetch(`${API_BASE_URL}/api/v1/mock-integration-logs`);
  if (!res.ok) throw new Error("Failed to fetch mock integration logs");
  return res.json();
}
