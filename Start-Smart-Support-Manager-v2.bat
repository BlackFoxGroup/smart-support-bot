@echo off
setlocal
cd /d "%~dp0"
set MANAGER_NAME=Smart Support Manager v2
set MANAGER_PORT=8766
start "Smart Support Manager v2" /min py -3 -m src.manager
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
start "" "http://127.0.0.1:8766"
endlocal
