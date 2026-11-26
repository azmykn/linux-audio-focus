#!/usr/bin/env bash
set -euo pipefail

APP_NAME="linux-audio-focus"
BIN_DIR="${HOME}/.local/bin"
SYSTEMD_DIR="${HOME}/.config/systemd/user"

echo "==> Uninstalling ${APP_NAME}..."

systemctl --user stop "${APP_NAME}.service" 2>/dev/null || true
systemctl --user disable "${APP_NAME}.service" 2>/dev/null || true

rm -f "${SYSTEMD_DIR}/${APP_NAME}.service"
rm -f "${BIN_DIR}/${APP_NAME}"

systemctl --user daemon-reload
echo "==> ${APP_NAME} has been uninstalled successfully."
