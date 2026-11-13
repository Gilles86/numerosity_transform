@echo off
rem Shows what every lab PC is doing (participant, session, version, phase). Add --test for test runs, --once for one look.
set "PY="
for /d %%d in ("%~dp0lab_python\cpython-3.10*") do set "PY=%%d\python.exe"
"%PY%" "%~dp0lab\status.py" %*
pause
