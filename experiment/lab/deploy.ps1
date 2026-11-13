# Update the code from GitHub and copy the experiment to the lab share, from which Lab Control mirrors it to the clients.
# Run on the ExpMaster PC, in PowerShell, from the experiment folder of the git clone:
#     powershell -ExecutionPolicy ByPass -File lab\deploy.ps1
# The first copy includes lab_python and takes ~15 minutes; later copies only transfer changed files.

$ErrorActionPreference = 'Stop'
$experiment = Split-Path -Parent $PSScriptRoot
$target = "N:\expfiles\$env:USERNAME\numerosity_transform\experiment"

Write-Host 'Updating the code (git pull) ...'
git -C $experiment pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'git pull failed (local changes? run "git status" in the experiment folder)' }

if (-not (Test-Path (Join-Path $experiment 'lab_python'))) { throw 'lab_python missing: run lab\setup_lab_env.ps1 first' }

Write-Host "Copying to $target ..."
robocopy $experiment $target /MIR /XD logs logs_backup .venv __pycache__ /NFL /NDL /NP
if ($LASTEXITCODE -ge 8) { throw "robocopy failed (exit code $LASTEXITCODE)" }
Write-Host "Done. In Lab Control: tick 'Mirror Experiment Files' when starting the clients."
