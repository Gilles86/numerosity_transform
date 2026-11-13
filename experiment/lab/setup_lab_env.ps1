# Builds a self-contained Python (3.10 + PsychoPy + exptools2) inside experiment\lab_python, for the BLU lab clients.
# Follows the "standalone Python" route of the Econ Lab intranet (Usage Guides > Python Experiments): the folder has
# its own python.exe and does not depend on anything installed on the clients, so it can be copied to N:\expfiles.
#
# Run ONCE on the ExpMaster PC (or any Windows 10/11 x64 PC), in PowerShell, from the experiment folder:
#     powershell -ExecutionPolicy ByPass -File lab\setup_lab_env.ps1
# Then copy the whole experiment folder to N:\expfiles\<shortname>\numerosity_transform\experiment (see lab\README.md).

$ErrorActionPreference = 'Stop'
$experiment = Split-Path -Parent $PSScriptRoot
$target = Join-Path $experiment 'lab_python'

# 1. uv (only needed here, not on the clients)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host 'Installing uv ...'
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

# 2. A relocatable ("standalone") Python 3.10 inside the experiment folder
Write-Host "Installing Python 3.10 into $target ..."
uv python install 3.10 --install-dir $target
$python = Get-ChildItem $target -Recurse -Filter python.exe | Where-Object { $_.DirectoryName -notmatch 'Scripts|venv' } |
    Select-Object -First 1 -ExpandProperty FullName
if (-not $python) { throw "No python.exe found in $target" }

# 3. The exact package versions of uv.lock (exptools2 from a GitHub zip, so git is not needed)
Write-Host 'Installing PsychoPy, exptools2 and dependencies (takes a few minutes) ...'
uv pip install --python $python --break-system-packages -r (Join-Path $PSScriptRoot 'requirements_lab.txt')

# 4. Check that everything imports
& $python -c "import psychopy, exptools2, yaml; print('OK: PsychoPy', psychopy.__version__)"
if ($LASTEXITCODE -ne 0) { throw 'Import check failed' }

$relative = $python.Substring($experiment.Length + 1)
Write-Host ''
Write-Host 'Done. In LabControl, create a Custom Experiment of type "Python" with:'
Write-Host "  Python executable:  C:\ExpFiles\<shortname>\numerosity_transform\experiment\$relative"
Write-Host '  Script:             C:\ExpFiles\<shortname>\numerosity_transform\experiment\lab.py'
Write-Host "Test here first:      & '$python' lab.py"
