@echo off
rem Updates the code (git pull) and copies the experiment to N:\expfiles\<shortname>\numerosity_transform\experiment.
powershell -ExecutionPolicy ByPass -File "%~dp0lab\deploy.ps1"
pause
