$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv install nahi mila. Pehle dependencies install/run setup check karein."
    exit 1
}

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared install nahi mila."
    Write-Host "Free install: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    Write-Host "Install ke baad is script ko dobara run karein."
    exit 1
}

Write-Host "Starting VidQuery AI locally on http://127.0.0.1:5000 ..."
$appProcess = Start-Process `
    -FilePath "uv" `
    -ArgumentList @("run", "python", "app.py") `
    -WorkingDirectory $projectRoot `
    -PassThru `
    -WindowStyle Hidden

try {
    Start-Sleep -Seconds 3
    Write-Host ""
    Write-Host "Cloudflare free public URL generate ho raha hai..."
    Write-Host "Terminal me jo https://*.trycloudflare.com URL aaye, wahi users ko share karein."
    Write-Host "Is window ko band karte hi app/tunnel stop ho jayega."
    Write-Host ""
    cloudflared tunnel --url http://127.0.0.1:5000
}
finally {
    if ($appProcess -and -not $appProcess.HasExited) {
        Stop-Process -Id $appProcess.Id -Force
    }
}
