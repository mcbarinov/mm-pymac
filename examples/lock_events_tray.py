"""TrayApp demo: on_screen_locked / on_screen_unlocked with NSRunLoop.

Shows the current lock state in the menu bar title and a non-clickable
menu item. Events are push-based (NSDistributedNotificationCenter) and
delivered instantly because TrayApp.run() pumps the NSRunLoop.
Logs every state change to stderr.

Run:
    uv run python examples/lock_events_tray.py
"""

import logging

from mm_pymac import MenuItem, MenuSeparator, TrayApp, is_screen_locked, on_screen_locked, on_screen_unlocked

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")


def _label(locked: bool | None) -> str:
    """Return human-readable lock state label for the title and menu item."""
    if locked is True:
        return "Screen: locked"
    if locked is False:
        return "Screen: unlocked"
    return "Screen: unknown"


app = TrayApp(title=_label(is_screen_locked()))
"""TrayApp instance — owns the menu bar icon and event loop."""

status = MenuItem(_label(is_screen_locked()), enabled=False)
"""Non-clickable menu item that mirrors the current lock state text."""

app.set_menu(
    [
        status,
        MenuSeparator(),
        MenuItem("Quit", callback=lambda _: app.quit()),
    ]
)

logging.info("Started, initial state: %s", _label(is_screen_locked()))


def _on_lock() -> None:
    """Handle screen-locked notification: update title, menu item, and log."""
    app.title = _label(True)
    status.title = _label(True)
    logging.info("Screen locked")


def _on_unlock() -> None:
    """Handle screen-unlocked notification: update title, menu item, and log."""
    app.title = _label(False)
    status.title = _label(False)
    logging.info("Screen unlocked")


on_screen_locked(_on_lock)
on_screen_unlocked(_on_unlock)

app.run()
