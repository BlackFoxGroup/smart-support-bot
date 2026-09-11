@echo off
setlocal
cd /d "%~dp0"
start "Smart Support Manager" /min py -3 -m src.manager
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
start "" "http://127.0.0.1:8765"
endlocal
