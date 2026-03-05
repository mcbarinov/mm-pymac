# mm-pymac

macOS native utilities for Python.

## Installation

```bash
uv add mm-pymac
```

## Usage

### Tray / Status Bar

```python
from mm_pymac import TrayApp, MenuItem, MenuSeparator

app = TrayApp(title="My App")
app.set_menu([
    MenuItem("Status: running", enabled=False),
    MenuSeparator(),
    MenuItem("Quit", callback=lambda _: app.quit()),
])
app.start_timer(1.0, lambda: print("tick"))
app.run()
```

### Alerts

```python
from mm_pymac import show_alert

result = show_alert(
    "Your task is complete.",
    title="Done",
    buttons=("Cancel", "OK"),
    default_button="OK",
)
if result == "OK":
    print("User confirmed")
```

### Lock Screen

```python
from mm_pymac import is_screen_locked

locked = is_screen_locked()
if locked is None:
    print("Cannot determine lock state")
elif locked:
    print("Screen is locked")
else:
    print("Screen is unlocked")
```

#### Event subscription

Subscribe to lock/unlock events from a `TrayApp`. Requires a running NSRunLoop — `TrayApp.run()` provides it:

```python
from mm_pymac import TrayApp, on_screen_locked, on_screen_unlocked

app = TrayApp(title="My App")
on_screen_locked(lambda: print("Screen locked"))
on_screen_unlocked(lambda: print("Screen unlocked"))
app.run()
```

#### Polling watcher (no NSRunLoop required)

Use `watch_screen_lock()` for scripts with their own main loop:

```python
from mm_pymac import watch_screen_lock

stop = watch_screen_lock(
    on_lock=lambda: print("Screen locked"),
    on_unlock=lambda: print("Screen unlocked"),
)

# Your own main loop
while True:
    do_work()
```

### Clipboard

```python
from mm_pymac import set_clipboard, get_clipboard, clear_clipboard

# Copy text
set_clipboard("Hello, world!")

# Read text (returns None if clipboard has no text)
text = get_clipboard()

# Clear clipboard
clear_clipboard()

# Clear only if clipboard still contains the expected value
clear_clipboard(expected="Hello, world!")
```

## Examples

See the [`examples/`](examples/) folder for runnable scripts:

- [`lock_events_cli.py`](examples/lock_events_cli.py) — CLI doing periodic work while lock/unlock events fire in the background
- [`lock_events_tray.py`](examples/lock_events_tray.py) — TrayApp showing screen lock state in the menu bar
