# Contributing to CO-ATTAIN PRO AI

Thank you for your interest in contributing to CO-ATTAIN PRO AI!

## Development Setup (Windows PowerShell)

```powershell
# 1. Clone the repository
git clone https://github.com/Kathirvel005/co-po-mini-project-.git
Set-Location -Path "co-po-mini-project-"

# 2. Create Python virtual environment and install backend dependencies
py -m venv .venv
.\.venv\Scripts\pip.exe install -r backend/requirements.txt

# 3. Apply Alembic migrations
Set-Location -Path "backend"
..\.venv\Scripts\alembic.exe upgrade head
Set-Location -Path ".."

# 4. Seed demo data
.\.venv\Scripts\python.exe -m backend.app.cli.seed

# 5. Install frontend dependencies
Set-Location -Path "frontend"
npm install --legacy-peer-deps
Set-Location -Path ".."
```

## Running Locally

**Terminal 1 — Backend (Port 8000):**
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend (Port 5173):**
```powershell
Set-Location -Path "frontend"
npm run dev
```

## Running Tests

```powershell
# All 34 automated tests
.\.venv\Scripts\pytest.exe -v

# Frontend type check + production build
Set-Location -Path "frontend"
npm run build

# Frontend lint
npm run lint
```

## Project Structure

```
backend/
  app/
    analytics/      # Attainment calculation engine & gap detector
    cli/            # Admin bootstrap & demo data seeder
    models/         # SQLAlchemy ORM models (29 tables)
    routers/        # FastAPI route handlers
    schemas/        # Pydantic v2 request/response schemas
    services/       # Auth, report generation, import, recommendations
  tests/            # Pytest test suites
frontend/
  src/
    api/            # Axios client with JWT interceptor
    components/     # Sidebar, Navbar, AppLayout
    context/        # AuthContext & role-based guards
    pages/          # 20 fully implemented pages
docs/               # Architecture, ER diagram, OBE formulas
scripts/            # PowerShell automation scripts
```

## Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use For |
|--------|---------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | Adding or updating tests |
| `refactor:` | Code restructure without behavior change |
| `chore:` | Build system, dependencies, config |
| `security:` | Security patches or hardening |

Examples:
```
feat(analytics): add CO-PO indirect attainment integration
fix(rbac): enforce student 403 on assessment mutation endpoints
docs: update README with PowerShell troubleshooting commands
test(calculations): add edge case for zero-mark submission
```

## Code Standards

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Pydantic v2, Alembic.
- **Frontend**: TypeScript strict mode, React 19, Tailwind CSS v4, Recharts.
- **Tests**: All new backend features must include pytest unit tests.
- **No mock data**: Dashboard, reports, and analytics must always read from the real database.
- **RBAC**: Every new router endpoint must declare its `require_roles()` dependency.
