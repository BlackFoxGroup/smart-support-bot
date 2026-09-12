#!/usr/bin/env bash
# Install Smart Support Bot from a downloaded public package on Ubuntu.
set -euo pipefail

INSTALL_DIR="/opt/smart-support"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y python3 python3-venv python3-pip

echo "==> Preparing ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"

if [[ "${SOURCE_DIR}" != "${INSTALL_DIR}" ]]; then
  cp -a "${SOURCE_DIR}/." "${INSTALL_DIR}/"
fi

mkdir -p "${INSTALL_DIR}/data"
if [[ ! -f "${INSTALL_DIR}/.env" ]]; then
  cp "${INSTALL_DIR}/.env.example" "${INSTALL_DIR}/.env"
fi

echo "==> Creating Python virtualenv and installing dependencies"
cd "${INSTALL_DIR}"
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

echo "==> Preparing safety store"
mkdir -p /opt/smart-support-bot-safety/backups /opt/smart-support-bot-safety/staging

echo "==> Installing systemd units"
install -m 644 "${INSTALL_DIR}/deploy/smart-support-bot.service" /etc/systemd/system/smart-support-bot.service
install -m 644 "${INSTALL_DIR}/deploy/smart-support-bot-watchdog.service" /etc/systemd/system/smart-support-bot-watchdog.service
systemctl daemon-reload
if grep -Eq '^TELEGRAM_BOT_TOKEN=.+$' "${INSTALL_DIR}/.env" &&
   ! grep -Eq '^TELEGRAM_BOT_TOKEN=.*replace-' "${INSTALL_DIR}/.env"; then
  systemctl enable --now smart-support-bot.service
  systemctl enable --now smart-support-bot-watchdog.service
else
  echo "Bot services were installed but not started."
  echo "Edit ${INSTALL_DIR}/.env, then run:"
  echo "  systemctl enable --now smart-support-bot.service smart-support-bot-watchdog.service"
fi

echo "==> Done. Status:"
systemctl status smart-support-bot.service --no-pager || true
systemctl status smart-support-bot-watchdog.service --no-pager || true
