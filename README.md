# CO-ATTAIN PRO AI
## Course Outcome Attainment Analytics & Gap Detection System
**Outcome-Based Education (OBE) • NBA / NAAC Accreditation Compliance • UN SDG 4 (Quality Education)**

CO-ATTAIN PRO AI is a professional-grade, end-to-end academic analytics platform for engineering and higher education institutions. It automates Course Outcome (CO), Program Outcome (PO), and Program Specific Outcome (PSO) attainment calculations, multi-dimensional learning gap diagnostics, Bloom's Taxonomy pedagogical recommendations, Continuous Quality Improvement (CQI) remedial loops, and official accreditation report exports.

---

## 1. Features Implemented

- **Authentic Database-Backed Analytics**: Zero hardcoded mock numbers. All dashboard KPIs, bar charts, and heatmaps are calculated live from stored student marks.
- **Pure Academic Calculation Engine**:
  - **Method A (Student Threshold Method)**: Calculates percentage of eligible students scoring $\ge$ threshold marks on each mapped question.
  - **Method B (Normalized Score Method)**: Sum of marks obtained divided by sum of maximum marks.
  - **CO-PO Mapping Matrix**: Weighted contribution to Washington Accord PO1–PO12 and PSOs based on 0–3 mapping strengths.
  - **Direct + Indirect Combination**: Integrates continuous evaluation exams (CIE), terminal exams (SEE), and Course Exit Surveys.
- **Multi-Dimensional Gap Detection**:
  - Identifies underperforming COs and flags severity (`ON_TARGET`, `MODERATE`, `HIGH`, `CRITICAL`).
  - Detects high-failure-rate exam questions ($< 50\%$ success rate).
  - Flags evaluation component disparities (e.g. CIE vs SEE grade inflation or terminal difficulty spikes).
  - Identifies students requiring academic intervention with explainable evidence.
- **Bloom's Cognitive Taxonomy Recommendation Engine**:
  - Deterministic pedagogical rules mapping Bloom's levels (Remember, Understand, Apply, Analyze, Evaluate, Create) to teaching actions, practice tasks, and diagnostic tests. Operates 100% offline with zero external API dependencies.
- **Continuous Quality Improvement (CQI) Remedial Workflow**:
  - Full lifecycle: Gap Detected $\to$ Action Plan $\to$ Remedial Teaching $\to$ Post-Remedial Exam $\to$ Verified Improvement Calculation ($\text{Post} - \text{Pre}$) $\to$ Effectiveness Rating.
- **Assessment Import & Data Validation Center**:
  - CSV and Excel parsing with row-level error reporting (negative marks, scores exceeding max marks, duplicate USNs).
  - Downloadable sample templates for student rosters and assessment question blueprints.
- **Official Accreditation Reports & Exports**:
  - Downloadable NBA/NAAC Course Outcome Attainment PDF reports with signatories.
  - Multi-tab Excel workbook exports.
- **Enterprise Security & Role-Based Access Control (RBAC)**:
  - Argon2id password hashing, JWT token lifecycle, and role enforcement (`SUPER_ADMIN`, `HOD`, `FACULTY`, `STUDENT`).

---

## 2. Directory Structure

```
COPO/
├── backend/
│   ├── app/
│   │   ├── analytics/       # Pure calculation engine & gap detector
│   │   ├── cli/             # Admin bootstrap & demo data seeder
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── routers/         # Modular FastAPI routers
│   │   ├── schemas/         # Pydantic v2 validation models
│   │   ├── services/        # Auth, reportlab PDF, excel, import services
│   │   ├── config.py        # Settings & environment configuration
│   │   ├── database.py      # Engine, sessionmaker, SQLite PRAGMA
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Pytest automated test suites (33 passed)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios client with JWT interceptor
│   │   ├── components/      # Sidebar, Navbar, AppLayout
│   │   ├── context/         # AuthContext & permissions
│   │   ├── pages/           # 14 complete responsive pages
│   │   ├── App.tsx          # Router configuration
│   │   └── index.css        # Tailwind CSS v4 design tokens
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Architecture, ER diagram, OBE formulas
├── scripts/                 # PowerShell runner scripts
├── docker-compose.yml       # PostgreSQL, Backend, Frontend stack
├── pytest.ini               # Test configuration
├── .env.example             # Environment template
└── README.md
```

---

## 3. Quick Start on Windows PowerShell

### Prerequisites
- Python 3.12+ (tested on Python 3.13)
- Node.js 18+ (tested on Node.js v24)
- Git (optional)

### Step 1: Clone or Navigate to Directory
```powershell
Set-Location -Path "d:\MINNI PROJECT\COPO"
```

### Step 2: Set Up Python Virtual Environment & Dependencies
```powershell
py -m venv .venv
.\.venv\Scripts\pip.exe install -r backend/requirements.txt
```

### Step 3: Run Database Migrations & Seed Realistic OBE Demo Data
```powershell
# Apply Alembic schema migrations
Set-Location -Path "backend"
..\.venv\Scripts\alembic.exe upgrade head
Set-Location -Path ".."

# Seed realistic demo data (4 users, 3 courses, 12 assessments, 288+ marks)
.\.venv\Scripts\python.exe -m backend.app.cli.seed
```

### Step 4: Install Frontend Dependencies
```powershell
Set-Location -Path "frontend"
npm install --legacy-peer-deps
Set-Location -Path ".."
```

### Step 5: Start the Application

**Terminal 1 — Backend API Server:**
```powershell
.\scripts\run_backend.ps1
```
*Backend runs on: `http://localhost:8000`*
*Interactive OpenAPI Docs: `http://localhost:8000/api/docs`*

**Terminal 2 — Frontend Dev Server:**
```powershell
.\scripts\run_frontend.ps1
```
*Frontend runs on: `http://localhost:5173`*

---

## 4. Demo Login Credentials

The deterministic seeder generates four role-based accounts:

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@apex.edu` | `Admin@12345` | Global system control, users, institutions |
| **HOD (Dept Head)** | `hod.cse@apex.edu` | `Hod@12345` | Department curriculum, faculty, offerings |
| **Faculty Member** | `sarah.jenkins@apex.edu` | `Faculty@12345` | Course outcomes, assessments, marks, calculation |
| **Student** | `1ap22cs001@apex.edu` | `Student@12345` | Restricted personal outcome progress |

*(The login screen also provides 1-click demo login buttons for instant access).*

---

## 5. Automated Test Suite Results

Run all 34 automated unit, integration, and security tests using:
```powershell
.\scripts\run_tests.ps1
```
or directly:
```powershell
.\.venv\Scripts\pytest.exe -v
```

```
backend/tests/test_calculations.py ...... (12 passed)
backend/tests/test_auth_rbac.py ......    (6 passed, including student 403 enforcement)
backend/tests/test_api_endpoints.py ........ (8 passed)
backend/tests/test_import_validation.py ...... (6 passed)
backend/tests/test_e2e_acceptance.py .   (1 passed - 16-step vertical slice)
backend/tests/test_rbac_matrix.py .      (1 passed)

======================= 34 passed in 4.10s =======================
```

### Full 14-Stage Live E2E Workflow Verification
Verify the complete live end-to-end API lifecycle against a running server:
```powershell
.\.venv\Scripts\python.exe verify_live_e2e.py
```
*Executes: Health $\to$ Auth $\to$ Course Creation $\to$ Offering $\to$ Enrollment $\to$ CO Definition $\to$ CO-PO Mapping $\to$ Assessment & Blueprint $\to$ Marks Import $\to$ Attainment Calculation $\to$ Gap Detection $\to$ Recommendations $\to$ CQI Intervention $\to$ Reassessment & Improvement Delta $\to$ Report Generation (PDF/Excel).*

---

## 6. Local URLs

- **Web Application Portal**: [http://localhost:5173](http://localhost:5173)
- **FastAPI REST API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc API Documentation**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)
- **Liveness Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)
- **Readiness Health Endpoint**: [http://localhost:8000/readiness](http://localhost:8000/readiness)

---

## 7. Production Build & Lint Verification

- **Automated Tests**: 34 / 34 passing in Pytest (`backend/tests/`)
- **Lint Check**: 0 errors with `oxlint` across 29 frontend files (`npm run lint`)
- **Type Check & Bundle**: Built cleanly in 593ms via `npm run build` (`tsc -b && vite build`)
- **Output**: Optimized bundle in `frontend/dist/`

---

## 8. Complete Application Page Sitemap

| Path | Name | Description | Role Access |
| :--- | :--- | :--- | :--- |
| `/login` | Authentication Portal | Secure Argon2id login with 1-click demo role switcher | Public |
| `/dashboard` | Live OBE Dashboard | Real-time CO/PO metrics, KPI cards, severity distribution | All Authenticated |
| `/semester-trends` | Semester Trends | Multi-semester attainment trajectory and target tracking | All Authenticated |
| `/outcomes/cos` | Course Outcomes | Bloom's taxonomy definition, target %, and CO CRUD | Faculty, HOD, Admin |
| `/outcomes/mapping` | CO-PO Mapping Matrix | Interactive 0-3 matrix for PO1-PO12 and PSOs | Faculty, HOD, Admin |
| `/courses` | Courses & Offerings | Course catalog, sections, and faculty assignments | Faculty, HOD, Admin |
| `/assessments` | Examinations & Tests | CIE/SEE exams, max marks, and question blueprints | Faculty, HOD, Admin |
| `/marks/import` | Spreadsheet Import | Excel/CSV parser with row-level validation & error reporting | Faculty, HOD, Admin |
| `/attainment` | Calculation Center | Multi-method engine (Method A & B) with real-time run trigger | Faculty, HOD, Admin |
| `/gaps` | Gap Analysis Explorer | Underperforming COs, weak questions, CIE-SEE disparities | Faculty, HOD, Admin |
| `/recommendations` | AI Recommendations | Bloom's cognitive taxonomy targeted pedagogical advice | Faculty, HOD, Admin |
| `/interventions` | Continuous Quality (CQI) | Remedial action plans, reassessment entry, verified delta | Faculty, HOD, Admin |
| `/reports` | Accreditation Exports | Official NBA/NAAC Course Outcome PDF & Excel generation | Faculty, HOD, Admin |
| `/students` | Student Directory | Student rosters, USN search, cohort enrollment status | Faculty, HOD, Admin |
| `/students/:id` | Student Record | Student performance history, assessment breakdown & chart | Faculty, HOD, Admin |
| `/my-performance` | Student Portal | Student's own academic progress & question performance | Student |
| `/institutions` | Institutions & Depts | Institutional hierarchy and academic units | Super Admin |
| `/calendar` | Academic Calendar | Semesters, academic year periods, active terms | Super Admin |
| `/users` | User Roles & Access | Account creation, role delegation, active statuses | Super Admin |
| `/audit` | Operational Audit Logs | Cryptographic event logs, import jobs, and system trace | Super Admin, HOD |
| `/profile` | Profile & Security | Account details and password change endpoint | All Authenticated |
| `/methodology` | OBE Methodology | Mathematical documentation, formulas, and rubrics | All Authenticated |

---

## 9. Troubleshooting & FAQ for Windows PowerShell

### 1. `Execution of scripts is disabled on this system` (PSSecurityException)
If running `./scripts/run_backend.ps1` gives a script execution policy error, enable local script execution:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Port Already in Use (`Errno 10048` on port 8000 or 5173)
To find and stop processes holding port 8000 or 5173:
```powershell
Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | Select-Object OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### 3. Alembic Migrations
To inspect or re-apply database schema migrations:
```powershell
Set-Location -Path "backend"
..\.venv\Scripts\alembic.exe upgrade head
Set-Location -Path ".."
```

### 4. Database Reset (If needed for a clean demonstration slate)
To reset and re-seed the SQLite database with full realistic academic data:
```powershell
Remove-Item -Path "co_attain.db" -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m backend.app.cli.seed
```

### 5. Running the Pytest Suite
```powershell
.\.venv\Scripts\pytest.exe -v
```
