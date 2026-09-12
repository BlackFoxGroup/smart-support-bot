@echo off
setlocal
cd /d "%~dp0"
set "BOT_ROOT=%~dp0"
set "MANAGER_CONFIG_DIR=%~dp0data"
set "MANAGER_NAME=Smart Support Manager"
set "MANAGER_VERSION=2.1"
set "BOT_VERSION=2.0"
set "MANAGER_PORT=8766"
set "MANAGER_DESKTOP_SESSION=1"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv || goto :error
  ".venv\Scripts\python.exe" -m pip install -U pip || goto :error
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
start "" ".venv\Scripts\pythonw.exe" -m src.manager
powershell -NoProfile -Command "Start-Sleep -Seconds 2"
start "" "http://127.0.0.1:8766"
endlocal
exit /b 0

:error
echo Smart Support Manager setup failed.
pause
exit /b 1
