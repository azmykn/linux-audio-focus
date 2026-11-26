#!/usr/bin/env python3
"""
Linux Audio Focus Manager (MPRIS).

Automatically pauses competing media players when an incoming audio/voice stream plays
(e.g. WhatsApp Web voice note in Chrome), and automatically resumes the interrupted
player (e.g. YouTube in Firefox, local video in VLC) when the voice note ends.

Author: Mohamed Azmy
License: MIT
"""

import sys
import signal
import logging
import argparse
from gi.repository import Gio, GLib

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger("linux-audio-focus")


class AudioFocusManager:
    def __init__(self, bus: Gio.DBusConnection):
        self.bus = bus
        self.interrupter_sender = None
        self.paused_players = []

    def get_name_owner(self, service: str):
        """Retrieve the unique bus name (:1.x) owning a well-known service name."""
        try:
            res = self.bus.call_sync(
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "GetNameOwner",
                GLib.Variant("(s)", (service,)),
                GLib.VariantType("(s)"),
                Gio.DBusCallFlags.NONE,
                300,
                None
            )
            return res[0]
        except Exception:
            return None

    def get_player_property(self, service: str, prop: str):
        """Fetch an MPRIS Player interface property string value."""
        try:
            val = self.bus.call_sync(
                service,
                "/org/mpris/MediaPlayer2",
                "org.freedesktop.DBus.Properties",
                "Get",
                GLib.Variant("(ss)", ("org.mpris.MediaPlayer2.Player", prop)),
                GLib.VariantType("(v)"),
                Gio.DBusCallFlags.NONE,
                300,
                None
            )
            inner = val[0]
            if hasattr(inner, "get_string"):
                return inner.get_string()
            return str(inner)
        except Exception:
            return None

    def call_player_method(self, service: str, method: str):
        """Call an MPRIS method (Play, Pause, PlayPause, etc.)."""
        try:
            self.bus.call_sync(
                service,
                "/org/mpris/MediaPlayer2",
                "org.mpris.MediaPlayer2.Player",
                method,
                None,
                None,
                Gio.DBusCallFlags.NONE,
                300,
                None
            )
            logger.debug(f"Called {method} on {service}")
        except Exception as err:
            logger.debug(f"Failed to call {method} on {service}: {err}")

    def get_all_mpris_players(self):
        """List all registered MPRIS media players on the session bus."""
        try:
            res = self.bus.call_sync(
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "ListNames",
                None,
                GLib.VariantType("(as)"),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
            return [name for name in res[0] if name.startswith("org.mpris.MediaPlayer2.")]
        except Exception:
            return []

    def resume_paused_players(self):
        """Resume all players that were paused during the current interruption."""
        if not self.paused_players:
            self.interrupter_sender = None
            return

        all_players = self.get_all_mpris_players()
        for player in self.paused_players:
            if player in all_players:
                logger.info(f"Resuming player: {player}")
                self.call_player_method(player, "Play")

        self.paused_players.clear()
        self.interrupter_sender = None

    def on_properties_changed(self, sender_name: str, parameters):
        """Handle MPRIS PropertiesChanged signals."""
        changed_props = parameters[1]
        if "PlaybackStatus" not in changed_props:
            return

        val = changed_props["PlaybackStatus"]
        status = val.get_string() if hasattr(val, "get_string") else str(val)
        active_sender = sender_name

        logger.debug(f"Signal received from {active_sender}: status={status}")

        # Case 1: A player enters 'Playing' state
        if status == "Playing":
            if active_sender == self.interrupter_sender:
                return

            players = self.get_all_mpris_players()
            newly_paused = []

            for player in players:
                owner = self.get_name_owner(player)
                if owner and owner != active_sender:
                    st = self.get_player_property(player, "PlaybackStatus")
                    if st == "Playing":
                        logger.info(f"Pausing competing player: {player}")
                        self.call_player_method(player, "Pause")
                        if player not in self.paused_players:
                            newly_paused.append(player)

            if newly_paused:
                self.interrupter_sender = active_sender
                self.paused_players.extend(newly_paused)

        # Case 2: The interrupting player stops or pauses
        elif status in ("Paused", "Stopped"):
            if active_sender == self.interrupter_sender:
                logger.info(f"Interrupter {active_sender} stopped/paused. Resuming...")
                self.resume_paused_players()

    def on_name_owner_changed(self, parameters):
        """Handle disconnects when an application exits or crashes."""
        name, old_owner, new_owner = parameters
        if self.interrupter_sender and (name == self.interrupter_sender or old_owner == self.interrupter_sender) and not new_owner:
            logger.info(f"Interrupter {self.interrupter_sender} disconnected from bus. Resuming...")
            self.resume_paused_players()


def main():
    parser = argparse.ArgumentParser(description="Linux Audio Focus Manager (MPRIS)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    manager = AudioFocusManager(bus)

    # D-Bus Signal Callback for PropertiesChanged
    def signal_handler(conn, sender, path, iface, signal_name, params, user_data):
        if iface == "org.freedesktop.DBus.Properties" and signal_name == "PropertiesChanged":
            manager.on_properties_changed(sender, params)

    # D-Bus Signal Callback for NameOwnerChanged
    def owner_changed_handler(conn, sender, path, iface, signal_name, params, user_data):
        manager.on_name_owner_changed(params)

    bus.signal_subscribe(
        None,
        "org.freedesktop.DBus.Properties",
        "PropertiesChanged",
        "/org/mpris/MediaPlayer2",
        None,
        Gio.DBusSignalFlags.NONE,
        signal_handler,
        None
    )

    bus.signal_subscribe(
        "org.freedesktop.DBus",
        "org.freedesktop.DBus",
        "NameOwnerChanged",
        "/org/freedesktop/DBus",
        None,
        Gio.DBusSignalFlags.NONE,
        owner_changed_handler,
        None
    )

    loop = GLib.MainLoop()

    def exit_gracefully(sig, frame):
        logger.info("Terminating Linux Audio Focus Manager...")
        loop.quit()

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    logger.info("Linux Audio Focus Manager started successfully.")
    loop.run()


if __name__ == "__main__":
    main()
