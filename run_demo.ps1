[CmdletBinding()]
param(
    [switch]$SkipPipeline,
    [int]$Port = 8501,
    [switch]$Headless,
    [ValidateSet('amazon', 'yelp')]
    [string]$Dataset = 'amazon',
    [string]$InputPath,
    [int]$MaxRows,
    [string]$DateStart,
    [string]$DateEnd,
    [string]$BusinessIdsFile
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path (Join-Path $projectRoot '..')
$python = Join-Path $workspaceRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
    throw "Could not find venv python at: $python`nExpected venv at: $(Join-Path $workspaceRoot '.venv')"
}

Set-Location $projectRoot

Write-Host "Using python: $python" -ForegroundColor Cyan

if (-not $SkipPipeline) {
    Write-Host 'Running pipeline (main.py)...' -ForegroundColor Cyan

    $mainArgs = @(
        (Join-Path $projectRoot 'main.py'),
        '--dataset',
        $Dataset
    )

    if ($InputPath) {
        $mainArgs += @('--input', $InputPath)
    }
    if ($MaxRows -gt 0) {
        $mainArgs += @('--max-rows', "$MaxRows")
    }
    if ($DateStart) {
        $mainArgs += @('--date-start', $DateStart)
    }
    if ($DateEnd) {
        $mainArgs += @('--date-end', $DateEnd)
    }
    if ($BusinessIdsFile) {
        $mainArgs += @('--business-ids-file', $BusinessIdsFile)
    }

    & $python @mainArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Pipeline failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Starting Streamlit on port $Port..." -ForegroundColor Cyan

$streamlitArgs = @(
    'run',
    (Join-Path $projectRoot 'app.py'),
    '--server.port',
    "$Port"
)

if ($Headless) {
    $streamlitArgs += @('--server.headless', 'true')
}

& $python -m streamlit @streamlitArgs
