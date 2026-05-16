# Run this after closing Cursor terminals / stopping npm run dev and uvicorn
$nested = Join-Path $PSScriptRoot "malkar-enterprises-platform"
if (Test-Path $nested) {
    Remove-Item $nested -Recurse -Force
    Write-Host "Removed duplicate nested folder."
} else {
    Write-Host "No nested folder found — already clean."
}
