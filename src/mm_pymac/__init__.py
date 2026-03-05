"""macOS native utilities for Python."""

from .clipboard import clear_clipboard as clear_clipboard
from .clipboard import get_clipboard as get_clipboard
from .clipboard import set_clipboard as set_clipboard
from .dialog import DEFAULT_SOUND as DEFAULT_SOUND
from .dialog import show_alert as show_alert
from .lock_screen import is_screen_locked as is_screen_locked
from .lock_screen import on_screen_locked as on_screen_locked
from .lock_screen import on_screen_unlocked as on_screen_unlocked
from .lock_screen import watch_screen_lock as watch_screen_lock
from .tray import MenuItem as MenuItem
from .tray import MenuSeparator as MenuSeparator
from .tray import TrayApp as TrayApp
