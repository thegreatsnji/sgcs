# SGCS — Um comando para testes (Docker)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

& npm run start:bg
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& npm run ready
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Verifique os logs: docker compose logs backend"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "=== SGCS pronto ==="
Write-Host "  UI:          http://localhost:5173"
Write-Host "  API:         http://localhost:8000/api/docs/"
Write-Host "  Login demo:  admin@sauvida.gw / Demo@2026!  (ver docs/DEMO_DATA.md)"
Write-Host "  Parar:       npm run stop"
