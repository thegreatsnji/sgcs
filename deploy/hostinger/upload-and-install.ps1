# Upload SGCS from this PC to VPS and run install (requires OpenSSH client).
# Usage:
#   cd C:\PROJECTS\SGCS
#   .\deploy\hostinger\upload-and-install.ps1
param(
  [string]$VpsHost = "148.230.113.108",
  [string]$VpsUser = "root",
  [string]$RemoteDir = "/opt/sgcs"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

Write-Host "Creating remote directory..."
ssh "${VpsUser}@${VpsHost}" "mkdir -p $RemoteDir"

Write-Host "Uploading project (excluding node_modules, .git, volumes)..."
# tar via ssh is faster than scp -r on Windows if tar available
Push-Location $ProjectRoot
tar --exclude=node_modules --exclude=.git --exclude=frontend/node_modules --exclude=backend/__pycache__ -czf - . |
  ssh "${VpsUser}@${VpsHost}" "tar -xzf - -C $RemoteDir"
Pop-Location

Write-Host "Running vps-install.sh on server..."
ssh "${VpsUser}@${VpsHost}" "cd $RemoteDir && bash deploy/hostinger/vps-install.sh"

Write-Host "Done. Open http://${VpsHost}/"
