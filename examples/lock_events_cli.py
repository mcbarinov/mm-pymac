"""CLI demo: watch_screen_lock() with a foreground work loop.

Starts a polling watcher on a background daemon thread, then runs its own
main loop printing "doing work..." every 3 s. Lock/unlock events appear
inline. No NSRunLoop or TrayApp required.

Run:
    uv run python examples/lock_events_cli.py
"""

import time
from datetime import datetime

from mm_pymac import watch_screen_lock


def _now() -> str:
    """Return current time as HH:MM:SS string."""
    return datetime.now().strftime("%H:%M:%S")


watch_screen_lock(
    on_lock=lambda: print(f"\n[{_now()}] *** Screen locked ***"),
    on_unlock=lambda: print(f"\n[{_now()}] *** Screen unlocked ***"),
)

print("Running... Lock/unlock events will appear inline. (Ctrl+C to stop)")
try:
    while True:
        print(f"[{_now()}] doing work...")
        time.sleep(3)
except KeyboardInterrupt:
    pass
