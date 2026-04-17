param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$ffmpegPath = Join-Path $projectRoot "vendor\ffmpeg.exe"

if (-not (Test-Path $ffmpegPath)) {
    Write-Error "Missing vendor\ffmpeg.exe. Put ffmpeg.exe in the vendor folder before building."
}

Push-Location $projectRoot
try {
    & $Python -m py_compile app.py
    & pyinstaller HeicMovConverter.spec --clean
}
finally {
    Pop-Location
}
