# Changelog — CO-ATTAIN PRO AI

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-10-25

### Added — Backend

- **OBE Calculation Engine** (`backend/app/analytics/engine.py`)
  - Method A: Student Threshold Method — percentage of students ≥ target marks on each mapped question.
  - Method B: Normalized Score Method — sum of marks obtained / sum of maximum marks × 100.
  - CO-PO weighted mapping matrix — weighted contribution to PO1–PO12 and PSOs using 0–3 strength values.
  - Direct + Indirect integration — 80% direct (CIE/SEE) + 20% indirect (Course Exit Survey).
  - Attainment run history with versioned JSON snapshots in `attainment_runs` table.

- **Multi-Dimensional Gap Detector** (`backend/app/analytics/gap_detector.py`)
  - CO severity classification: `ON_TARGET`, `MODERATE`, `HIGH`, `CRITICAL`.
  - Question-level failure detection (< 50% pass rate threshold).
  - CIE vs SEE component disparity detection (grade inflation / terminal difficulty spikes).
  - Student intervention targeting with explainable evidence.

- **Bloom's Taxonomy Recommendation Engine** (`backend/app/services/recommendation_service.py`)
  - Deterministic pedagogical rules mapped to all six Bloom's cognitive levels.
  - 100% offline — zero external API or LLM calls.
  - Output includes teaching action, practice tasks, and diagnostic test suggestions.

- **FastAPI REST API** (`backend/app/routers/`)
  - 16 fully documented routers with Pydantic v2 schema validation.
  - JWT token lifecycle (issue, validate, revoke via blacklist).
  - Argon2id password hashing via `passlib`.
  - Role-Based Access Control: `SUPER_ADMIN` > `HOD` > `FACULTY` > `STUDENT`.
  - Students enforced to 403 Forbidden on all mutation endpoints.

- **Assessment Import Service** (`backend/app/services/import_service.py`)
  - CSV and Excel parsing with row-level error reporting.
  - Validations: negative marks, marks > max marks, duplicate USNs, missing required columns.

- **Accreditation Report Service** (`backend/app/services/report_service.py`)
  - ReportLab PDF — NBA/NAAC formatted Course Outcome Attainment report with signatories.
  - openpyxl Excel — Multi-tab workbook with CO results, PO mapping, question analysis, student data.

- **SQLAlchemy ORM Models** (`backend/app/models/`)
  - 29 relational tables covering academic hierarchy, assessments, attainment runs, interventions, and audit logs.
  - Alembic migration: `c96a4b48eb1a_initial_obe_schema.py`

- **CLI Bootstrap & Demo Seeder** (`backend/app/cli/`)
  - Idempotent seeder generating 4 role-based users, 3 courses, 3 offerings, 12 assessments, 288+ student marks.

### Added — Frontend

- **React + TypeScript SPA** (`frontend/src/`)
  - 20 fully wired, responsive pages (React Router v6, Tailwind CSS v4).
  - JWT auth via Axios interceptor with automatic token refresh.
  - AuthContext with role-based route guards.

- **Live OBE Dashboard** (`DashboardPage.tsx`)
  - Real-time KPI cards: total courses, average attainment, students at risk, CQI actions.
  - CO severity distribution bar chart (Recharts).
  - PO attainment heatmap matrix.
  - Top 3 underperforming COs with Bloom's level tags.

- **Courses & Outcomes Management**
  - Course catalog with department, semester, credits, and code.
  - "+ Add Course" modal with live POST.
  - Course Outcome CRUD with Bloom's taxonomy tagging and target % configuration.
  - CO-PO Mapping interactive matrix (0–3 strength values, batch save).

- **Assessment & Marks Workflow**
  - Assessment creation with max marks and type (CIE/SEE).
  - Question blueprint definition with per-question CO mapping.
  - Batch marks import: CSV preview table, row-level validation, commit.
  - Sample CSV template download.

- **Analytics Pages**
  - Attainment Calculation Center — run engine, view CO results, PO mapping results.
  - Gap Analysis Explorer — underperforming CO table, weak question table, CIE-SEE disparity table.
  - AI Recommendations — Bloom's-aligned pedagogical advice cards with CO context.

- **CQI Remedial Workflow** (`InterventionsPage.tsx`)
  - Create remedial action plan modal.
  - Record reassessment results (pre/post %) with live Δ improvement calculation.
  - Effectiveness rating display.

- **Accreditation Exports** (`ReportsPage.tsx`)
  - Offering selector dropdown.
  - Download buttons for `/api/reports/offerings/{id}/pdf` and `/excel`.
  - Live report preview table.

- **Admin Pages**
  - Student Directory with USN search.
  - User Roles & Access management.
  - Institutions & Departments hierarchy.
  - Academic Calendar.
  - Operational Audit Logs.

### Added — DevOps & Testing

- **Pytest Test Suite** — 34 tests, 100% pass rate:
  - `test_calculations.py` — 12 unit tests for calculation engine
  - `test_auth_rbac.py` — 6 security tests including student 403 enforcement
  - `test_api_endpoints.py` — 8 API integration tests
  - `test_import_validation.py` — 6 CSV/Excel validation tests
  - `test_e2e_acceptance.py` — 16-step full vertical slice acceptance test

- **Live 14-Stage E2E Verification** (`verify_live_e2e.py`)
  - Health → Auth → Course → Offering → Enrollment → CO → CO-PO Map → Assessment → Marks → Attainment → Gaps → Recommendations → Intervention → Report

- **Docker Compose** — Multi-container PostgreSQL + FastAPI + React stack.

- **PowerShell Runner Scripts** (`scripts/`)
  - `run_backend.ps1`, `run_frontend.ps1`, `run_tests.ps1`, `seed_demo_data.ps1`

- **Documentation** (`docs/`)
  - `ARCHITECTURE.md` — System design and component interaction diagrams.
  - `ER_DIAGRAM.md` — Complete entity-relationship diagram in Mermaid.
  - `OBE_CALCULATION_GUIDE.md` — Mathematical formulas, rubrics, and worked examples.

### Security

- All passwords hashed with Argon2id (memory-hard, side-channel resistant).
- JWT tokens include `exp`, `iat`, `sub`, and `role` claims.
- Backend token blacklist for logout invalidation.
- Role dependency injection (`require_roles()`) enforced at every router function.
- `.env` excluded from version control; `.env.example` provided as template.
- SQLite database (`co_attain.db`) excluded from version control via `.gitignore`.
