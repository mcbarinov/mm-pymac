# mm-pymac

macOS utilities for Python CLI apps: tray/status bar and alert dialogs.

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
