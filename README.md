# Linux Audio Focus (MPRIS)

A lightweight Linux background service that brings mobile-like audio focus to your desktop.

When an incoming audio or video starts playing (for example, a WhatsApp Web voice note in Google Chrome), `linux-audio-focus` automatically pauses background playback (such as a YouTube video in Firefox or a movie in VLC). Once the voice note ends, your background media automatically resumes.

## Features

- **Automatic Pause & Resume**: Competing players pause when new audio begins and resume when the interruption ends.
- **Cross-Application Support**: Works with any media player or browser supporting the MPRIS D-Bus interface (Firefox, Chrome, Brave, VLC, MPV, Spotify, Celluloid, etc.).
- **Zero Polling / Event-Driven**: Listens strictly to D-Bus signal events with negligible CPU and memory usage.
- **Non-Privileged**: Runs entirely under user session (`systemd --user`) without requiring `sudo`.

## Installation Methods

### Option 1: Native APT / Debian Package (.deb)

Download the latest `.deb` package from [Releases](https://github.com/azmykn/linux-audio-focus/releases), then install it using `apt`:

```bash
sudo apt install ./linux-audio-focus_1.0.0_all.deb
```

Or build and install it locally:

```bash
./packaging/build-deb.sh
sudo apt install ./dist/linux-audio-focus_1.0.0_all.deb
```

### Option 2: Snap Store (Ubuntu App Center)

Install directly via Snapcraft:

```bash
sudo snap install linux-audio-focus
```

### Option 3: Quick Script Install (No Root Required)

Clone this repository and run the install script:

```bash
git clone https://github.com/azmykn/linux-audio-focus.git
cd linux-audio-focus
./install.sh
```

## Uninstallation

- If installed via script:
  ```bash
  ./uninstall.sh
  ```
- If installed via APT:
  ```bash
  sudo apt remove linux-audio-focus
  ```
- If installed via Snap:
  ```bash
  sudo snap remove linux-audio-focus
  ```

## Service Status & Logs

Check service status anytime:

```bash
systemctl --user status linux-audio-focus.service
```

View real-time logs:

```bash
journalctl --user -u linux-audio-focus.service -f
```
