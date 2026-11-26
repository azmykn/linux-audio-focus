#!/usr/bin/env bash
set -euo pipefail

# Installer for linux-audio-focus

APP_NAME="linux-audio-focus"
BIN_DIR="${HOME}/.local/bin"
SYSTEMD_DIR="${HOME}/.config/systemd/user"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing ${APP_NAME}..."

# Check Python 3 and PyGObject
PYTHON_BIN="$(command -v /usr/bin/python3 || command -v python3)"
if [[ -z "${PYTHON_BIN}" ]]; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

if ! "${PYTHON_BIN}" -c "import gi; from gi.repository import Gio, GLib" >/dev/null 2>&1; then
    echo "Warning: PyGObject (python3-gi) might not be installed."
    echo "On Ubuntu/Debian, install with: sudo apt install python3-gi"
fi

# Create target directories
mkdir -p "${BIN_DIR}"
mkdir -p "${SYSTEMD_DIR}"

# Copy files
echo "==> Deploying script to ${BIN_DIR}/${APP_NAME}..."
cp "${SOURCE_DIR}/bin/linux-audio-focus.py" "${BIN_DIR}/${APP_NAME}"
chmod +x "${BIN_DIR}/${APP_NAME}"

echo "==> Deploying systemd service to ${SYSTEMD_DIR}/${APP_NAME}.service..."
cp "${SOURCE_DIR}/systemd/linux-audio-focus.service" "${SYSTEMD_DIR}/${APP_NAME}.service"

# Reload and enable service
echo "==> Enabling and starting user systemd service..."
systemctl --user daemon-reload
systemctl --user enable --now "${APP_NAME}.service"

echo "==> Installation complete! Service status:"
systemctl --user status "${APP_NAME}.service" --no-pager || true
