# CitySense: AI-Powered Civic Impact Platform

> **"From Complaints to Action"** — Intelligent Municipal Infrastructure & Rapid Action Platform

CitySense is an end-to-end full-stack civic platform that transforms fragmented, unstructured citizen complaints into prioritized, explainable, and accountable municipal action.

---

## 1. System Architecture & Monorepo Structure

```
CitySense/
├── apps/
│   ├── api/                     # FastAPI backend (Python 3.12+), SQLAlchemy, PostGIS/pgvector, Celery
│   │   ├── core/                # Database pool, Redis client, HMAC-SHA256 RBAC token auth
│   │   ├── models/              # Relational models: Report, AdministrativeZone, ReportAuditLog
│   │   ├── routes/              # REST & GeoJSON API routers
│   │   ├── services/            # AI Pipeline: category, embeddings, duplicates, priority, action briefs
│   │   ├── standalone_server.py # Pure-Python zero-dependency HTTP server (port 8000)
│   │   └── tests/               # Unit, integration, and SLA benchmark test suites
│   └── web/                     # Next.js 15+ App Router, React 19, MapLibre GL, Tailwind CSS v4
│       ├── src/app/
│       │   ├── (citizen)/       # Citizen Mobile PWA: /report & /track/[id]
│       │   ├── (admin)/         # Admin Command Console: /dashboard
│       │   ├── (field)/         # Field Maintenance Portal: /tasks
│       │   └── page.tsx         # Design System Token Showcase: /
│       ├── src/components/      # Reusable UI component library (WCAG AA compliant)
│       └── src/lib/api.ts       # Typed API client with pre-signed RBAC tokens
├── tests/
│   └── e2e/                     # Playwright cross-role lifecycle test suite
├── scripts/
│   ├── demo_rehearsal.sh        # 5-minute live demo protocol script
│   └── demo_rehearsal.py        # Python/cross-platform demo protocol runner
├── citysense.db                 # Seeded SQLite database with 42+ realistic civic records
├── docker-compose.yml           # PostgreSQL 16 (PostGIS + pgvector) and Redis 7 orchestration
├── LIMITATIONS.md               # Transparency declaration, edge cases & real vs. mocked components
└── package.json                 # Monorepo pnpm workspace configuration
```

---

## 2. Core Stakeholder Portals & URLs

| Role | Target Persona | Route | Key Capabilities |
|:---|:---|:---|:---|
| **Citizen Capture** | Maya | `http://localhost:3000/report` | < 60s mobile reporting, photo upload, draggable GPS map pin, instant AI category hint, unique Tracking ID (`CS-XXXX-XXXX`). |
| **Citizen Tracking** | Maya | `http://localhost:3000/track/[id]` | 4-stage vertical lifecycle tracker (`Submitted` → `Under Review` → `Assigned` → `Resolved`), QR code, duplicate consolidation notice. |
| **Command Console** | David (Dispatcher) | `http://localhost:3000/dashboard` | Full-screen GIS map canvas, "Fix First" priority-sorted triage queue, explainable "Why High?" cards, sub-minute Action Brief modal. |
| **Field Lead Portal** | Carlos (Maintenance) | `http://localhost:3000/tasks` | High-contrast mobile task queue filtered by authenticated department, GPS navigation links, photo evidence upload, "Mark Fixed" resolution CTA. |
| **Design Tokens** | Developers | `http://localhost:3000/` | Interactive design system showcase displaying color tokens, badges, buttons, cards, and WCAG AA contrast audits. |

---

## 3. Quick Start: Local Development Setup

### Prerequisites
- **Node.js** >= 20.0.0 (v22+ recommended)
- **pnpm** >= 9.0.0
- **Python** >= 3.12 (Python 3.12 or 3.13)

### Option A: Standard Local Setup (Recommended for Demo)

1. **Install Dependencies:**
   ```bash
   # From the root directory:
   pnpm install
   ```

2. **Start the Backend API Server:**
   ```bash
   # In Terminal 1:
   python -m apps.api.standalone_server
   # Server listens at http://localhost:8000
   ```

3. **Start the Next.js Frontend:**
   ```bash
   # In Terminal 2:
   pnpm --filter web dev
   # Web application available at http://localhost:3000
   ```

### Option B: Docker Containerized Setup (Full Production Stack)

```bash
# Provision PostgreSQL 16 with PostGIS & pgvector + Redis 7:
docker compose up -d

# Execute database migrations:
cd apps/api
alembic upgrade head

# Seed synthetic test data (40+ complaints, duplicates, POIs, MG Road corridor):
python -m apps.api.seeds.seed_db
```

---

## 4. Running the Automated Test & Benchmark Suites

### 1. Operational SLA Benchmark Suite (TASK-074)
Measures all 6 performance targets defined in PRD Section 6:
```bash
python -m apps.api.tests.benchmark_slas
```
*Expected Result:* **100% GREEN (ALL 6 SLAS PASS)**
- Intake Submission Latency: < 1 ms (Target: < 60,000 ms)
- Duplicate Detection Precision: 100.0% (Target: > 85.0%)
- Category Classification Accuracy: 100.0% (Target: > 90.0%)
- AI Triage Processing Speed: ~ 0.009 s (Target: < 120 s)
- Action Brief Generation Speed: ~ 0.01 ms (Target: < 15 s)
- Report Tracking Visibility: 100.0% (42/42 queryable)

### 2. Backend Integration Test Suite (TASK-070 to TASK-072)
```bash
python -m apps.api.tests.test_phase11_field
```
*Expected Result:* **74 PASS | 0 FAIL**

### 3. Frontend Component & Structure Test Suite
```bash
node apps/web/test_phase11_field.mjs
node apps/web/test_phase_10_admin.mjs
node apps/web/test_phase_9_citizen.mjs
node apps/web/test_design_system.mjs
```
*Expected Result:* **ALL PASS (100% Conformance)**

### 4. Playwright Cross-Role Lifecycle E2E Test (TASK-073)
```bash
npx playwright test tests/e2e/lifecycle_flow.spec.ts
```
*Expected Result:* **5/5 steps pass (Maya -> AI Engine -> David -> Carlos -> Maya)**

---

## 5. 5-Minute Live Demonstration Protocol

To rehearse or execute the live five-minute presentation:
```bash
python scripts/demo_rehearsal.py
# or in bash:
bash scripts/demo_rehearsal.sh
```

| Timeline | Stage | Presenter Action & Narrative | Screen / URL |
|:---|:---|:---|:---|
| **0:00 – 1:00** | **Capture** | Submit new waterlogging report near school. Show EXIF stripping, GPS pin drop, and receive unique Tracking ID `CS-XXXX-XXXX`. | `http://localhost:3000/report` |
| **1:00 – 2:00** | **Understand** | Switch to admin console. Show automated category validation, one-sentence summary, duplicate detection, and "Why High?" (+40 POI) card. | `http://localhost:3000/dashboard` |
| **2:00 – 3:00** | **Reveal** | Click MG Road cluster on GIS map. Highlight 8 correlated citizen reports. Click "Generate Action Brief" (synthesized in < 15ms). | `http://localhost:3000/dashboard` |
| **3:00 – 4:00** | **Act** | Assign Action Brief to Public Works / Drainage Crew A. Show child tickets synchronized. Switch to Field Portal and click "Mark Fixed". | `http://localhost:3000/tasks` |
| **4:00 – 5:00** | **Feedback Loop** | Open Citizen Tracker using Tracking ID. Verify state updated to `Resolved` with field notes and completed repair evidence. | `http://localhost:3000/track/[id]` |

---

## 6. Transparency & Governance

For full architectural boundary declarations, image fallback behaviors, geocoding edge cases, and mocked integration specifications, consult [LIMITATIONS.md](./LIMITATIONS.md).
