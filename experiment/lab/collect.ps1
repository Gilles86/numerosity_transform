# Copies the results from the lab share (results_dir) to the project's data folder (archive_dir), both set in
# lab\lab_config.yml. Only adds and updates files at the destination, never deletes.
#     collect.bat           copy once (e.g. right after a session)
#     collect.bat -Watch    keep copying every minute during a session; stop with Ctrl+C
param([switch]$Watch)
$ErrorActionPreference = 'Stop'
$config = Get-Content (Join-Path $PSScriptRoot 'lab_config.yml') -Raw
function Get-Setting($name) {
    if ($config -match "(?m)^$name\s*:\s*'([^']+)'") { return $Matches[1] }
    throw "$name not found in lab_config.yml"
}
$source = Get-Setting 'results_dir'
$target = Get-Setting 'archive_dir'
if (-not (Test-Path $source)) { throw "Results folder not found: $source" }

do {
    robocopy $source $target /E /XO /R:2 /W:5 /NFL /NDL /NP /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { Write-Warning "robocopy failed (exit code $LASTEXITCODE)" }
    else {
        $n = (Get-ChildItem $target -Recurse -File).Count
        Write-Host "$(Get-Date -Format HH:mm:ss)  copied to $target ($n files)"
    }
    if ($Watch) { Start-Sleep -Seconds 60 }
} while ($Watch)
