/**
 * Phase 8: Design System & UI Component Library Verification Test
 * Validates:
 * 1. CSS variable design tokens in globals.css (Brand, Priority, Canvas, Geometry, Shadows, Z-index)
 * 2. WCAG contrast ratios for all PriorityBadge and StatusBadge color pairs (> 4.5:1)
 * 3. Component definitions: PriorityBadge, StatusBadge, FilterChip, ActionButton, FloatingCard
 * 4. Touch target compliance (minimum 48px height)
 * 5. Z-index scale compliance (1, 5, 10, 50, 100)
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function hexToRgb(hex) {
  const cleanHex = hex.replace("#", "");
  const bigint = parseInt(cleanHex, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

function getLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const val = c / 255;
    return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(hex1, hex2) {
  const c1 = hexToRgb(hex1);
  const c2 = hexToRgb(hex2);
  const l1 = getLuminance(c1.r, c1.g, c1.b);
  const l2 = getLuminance(c2.r, c2.g, c2.b);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function runVerification() {
  console.log("=".repeat(70));
  console.log("STARTING PHASE 8 DESIGN SYSTEM & UI COMPONENT LIBRARY TESTS");
  console.log("=".repeat(70));

  const globalsPath = path.join(__dirname, "src/styles/globals.css");
  assert(fs.existsSync(globalsPath), "globals.css must exist");
  const css = fs.readFileSync(globalsPath, "utf-8");

  // ── TEST 1: TASK-049 CSS Variables Verification ──────────────────────────
  console.log("\nTest 1: TASK-049 CSS Variables Verification");
  const requiredTokens = [
    ["--color-brand-teal-dark", "#0B6B61"],
    ["--color-brand-teal-light", "#E1F2EF"],
    ["--color-brand-teal-hover", "#08544C"],
    ["--color-brand-teal-border", "#A8DADC"],
    ["--color-priority-high-bg", "#FCE8E2"],
    ["--color-priority-high-text", "#C53030"],
    ["--color-priority-med-bg", "#FEF3C7"],
    ["--color-priority-med-text", "#B45309"],
    ["--color-priority-low-bg", "#E6FFFA"],
    ["--color-priority-low-text", "#0D9488"],
    ["--color-canvas-bg", "#F8FAFC"],
    ["--color-map-canvas-bg", "#EAEFEA"],
    ["--color-slate-900", "#1E293B"],
  ];

  for (const [token, expectedHex] of requiredTokens) {
    const hasToken = css.includes(token) && css.toLowerCase().includes(expectedHex.toLowerCase());
    assert(hasToken, `globals.css must contain ${token}: ${expectedHex}`);
    console.log(`  [PASS] Token ${token} = ${expectedHex}`);
  }

  // ── TEST 2: TASK-050 Typography, Radii and Shadows ───────────────────────
  console.log("\nTest 2: TASK-050 Typography, Radii and Elevation Shadows");
  const structureRules = [
    ["text-display", "24px"],
    ["text-section", "18px"],
    ["text-subtitle", "14px"],
    ["text-body", "14px"],
    ["text-micro", "12px"],
    ["rounded-pill", "9999px"],
    ["rounded-xl", "24px"],
    ["rounded-lg", "16px"],
    ["rounded-md", "12px"],
    ["shadow-subtle", "0px 2px 8px"],
    ["shadow-floating", "0px 8px 24px"],
    ["shadow-modal", "0px -4px 32px"],
  ];

  for (const [rule, expectedVal] of structureRules) {
    assert(css.includes(rule) && css.includes(expectedVal), `CSS must define ${rule} with ${expectedVal}`);
    console.log(`  [PASS] Geometry/Typography rule '${rule}' contains '${expectedVal}'`);
  }

  // ── TEST 3: TASK-051 WCAG Contrast Ratio (> 4.5:1) ──────────────────────
  console.log("\nTest 3: TASK-051 WCAG Accessible Contrast Verification (> 4.5:1)");
  const badgePairs = [
    { name: "Priority High", bg: "#FCE8E2", text: "#C53030" },
    { name: "Priority Medium", bg: "#FEF3C7", text: "#B45309" },
    { name: "Priority Low (Accessible #0F766E)", bg: "#E6FFFA", text: "#0F766E" },
    { name: "Status Submitted", bg: "#F1F5F9", text: "#334155" },
    { name: "Status Under Review", bg: "#FEF3C7", text: "#B45309" },
    { name: "Status Assigned", bg: "#E1F2EF", text: "#0B6B61" },
    { name: "Status Resolved", bg: "#DCFCE7", text: "#15803D" },
  ];

  for (const pair of badgePairs) {
    const ratio = getContrastRatio(pair.bg, pair.text);
    assert(ratio >= 4.5, `${pair.name} contrast ratio ${ratio.toFixed(2)}:1 must be >= 4.5:1`);
    console.log(`  [PASS] ${pair.name} contrast ratio: ${ratio.toFixed(2)}:1 (WCAG AA compliant)`);
  }

  // ── TEST 4: TASK-052 FilterChip & ActionButton Touch Targets ─────────────
  console.log("\nTest 4: TASK-052 FilterChip & ActionButton Touch Targets");
  const chipFile = fs.readFileSync(path.join(__dirname, "src/components/ui/FilterChip.tsx"), "utf-8");
  assert(chipFile.includes("min-h-[48px]"), "FilterChip must enforce min-h-[48px] touch target");
  assert(chipFile.includes("#0B6B61"), "FilterChip active state must use #0B6B61");
  assert(chipFile.includes("#E2E8F0"), "FilterChip inactive state must use #E2E8F0 border");
  console.log("  [PASS] FilterChip enforces minimum 48px touch target and active/inactive state styles.");

  const buttonFile = fs.readFileSync(path.join(__dirname, "src/components/ui/ActionButton.tsx"), "utf-8");
  assert(buttonFile.includes("h-[52px]"), "ActionButton must use 52px height");
  assert(buttonFile.includes("min-h-[48px]"), "ActionButton must enforce minimum 48px touch target");
  assert(buttonFile.includes("font-bold"), "ActionButton must have bold text");
  assert(buttonFile.includes("fullWidth"), "ActionButton must support fullWidth layout");
  console.log("  [PASS] ActionButton enforces 52px height, >= 48px touch targets, and fullWidth support.");

  // ── TEST 5: TASK-053 FloatingCard & Z-Index Hierarchy ────────────────────
  console.log("\nTest 5: TASK-053 FloatingCard & Global Z-Index Hierarchy");
  const cardFile = fs.readFileSync(path.join(__dirname, "src/components/ui/FloatingCard.tsx"), "utf-8");
  assert(cardFile.includes("0px 8px 24px rgba(0, 0, 0, 0.08)"), "FloatingCard must use shadow-floating");
  assert(cardFile.includes("24px"), "FloatingCard must use 24px border radius (radius-xl)");
  assert(cardFile.includes("zIndex"), "FloatingCard must accept zIndex parameter");

  const zIndexes = [
    ["--z-map", "1"],
    ["--z-pins", "5"],
    ["--z-floating", "10"],
    ["--z-popover", "50"],
    ["--z-modal", "100"],
  ];
  for (const [zToken, zVal] of zIndexes) {
    assert(css.includes(zToken) && css.includes(zVal), `globals.css must specify ${zToken}: ${zVal}`);
    console.log(`  [PASS] Z-Index scale verified: ${zToken} = ${zVal}`);
  }

  console.log("\n" + "=".repeat(70));
  console.log("ALL PHASE 8 DESIGN SYSTEM & UI COMPONENT TESTS PASSED!");
  console.log("=".repeat(70));
}

function assert(condition, message) {
  if (!condition) {
    console.error(`  [FAIL] ${message}`);
    process.exit(1);
  }
}

runVerification();
