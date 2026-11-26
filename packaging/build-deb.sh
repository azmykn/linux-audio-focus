#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PKG_NAME="linux-audio-focus"
PKG_VERSION="1.0.0"
PKG_ARCH="all"
DIST_DIR="${ROOT_DIR}/dist"
BUILD_DIR="${ROOT_DIR}/build/deb"

echo "==> Building Debian package for ${PKG_NAME} v${PKG_VERSION}..."

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/lib/systemd/user"
mkdir -p "${BUILD_DIR}/usr/lib/systemd/user-preset"
mkdir -p "${DIST_DIR}"

# 1. Install binary
cp "${ROOT_DIR}/bin/linux-audio-focus.py" "${BUILD_DIR}/usr/bin/${PKG_NAME}"
chmod 755 "${BUILD_DIR}/usr/bin/${PKG_NAME}"

# 2. Install systemd user service
cat << 'EOF' > "${BUILD_DIR}/usr/lib/systemd/user/${PKG_NAME}.service"
[Unit]
Description=Linux Audio Focus Manager (MPRIS)
Documentation=https://github.com/azmykn/linux-audio-focus
After=graphical-session.target sound.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/bin/linux-audio-focus
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
chmod 644 "${BUILD_DIR}/usr/lib/systemd/user/${PKG_NAME}.service"

# 3. User preset to enable automatically
echo "enable ${PKG_NAME}.service" > "${BUILD_DIR}/usr/lib/systemd/user-preset/90-${PKG_NAME}.preset"
chmod 644 "${BUILD_DIR}/usr/lib/systemd/user-preset/90-${PKG_NAME}.preset"

# 3b. Install desktop entry and application icon
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/icons/hicolor/512x512/apps"
cp "${ROOT_DIR}/snap/gui/linux-audio-focus.desktop" "${BUILD_DIR}/usr/share/applications/"
cp "${ROOT_DIR}/assets/icon.png" "${BUILD_DIR}/usr/share/icons/hicolor/512x512/apps/${PKG_NAME}.png"

# 4. Control file
cat << EOF > "${BUILD_DIR}/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Section: sound
Priority: optional
Architecture: ${PKG_ARCH}
Depends: python3, python3-gi, gir1.2-glib-2.0
Maintainer: Azmy <mask.azmy@gmail.com>
Homepage: https://github.com/azmykn/linux-audio-focus
Description: Mobile-style Audio Focus manager for Linux desktops (MPRIS)
 Linux Audio Focus brings intelligent, mobile-grade Audio Focus management
 to your Linux desktop. It runs quietly in the background as an event-driven
 service that monitors media playback via D-Bus (MPRIS). When an incoming
 audio or voice note plays (e.g. WhatsApp Web in Chrome), competing media
 players (e.g. YouTube in Firefox, VLC, Spotify) are automatically paused,
 and instantly resumed when the voice note ends.
EOF

# 5. Maintainer scripts
cat << 'EOF' > "${BUILD_DIR}/DEBIAN/postinst"
#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
    systemctl --global daemon-reload 2>/dev/null || true
fi
exit 0
EOF
chmod 755 "${BUILD_DIR}/DEBIAN/postinst"

cat << 'EOF' > "${BUILD_DIR}/DEBIAN/prerm"
#!/bin/sh
set -e
if [ "$1" = "remove" ]; then
    systemctl --global disable linux-audio-focus.service 2>/dev/null || true
fi
exit 0
EOF
chmod 755 "${BUILD_DIR}/DEBIAN/prerm"

# 6. Build .deb package
OUTPUT_DEB="${DIST_DIR}/${PKG_NAME}_${PKG_VERSION}_${PKG_ARCH}.deb"
dpkg-deb --build --root-owner-group "${BUILD_DIR}" "${OUTPUT_DEB}"

echo "==> Successfully created: ${OUTPUT_DEB}"
dpkg-deb --info "${OUTPUT_DEB}"
