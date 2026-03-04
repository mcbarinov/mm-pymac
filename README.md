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

Subscribe to lock/unlock events (requires a running run loop, e.g. `TrayApp.run()`):

```python
from mm_pymac import on_screen_locked, on_screen_unlocked

unsub_lock = on_screen_locked(lambda: print("Screen locked"))
unsub_unlock = on_screen_unlocked(lambda: print("Screen unlocked"))

# Later, to stop listening:
unsub_lock()
unsub_unlock()
```
