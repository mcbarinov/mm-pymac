"""Tests for clipboard operations (uses the real system clipboard)."""

import pytest
from AppKit import NSPasteboard, NSPasteboardTypeString

from mm_pymac.clipboard import clear_clipboard, get_clipboard, set_clipboard

# All clipboard tests must run in the same xdist worker to avoid race conditions on the shared system clipboard.
pytestmark = pytest.mark.xdist_group("clipboard")


@pytest.fixture(autouse=True)
def _restore_clipboard():
    """Save and restore clipboard content around each test."""
    pasteboard = NSPasteboard.generalPasteboard()
    original = pasteboard.stringForType_(NSPasteboardTypeString)
    yield
    pasteboard.clearContents()
    if original is not None:
        pasteboard.setString_forType_(original, NSPasteboardTypeString)


class TestSetAndGetClipboard:
    """Round-trip tests for set_clipboard / get_clipboard."""

    def test_set_then_get(self):
        """Set text and read it back."""
        set_clipboard("hello")
        assert get_clipboard() == "hello"

    def test_overwrites_previous(self):
        """New set_clipboard replaces old content."""
        set_clipboard("first")
        set_clipboard("second")
        assert get_clipboard() == "second"

    def test_empty_string(self):
        """Empty string is valid clipboard content, not None."""
        set_clipboard("")
        assert get_clipboard() == ""

    def test_unicode(self):
        """Unicode text round-trips correctly."""
        text = "emoji: \U0001f680 cjk: \u4f60\u597d"
        set_clipboard(text)
        assert get_clipboard() == text


class TestGetClipboard:
    """Tests for get_clipboard edge cases."""

    def test_returns_none_after_clear(self):
        """Returns None when clipboard has no text type."""
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        assert get_clipboard() is None


class TestClearClipboard:
    """Tests for clear_clipboard with and without expected parameter."""

    def test_unconditional_clear(self):
        """Clears clipboard without expected check."""
        set_clipboard("something")
        clear_clipboard()
        assert get_clipboard() is None

    def test_expected_matches(self):
        """Clears when expected matches current content."""
        set_clipboard("secret")
        clear_clipboard(expected="secret")
        assert get_clipboard() is None

    def test_expected_does_not_match(self):
        """Does not clear when expected differs from current content."""
        set_clipboard("keep this")
        clear_clipboard(expected="something else")
        assert get_clipboard() == "keep this"

    def test_expected_with_empty_clipboard(self):
        """Does not clear when expected is provided but clipboard has no text."""
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        clear_clipboard(expected="foo")
        # Clipboard stays cleared (None != "foo", so clearContents not called again — still None)
        assert get_clipboard() is None
