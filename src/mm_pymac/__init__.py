"""macOS native utilities for Python."""

from .dialog import DEFAULT_SOUND as DEFAULT_SOUND
from .dialog import show_alert as show_alert
from .lock_screen import is_screen_locked as is_screen_locked
from .lock_screen import on_screen_locked as on_screen_locked
from .lock_screen import on_screen_unlocked as on_screen_unlocked
from .tray import MenuItem as MenuItem
from .tray import MenuSeparator as MenuSeparator
from .tray import TrayApp as TrayApp
