<div align="center">
  <img src="assets/icon.png" width="140" height="140" alt="Linux Audio Focus Icon" style="border-radius: 28px;" />
  <h1>Linux Audio Focus</h1>
  <p><strong>Intelligent, mobile-like Audio Focus management for the Linux desktop (MPRIS)</strong></p>

  <p>
    <a href="https://github.com/azmykn/linux-audio-focus/releases"><img src="https://img.shields.io/github/v/release/azmykn/linux-audio-focus?style=flat-square&color=blue" alt="Latest Release" /></a>
    <a href="https://snapcraft.io/linux-audio-focus"><img src="https://img.shields.io/badge/snapcraft-linux--audio--focus-orange?style=flat-square" alt="Snapcraft" /></a>
    <img src="https://img.shields.io/badge/platform-Linux%20%7C%20Ubuntu-E95420?style=flat-square" alt="Platform" />
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
    <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square" alt="Python Version" />
  </p>
</div>

---

## Overview

On mobile platforms (Android & iOS), the operating system provides an **Audio Focus** system: when an incoming voice message or call plays (e.g. WhatsApp, Telegram), background media (such as YouTube or Spotify) automatically pauses, and resumes when the message finishes.

On desktop Linux, all audio streams mix simultaneously by default. If you are watching a video or listening to music and click to play a voice note in WhatsApp Web or an incoming audio message, both sounds play on top of each other.

**Linux Audio Focus** bridges this gap. It runs quietly in the background as an event-driven service, automatically pausing background playback whenever a new audio or voice stream begins, and immediately resuming your original media when the interruption ends.

---

## The Experience

| Scenario | Standard Desktop Behavior | With Linux Audio Focus |
| :--- | :--- | :--- |
| **Watching YouTube while a voice note arrives** | Both sounds clash and play together simultaneously. | YouTube automatically pauses the instant the voice note starts. |
| **Voice note finishes** | YouTube continues playing, user must manually seek back. | YouTube automatically resumes from the exact millisecond it stopped. |
| **Tab/Player closed during playback** | Audio might hang or glitch. | Interrupting state clears cleanly; background media safely resumes. |

---

## Key Features

- **Automatic Pause & Resume**: Instantly pauses competing players when a new stream takes focus, and resumes playback when the stream finishes.
- **Cross-Application Support**: Works seamlessly across browsers, video players, and audio apps through the standard Linux MPRIS D-Bus specification.
- **Zero Polling / Event-Driven**: Uses D-Bus signal subscriptions (`PropertiesChanged`, `NameOwnerChanged`). Consumes **0.0% CPU** at idle and negligible memory (~14MB).
- **Graceful Lifecycle Handling**: Detects when an interrupting app is closed, paused, or killed, ensuring your background audio never remains paused unintentionally.
- **Non-Privileged & Secure**: Runs entirely within user session space (`systemd --user` or desktop autostart) without requiring `sudo` or elevated privileges.

---

## Supported Applications

Linux Audio Focus supports any application adhering to the **MPRIS (Media Player Remote Interfacing Specification)** standard:

| Category | Supported Apps |
| :--- | :--- |
| **Web Browsers** | Google Chrome, Mozilla Firefox, Brave, Microsoft Edge, Chromium, Opera, Vivaldi |
| **Media Players** | VLC Media Player, MPV (with `mpv-mpris`), Celluloid, Totem (GNOME Videos) |
| **Music & Streaming** | Spotify, Rhythmbox, Clementine, Audacious, Strawberry |
| **Communication Web Apps** | WhatsApp Web, Telegram Web, Slack, Discord (running in any supported browser) |

---

## Installation Methods

### Option 1: Snap Store (Ubuntu App Center)

Install directly from the Canonical Snap Store:

```bash
sudo snap install linux-audio-focus
```

### Option 2: Native APT / Debian Package (.deb)

Download the latest `.deb` package from the [GitHub Releases](https://github.com/azmykn/linux-audio-focus/releases) page, then install with:

```bash
sudo apt install ./linux-audio-focus_1.0.0_all.deb
```

Or build and package it locally in one step:

```bash
./packaging/build-deb.sh
sudo apt install ./dist/linux-audio-focus_1.0.0_all.deb
```

### Option 3: Quick Script Install (No Root Required)

Clone the repository and run the standalone user-level installer:

```bash
git clone https://github.com/azmykn/linux-audio-focus.git
cd linux-audio-focus
./install.sh
```

---

## How It Works Under The Hood

```
[ App A Playing ]  <--- (e.g. YouTube in Firefox)
       |
       v
[ App B Starts Playing ]  <--- (e.g. Voice Note in Chrome)
       |
       |-- 1. Captures D-Bus 'PropertiesChanged' (PlaybackStatus: Playing)
       |-- 2. Detects App B as Interrupter
       |-- 3. Calls 'org.mpris.MediaPlayer2.Player.Pause' on App A
       v
[ App B Stops / Finishes ]
       |
       |-- 4. Captures D-Bus 'PlaybackStatus: Paused' from Interrupter
       |-- 5. Calls 'org.mpris.MediaPlayer2.Player.Play' on App A
       v
[ App A Resumes Seamlessly ]
```

---

## Management & Debugging

### Check Service Status
```bash
systemctl --user status linux-audio-focus.service
```

### View Real-Time Logs
```bash
journalctl --user -u linux-audio-focus.service -f
```

### Run Manually with Debug Output
You can run the script directly in your terminal with verbose logging enabled:
```bash
linux-audio-focus -v
```

---

## Uninstallation

Depending on how you installed the application:

* **If installed via Script:**
  ```bash
  cd linux-audio-focus && ./uninstall.sh
  ```
* **If installed via APT:**
  ```bash
  sudo apt remove linux-audio-focus
  ```
* **If installed via Snap:**
  ```bash
  sudo snap remove linux-audio-focus
  ```

---

## License & Credits

- **Author**: Mohamed Azmy ([@azmykn](https://github.com/azmykn))
- **License**: [MIT License](LICENSE)
- **Repository**: [https://github.com/azmykn/linux-audio-focus](https://github.com/azmykn/linux-audio-focus)
