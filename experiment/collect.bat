@echo off
rem Copies the results from the lab share to the project data folder (see lab\collect.ps1). Add -Watch to keep copying.
powershell -ExecutionPolicy ByPass -File "%~dp0lab\collect.ps1" %*
pause
