# backend\run.ps1
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "Starting FastAPI server..."
Write-Host "cwd: $(Get-Location)"
Write-Host "python: $(& $py -c 'import sys; print(sys.executable)')"

& $py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
