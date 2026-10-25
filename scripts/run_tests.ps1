# Runs all backend pytest test suites
$ErrorActionPreference = "Stop"
Write-Host "Running automated calculation and API test suites..." -ForegroundColor Cyan

.\.venv\Scripts\pytest.exe -v
