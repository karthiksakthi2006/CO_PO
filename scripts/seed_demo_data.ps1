# Seeds deterministic realistic OBE demo data
$ErrorActionPreference = "Stop"
Write-Host "Seeding realistic OBE academic records and attainment data..." -ForegroundColor Cyan

.\.venv\Scripts\python.exe -m backend.app.cli.seed
