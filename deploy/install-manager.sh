#!/usr/bin/env bash
# Install Smart Support Manager as a local-only Linux service.
set -euo pipefail

INSTALL_DIR="${MANAGER_INSTALL_DIR:-/opt/smart-support}"
REPO_URL="${MANAGER_REPO_URL:-https://github.com/BlackFoxGroup/smart-support-bot.git}"
SERVICE_NAME="smart-support-manager"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer as root." >&2
  exit 1
fi

apt-get update -qq
apt-get install -y git python3 python3-venv python3-pip

if [[ -d "${INSTALL_DIR}/.git" ]]; then
  git -C "${INSTALL_DIR}" pull --ff-only
elif [[ -e "${INSTALL_DIR}" ]] && [[ -n "$(ls -A "${INSTALL_DIR}" 2>/dev/null)" ]]; then
  echo "${INSTALL_DIR} exists and is not a git checkout; refusing to overwrite it." >&2
  exit 1
else
  rm -rf "${INSTALL_DIR}"
  git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
fi

python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install -U pip
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"
install -d -m 700 "${INSTALL_DIR}/data"

cat >"/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Smart Support Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
Environment="BOT_ROOT=${INSTALL_DIR}"
Environment="BOT_REMOTE_ROOT=${INSTALL_DIR}"
Environment="BOT_SERVICE_NAME=smart-support-bot.service"
Environment="MANAGER_LOCAL_BOT=1"
Environment="MANAGER_NAME=Smart Support Manager"
Environment="MANAGER_VERSION=2.3"
Environment="BOT_VERSION=2.3"
Environment="MANAGER_PORT=8766"
Environment="MANAGER_CONFIG_DIR=${INSTALL_DIR}/data"
ExecStart=${INSTALL_DIR}/.venv/bin/python -m src.manager
Restart=on-failure
RestartSec=5
UMask=0077

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

echo "Smart Support Manager 2.3 is listening on 127.0.0.1:8766."
echo "Open a tunnel: ssh -L 8766:127.0.0.1:8766 USER@SERVER"
