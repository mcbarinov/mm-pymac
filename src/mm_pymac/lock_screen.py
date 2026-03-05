"""macOS lock screen detection and event subscription."""

import threading
from collections.abc import Callable
from typing import Self

import objc
from Foundation import NSDistributedNotificationCenter, NSObject
from Quartz import CGSessionCopyCurrentDictionary


class _Observer(NSObject):  # type: ignore[misc]
    """Routes distributed notification to a Python callback."""

    def init(self) -> Self:
        """Initialize callback storage."""
        self = objc.super(_Observer, self).init()  # noqa: PLW0642  — required pyobjc init pattern
        self.callback: Callable[[], None] = lambda: None
        return self

    def handleNotification_(self, _notification: object) -> None:  # noqa: N802  — ObjC selector
        """Forward notification to Python callback."""
        self.callback()


_active_observers: set[_Observer] = set()
"""Keeps strong references to active observers so GC doesn't collect them."""


def _subscribe(notification_name: str, callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to a distributed notification. Returns unsubscribe function."""
    observer = _Observer.alloc().init()
    observer.callback = callback
    center = NSDistributedNotificationCenter.defaultCenter()
    # suspensionBehavior=4 (NSNotificationSuspensionBehaviorDeliverImmediately) ensures
    # delivery even when the process is considered suspended by the OS.
    center.addObserver_selector_name_object_suspensionBehavior_(observer, "handleNotification:", notification_name, None, 4)
    _active_observers.add(observer)

    def unsubscribe() -> None:
        """Remove the observer from the notification center and active set."""
        center.removeObserver_(observer)
        _active_observers.discard(observer)

    return unsubscribe


def on_screen_locked(callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to screen lock events. Requires a running NSRunLoop (e.g. TrayApp.run()). Returns unsubscribe function."""
    return _subscribe("com.apple.screenIsLocked", callback)


def on_screen_unlocked(callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to screen unlock events. Requires a running NSRunLoop (e.g. TrayApp.run()). Returns unsubscribe function."""
    return _subscribe("com.apple.screenIsUnlocked", callback)


def is_screen_locked() -> bool | None:
    """Check whether the macOS screen is currently locked. Works without NSRunLoop.

    Uses ``CGSessionCopyCurrentDictionary()`` to inspect the current login
    session.

    Returns:
        True if the lock screen is active (including after fast user switching).
        False if the screen is unlocked.
        None if the session state cannot be determined (headless/remote/no GUI session).

    """
    session = CGSessionCopyCurrentDictionary()
    if session is None:
        return None
    # CGSSessionScreenIsLocked is absent when unlocked, present (True) when locked
    return bool(session.get("CGSSessionScreenIsLocked", False))


def watch_screen_lock(
    on_lock: Callable[[], None] | None = None,
    on_unlock: Callable[[], None] | None = None,
    *,
    interval: float = 1.0,
) -> Callable[[], None]:
    """Watch for screen lock/unlock by polling. Works without a NSRunLoop.

    Starts a background daemon thread that calls is_screen_locked() every
    ``interval`` seconds. Fires ``on_lock`` when the screen locks and
    ``on_unlock`` when it unlocks.

    Returns a stop function — call it to cancel watching.
    """
    stop = threading.Event()

    def _poll() -> None:
        """Poll is_screen_locked() and fire callbacks on state changes."""
        prev = is_screen_locked()
        while not stop.wait(interval):
            current = is_screen_locked()
            if current != prev:
                if current is True and on_lock is not None:
                    on_lock()
                elif current is False and on_unlock is not None:
                    on_unlock()
                prev = current

    threading.Thread(target=_poll, daemon=True).start()
    return stop.set
