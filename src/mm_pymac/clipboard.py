"""macOS clipboard operations via NSPasteboard."""

from AppKit import NSPasteboard, NSPasteboardTypeString


def set_clipboard(text: str) -> None:
    """Copy text to the system clipboard.

    Replaces any existing clipboard content.
    """
    pasteboard: NSPasteboard = NSPasteboard.generalPasteboard()
    pasteboard.clearContents()
    pasteboard.setString_forType_(text, NSPasteboardTypeString)


def get_clipboard() -> str | None:
    """Read current clipboard text content.

    Returns:
        The clipboard text, or None if the clipboard has no text content.

    """
    pasteboard: NSPasteboard = NSPasteboard.generalPasteboard()
    result: str | None = pasteboard.stringForType_(NSPasteboardTypeString)
    return result


def clear_clipboard(*, expected: str | None = None) -> None:
    """Clear the system clipboard.

    If expected is provided, only clear when the clipboard still contains that value.
    """
    pasteboard: NSPasteboard = NSPasteboard.generalPasteboard()
    if expected is not None:
        current: str | None = pasteboard.stringForType_(NSPasteboardTypeString)
        if current != expected:
            return
    pasteboard.clearContents()
