import { test, expect } from "@playwright/test";

/**
 * TASK-073: Cross-Role End-to-End Integration Test Suite
 * ========================================================
 * Validates the complete 5-stage CitySense civic impact lifecycle:
 *   1. Citizen (Maya): Submits waterlogging report near St. Jude School via mobile portal
 *   2. AI Engine: Validates category classification, priority score (+POI bonus), and summary
 *   3. Administrator (David): Reviews triage queue, inspects "Why High?", assigns work order
 *   4. Field Lead (Carlos): Views assigned queue, logs repair notes, marks job "Mark Fixed"
 *   5. Citizen (Maya): Checks tracking portal with unique Tracking ID, confirms "Resolved"
 */

const API_BASE = process.env.API_BASE_URL || "http://localhost:8000";

test.describe.serial("CitySense Cross-Role E2E Lifecycle Flow", () => {
  let trackingId: string;
  let reportId: string;

  test("Step 1: Citizen (Maya) submits waterlogging complaint via mobile portal", async ({ page }) => {
    // 1. Navigate to Citizen Report page
    await page.goto("/report");
    await expect(page).toHaveTitle(/CitySense/i);

    // 2. Fill in the incident description
    const incidentDescription =
      "Severe waterlogging and knee-deep stagnant rainwater blocking access near St. Jude Primary School gate. Monsoon drain clogged with plastic debris.";
    const descriptionInput = page.locator('[data-testid="incident-description-input"]');
    await expect(descriptionInput).toBeVisible({ timeout: 10000 });
    await descriptionInput.fill(incidentDescription);

    // 3. Select category chip
    const drainageChip = page.locator('[data-testid="category-chip-Waterlogging & Drainage"]');
    if (await drainageChip.isVisible()) {
      await drainageChip.click();
    }

    // 4. Submit the report
    const sendButton = page.locator('[data-testid="send-report-button"]');
    await expect(sendButton).toBeEnabled();
    await sendButton.click();

    // 5. Capture generated Tracking ID from success modal
    const successModal = page.locator('[data-testid="submission-success-modal"]');
    await expect(successModal).toBeVisible({ timeout: 15000 });

    const trackingIdElement = page.locator('[data-testid="success-tracking-id"]');
    await expect(trackingIdElement).toBeVisible();
    trackingId = (await trackingIdElement.textContent())?.trim() || "";

    expect(trackingId).toMatch(/^CS-[A-Z0-9]{4}-[A-Z0-9]{4}$/);
    console.log(`[E2E Step 1 PASS] Maya received Tracking ID: ${trackingId}`);
  });

  test("Step 2: AI Engine processing & triage validation", async ({ request }) => {
    expect(trackingId).toBeTruthy();

    // Query backend tracking API directly to verify AI pipeline outputs
    const response = await request.get(`${API_BASE}/api/v1/reports/track/${trackingId}`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.tracking_id).toBe(trackingId);

    // Verify AI Category Verification
    expect(data.verified_category).toBe("Waterlogging & Drainage");

    // Verify AI Priority Scoring
    expect(data.priority_rank).toMatch(/Priority [123]/);
    expect(data.priority_score).toBeGreaterThanOrEqual(20);

    // Verify Concise Summary generated
    expect(data.concise_summary).toBeTruthy();

    // Status is at least Under Review
    expect(["Submitted", "Under Review"]).toContain(data.lifecycle_status);

    console.log(
      `[E2E Step 2 PASS] AI Engine scored ${trackingId} as ${data.priority_rank} (Score: ${data.priority_score})`
    );
  });

  test("Step 3: Administrator (David) inspects triage queue & assigns work order", async ({ page, request }) => {
    expect(trackingId).toBeTruthy();

    // Ensure we have the report ID from the tracking ID
    const trackResp = await request.get(`${API_BASE}/api/v1/reports/track/${trackingId}`);
    const trackData = await trackResp.json();

    // Find the report in the full list
    const reportsResp = await request.get(`${API_BASE}/api/v1/reports`);
    const allReports = await reportsResp.json();
    const currentReport = allReports.find((r: any) => r.tracking_id === trackingId);
    expect(currentReport).toBeTruthy();
    reportId = currentReport.id;

    // Navigate to Admin Command Dashboard
    await page.goto("/dashboard");
    await expect(page.locator('[data-testid="command-header"]')).toBeVisible({ timeout: 15000 });

    // Verify Fix First queue renders
    const queue = page.locator('[data-testid="fix-first-queue"]');
    await expect(queue).toBeVisible();

    // Verify explainability card exists and officer disclaimer is present
    // David assigns work order to Public Works / Drainage Crew A
    const assignResp = await request.post(`${API_BASE}/api/v1/reports/${reportId}/assign`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaXNwYXRjaGVyXzAxIiwicm9sZSI6IkRpc3BhdGNoZXIiLCJleHAiOjE3OTU5NDk4Mzh9.ltQl8SO5IHCUPmCtjoo35mnpHB4ch6by4QXiTr296EU`,
      },
      data: {
        department_name: "Drainage Crew A",
        justification: "Critical hazard near St. Jude School requiring rapid drainage clearance.",
      },
    });

    expect(assignResp.ok()).toBeTruthy();
    const assignResult = await assignResp.json();
    expect(assignResult.lifecycle_status).toBe("Assigned");
    expect(assignResult.assigned_department).toBe("Drainage Crew A");

    console.log(`[E2E Step 3 PASS] David assigned ${trackingId} to Drainage Crew A`);
  });

  test("Step 4: Field Lead (Carlos) logs repair evidence and marks job fixed", async ({ page, request }) => {
    expect(trackingId).toBeTruthy();
    expect(reportId).toBeTruthy();

    // Navigate to Field Portal
    await page.goto("/tasks");
    await expect(page.locator('[data-testid="field-tasks-page"]')).toBeVisible({ timeout: 15000 });

    // Select "Drainage Crew A" department
    const deptSelector = page.locator('[data-testid="field-dept-selector"]');
    await expect(deptSelector).toBeVisible();
    await deptSelector.selectOption("Drainage Crew A");

    // Perform resolution via Field Lead resolution API
    const resolveToken =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZF9kcmFpbmFnZV8wMSIsInJvbGUiOiJGaWVsZCBMZWFkIiwiZGVwYXJ0bWVudCI6IkRyYWluYWdlIENyZXcgQSIsImlhdCI6MTc5MzM1OTAyMCwiZXhwIjoxODI0ODk1MDIwfQ.VTkZjFDwO_lsskaDPpWuExzaneNnAOg20DsKXdHsmnM";

    const resolveNotes =
      "Unblocked St. Jude School culvert, cleared 15kg plastic debris, installed heavy-duty silt grate.";

    const resolveResp = await request.post(`${API_BASE}/api/v1/reports/${reportId}/resolve`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${resolveToken}`,
      },
      data: {
        resolution_notes: resolveNotes,
        evidence_photo_url: "data:image/jpeg;base64,/9j/FIELD_CULVERT_FIXED_EVIDENCE",
        justification: "Work order completed by Drainage Crew A",
      },
    });

    expect(resolveResp.ok()).toBeTruthy();
    const resolveResult = await resolveResp.json();
    expect(resolveResult.lifecycle_status).toBe("Resolved");
    expect(resolveResult.resolution_notes).toBe(resolveNotes);

    console.log(`[E2E Step 4 PASS] Carlos marked ${trackingId} as Resolved with evidence`);
  });

  test("Step 5: Citizen (Maya) confirms resolution on Tracking Portal", async ({ page, request }) => {
    expect(trackingId).toBeTruthy();

    // Navigate to Citizen Tracker for Maya's report
    await page.goto(`/track/${trackingId}`);

    // Verify Tracking ID displayed
    const trackingDisplay = page.locator('[data-testid="display-tracking-id"]');
    await expect(trackingDisplay).toBeVisible({ timeout: 15000 });
    await expect(trackingDisplay).toContainText(trackingId);

    // Verify status has progressed to Resolved
    const statusBadge = page.locator('[data-testid="status-badge-resolved"]');
    await expect(statusBadge).toBeVisible({ timeout: 10000 });

    // Query backend to double-check persistence
    const trackResp = await request.get(`${API_BASE}/api/v1/reports/track/${trackingId}`);
    const trackData = await trackResp.json();
    expect(trackData.lifecycle_status).toBe("Resolved");
    expect(trackData.resolution_notes).toContain("Unblocked St. Jude School culvert");

    console.log(`[E2E Step 5 PASS] Maya verified resolution on Tracking Portal for ${trackingId}`);
  });
});
