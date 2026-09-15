$ErrorActionPreference = "Stop"

$PackageUrl = "https://github.com/BlackFoxGroup/smart-support-bot/raw/main/downloads/smart-support-suite-v2.3.zip"
$InstallDir = Join-Path $env:LOCALAPPDATA "SmartSupport"
$TempDir = Join-Path $env:TEMP ("smart-support-" + [guid]::NewGuid())
$ZipPath = Join-Path $TempDir "smart-support-suite.zip"

function Read-Required([string]$Prompt, [string]$Default = "") {
    $value = Read-Host $Prompt
    if (-not $value) { $value = $Default }
    if (-not $value) { throw "$Prompt is required." }
    return $value
}

function Read-PlainSecret([string]$Prompt) {
    $secure = Read-Host $Prompt -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

try {
    Write-Host "Downloading Smart Support..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri $PackageUrl -OutFile $ZipPath
    Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force

    $SourceDir = Join-Path $TempDir "smart-support-suite-v2.3"
    if (-not (Test-Path (Join-Path $SourceDir "requirements.txt"))) {
        throw "The downloaded package is invalid."
    }

    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "Saving Expert on this computer..." -ForegroundColor Cyan
    & robocopy $SourceDir $InstallDir /E /XD data .venv downloads tests /XF .env *.session *.pyc /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -gt 7) { throw "Copying Expert failed." }

    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $Launcher) {
        throw "Python 3.11 or newer is required. Install Python and run this command again."
    }
    $VenvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
    if (-not (Test-Path $VenvPython)) {
        Write-Host "Preparing Expert for the first run..." -ForegroundColor Cyan
        & py -3 -m venv (Join-Path $InstallDir ".venv")
        if ($LASTEXITCODE) { throw "Creating the Python environment failed." }
    }
    & $VenvPython -m pip install -U pip --quiet
    if ($LASTEXITCODE) { throw "Updating pip failed." }
    & $VenvPython -m pip install -r (Join-Path $InstallDir "requirements.txt") --quiet
    if ($LASTEXITCODE) { throw "Installing Python packages failed." }

    Write-Host "Enter the Linux server details." -ForegroundColor Yellow
    $HostName = Read-Required "Server IP or host"
    $Port = Read-Required "SSH port [22]" "22"
    $UserName = Read-Required "SSH user [root]" "root"
    $Password = Read-PlainSecret "SSH password"
    $BotToken = Read-PlainSecret "Telegram bot token"
    if (-not $Password -or -not $BotToken) { throw "SSH password and Telegram token are required." }
    $BotMode = (Read-Host "Bot mode: polling or webhook [polling]").Trim().ToLower()
    if (-not $BotMode) { $BotMode = "polling" }
    if ($BotMode -eq "hook") { $BotMode = "webhook" }
    if ($BotMode -notin @("polling", "webhook")) { throw "Bot mode must be polling or webhook." }
    $WebhookUrl = ""
    $WebhookPort = "8080"
    if ($BotMode -eq "webhook") {
        $WebhookUrl = Read-Required "Public HTTPS base URL"
        $WebhookPort = Read-Required "Internal webhook port [8080]" "8080"
    }

    $env:SS_HOST = $HostName
    $env:SS_PORT = $Port
    $env:SS_USER = $UserName
    $env:SS_PASSWORD = $Password
    $env:SS_BOT_TOKEN = $BotToken
    $env:SS_BOT_MODE = $BotMode
    $env:SS_WEBHOOK_URL = $WebhookUrl
    $env:SS_WEBHOOK_PORT = $WebhookPort
    $env:SS_INSTALL_DIR = $InstallDir
    $env:MANAGER_CONFIG_DIR = Join-Path $InstallDir "data"

    $Installer = @'
import os
from pathlib import Path

from src.knowledge.source_catalog.sftp_conn import save_sftp_settings
from src.manager.install_bot import activate_bot_and_expert, install_expert, install_telegram_bot

common = {
    "host": os.environ["SS_HOST"],
    "port": os.environ["SS_PORT"],
    "username": os.environ["SS_USER"],
    "password": os.environ["SS_PASSWORD"],
}
root = os.environ["SS_INSTALL_DIR"]

print("1/3 Installing bot...")
result = install_telegram_bot(
    local_path=root,
    bot_token=os.environ["SS_BOT_TOKEN"],
    bot_mode=os.environ["SS_BOT_MODE"],
    webhook_url=os.environ["SS_WEBHOOK_URL"],
    webhook_port=os.environ["SS_WEBHOOK_PORT"],
    **common,
)
if not result.get("ok"):
    raise RuntimeError(result.get("error") or "Bot installation failed")

print("2/3 Installing Expert...")
result = install_expert(local_path=root, **common)
if not result.get("ok"):
    raise RuntimeError(result.get("error") or "Expert installation failed")

print("3/3 Activating bot and Expert...")
result = activate_bot_and_expert(**common)
if not result.get("ok"):
    raise RuntimeError(result.get("error") or "Activation failed")

save_sftp_settings(
    Path(root) / "data",
    {
        "host": common["host"],
        "port": common["port"],
        "username": common["username"],
        "auth_method": "password",
        "remote_bot_root": "/opt/smart-support",
        "remote_media_path": "/opt/smart-support/products",
        "timeout": "30",
    },
    password=common["password"],
)
'@

    Push-Location $InstallDir
    try {
        & $VenvPython -c $Installer
        if ($LASTEXITCODE) { throw "Server installation failed." }
    }
    finally {
        Pop-Location
    }

    Remove-Item Env:SS_PASSWORD, Env:SS_BOT_TOKEN -ErrorAction SilentlyContinue
    Write-Host "Installation finished. Starting Expert..." -ForegroundColor Green
    $env:BOT_ROOT = $InstallDir
    $env:MANAGER_NAME = "Smart Support Manager"
    $env:MANAGER_VERSION = "2.3"
    $env:BOT_VERSION = "2.3"
    $env:MANAGER_PORT = "8766"
    $env:MANAGER_DESKTOP_SESSION = "1"
    $VenvPythonw = Join-Path $InstallDir ".venv\Scripts\pythonw.exe"
    Start-Process -FilePath $VenvPythonw -ArgumentList "-m", "src.manager" -WorkingDirectory $InstallDir -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Start-Process "http://127.0.0.1:8766"
    Write-Host "The bot is ready. Open it in Telegram and send /start." -ForegroundColor Green
}
catch {
    Write-Host ("Installation failed: " + $_.Exception.Message) -ForegroundColor Red
    throw
}
finally {
    Remove-Item Env:SS_PASSWORD, Env:SS_BOT_TOKEN -ErrorAction SilentlyContinue
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}
