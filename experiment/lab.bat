@echo off
rem Starts the lab experiment (lab.py) with the Python in lab_python. Double-click it, type "lab" in this folder,
rem or use it as the command in Lab Control.
set "PY="
for /d %%d in ("%~dp0lab_python\cpython-3.10*") do set "PY=%%d\python.exe"
if not defined PY (
    echo lab_python not found: run lab\setup_lab_env.ps1 first.
    pause
    exit /b 1
)
echo Python: %PY%
"%PY%" "%~dp0lab.py" %*
