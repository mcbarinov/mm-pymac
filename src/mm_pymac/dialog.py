"""macOS alert dialogs via osascript (AppleScript).

Provides a generic ``show_alert()`` that displays a native macOS alert with
configurable message, title, buttons, sound, and timeout.
"""

import logging
import subprocess  # nosec B404

logger = logging.getLogger(__name__)

DEFAULT_SOUND = "/System/Library/Sounds/Glass.aiff"


def _build_script(
    message: str,
    *,
    title: str,
    buttons: tuple[str, ...],
    default_button: str,
    sound: str | None,
) -> str:
    """Build an AppleScript string for ``display dialog``.

    Escapes double quotes in user-provided strings to prevent injection.
    """
    esc_msg = message.replace('"', '\\"')
    esc_title = title.replace('"', '\\"')
    btn_list = ", ".join(f'"{b.replace(chr(34), chr(92) + chr(34))}"' for b in buttons)
    esc_default = default_button.replace('"', '\\"')

    parts: list[str] = []
    if sound is not None:
        esc_sound = sound.replace('"', '\\"')
        parts.append(f'do shell script "afplay \\"{esc_sound}\\" &"')

    parts.append(f'display dialog "{esc_msg}" with title "{esc_title}" buttons {{{btn_list}}} default button "{esc_default}"')
    return "\n".join(parts)


def _parse_button(stdout: str) -> str | None:
    """Extract the button label from osascript output.

    osascript returns ``button returned:<label>``.
    """
    prefix = "button returned:"
    for line in stdout.strip().splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :]
    return None


def show_alert(
    message: str,
    *,
    title: str = "",
    buttons: tuple[str, ...] = ("OK",),
    default_button: str | None = None,
    sound: str | None = DEFAULT_SOUND,
    timeout_sec: int = 300,
) -> str | None:
    """Show a macOS alert via osascript and return the clicked button label.

    Args:
        message: Dialog body text.
        title: Dialog window title.
        buttons: Button labels (rightmost is visually default in macOS).
        default_button: Which button is the default. Defaults to the last button.
        sound: Path to a sound file to play, or None for silence.
        timeout_sec: Seconds before the dialog auto-dismisses.

    Returns:
        The label of the clicked button, or None on timeout/error.

    """
    resolved_default = default_button if default_button is not None else buttons[-1]
    script = _build_script(message, title=title, buttons=buttons, default_button=resolved_default, sound=sound)

    try:
        # S603/S607: args are controlled literals, "osascript" is a standard macOS utility
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False, timeout=timeout_sec)  # noqa: S603, S607  # nosec B603, B607
        return _parse_button(result.stdout)
    except Exception:
        logger.warning("Dialog failed", exc_info=True)
        return None
