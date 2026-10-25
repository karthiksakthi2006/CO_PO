# Starts the Vite React frontend dev server
$ErrorActionPreference = "Stop"
Write-Host "Starting CO-ATTAIN PRO AI Frontend on http://localhost:5173..." -ForegroundColor Cyan

Set-Location -Path "frontend"
npm run dev
