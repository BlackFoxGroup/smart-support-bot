@echo off
setlocal
cd /d "%~dp0"
set "BOT_ROOT=%~dp0"
set "MANAGER_CONFIG_DIR=%~dp0data"
set "MANAGER_NAME=Smart Support Manager"
set "MANAGER_VERSION=2.1"
set "BOT_VERSION=2.0"
set "MANAGER_PORT=8766"
start "Smart Support Manager" /min py -3 -m src.manager
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
start "" "http://127.0.0.1:8766"
endlocal
