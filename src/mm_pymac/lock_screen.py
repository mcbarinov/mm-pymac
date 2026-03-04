"""macOS lock screen detection and event subscription."""

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


def _subscribe(notification_name: str, callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to a distributed notification. Returns unsubscribe function."""
    observer = _Observer.alloc().init()
    observer.callback = callback
    center = NSDistributedNotificationCenter.defaultCenter()
    center.addObserver_selector_name_object_(observer, "handleNotification:", notification_name, None)
    _active_observers.add(observer)

    def unsubscribe() -> None:
        center.removeObserver_(observer)
        _active_observers.discard(observer)

    return unsubscribe


def on_screen_locked(callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to screen lock events. Returns unsubscribe function.

    Requires a running run loop (e.g. TrayApp.run()).
    """
    return _subscribe("com.apple.screenIsLocked", callback)


def on_screen_unlocked(callback: Callable[[], None]) -> Callable[[], None]:
    """Subscribe to screen unlock events. Returns unsubscribe function.

    Requires a running run loop (e.g. TrayApp.run()).
    """
    return _subscribe("com.apple.screenIsUnlocked", callback)


def is_screen_locked() -> bool | None:
    """Check whether the macOS screen is currently locked.

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
