# Linux Audio Focus (MPRIS)

A lightweight Linux background service that brings mobile-like audio focus to your desktop.

When an incoming audio or video starts playing (for example, a WhatsApp Web voice note in Google Chrome), `linux-audio-focus` automatically pauses background playback (such as a YouTube video in Firefox or a movie in VLC). Once the voice note ends, your background media automatically resumes.

## Features

- **Automatic Pause & Resume**: Competing players pause when new audio begins and resume when the interruption ends.
- **Cross-Application Support**: Works with any media player or browser supporting the MPRIS D-Bus interface (Firefox, Chrome, Brave, VLC, MPV, Spotify, Celluloid, etc.).
- **Zero Polling / Event-Driven**: Listens strictly to D-Bus signal events with negligible CPU and memory usage.
- **Non-Privileged**: Runs entirely under user session (`systemd --user`) without requiring `sudo`.

## Requirements

- Linux with a graphical desktop session (GNOME, KDE, XFCE, etc.)
- Python 3 with `PyGObject` (`python3-gi`)
  - Ubuntu/Debian: `sudo apt install python3-gi`
  - Fedora: `sudo dnf install python3-gobject`
  - Arch: `sudo pacman -S python-gobject`

## Quick Installation

Clone this repository and run the install script:

```bash
git clone https://github.com/azmy/linux-audio-focus.git
cd linux-audio-focus
./install.sh
```

## Uninstallation

To remove the service and script:

```bash
cd linux-audio-focus
./uninstall.sh
```

## Manual Verification

Check service status anytime:

```bash
systemctl --user status linux-audio-focus.service
```

View real-time logs:

```bash
journalctl --user -u linux-audio-focus.service -f
```
