"""Tests for dialog.py pure helper functions."""

import pytest

from mm_pymac.dialog import _build_script, _parse_button


class TestBuildScript:
    """Tests for AppleScript string builder."""

    def test_basic_single_button(self):
        """Single button, no sound — produces a bare display dialog line."""
        result = _build_script("Hello", title="Title", buttons=("OK",), default_button="OK", sound=None)
        assert result == 'display dialog "Hello" with title "Title" buttons {"OK"} default button "OK"'

    def test_sound_prepends_afplay(self):
        """Sound path adds an afplay line before the dialog."""
        result = _build_script("msg", title="t", buttons=("OK",), default_button="OK", sound="/path/to/sound.aiff")
        lines = result.splitlines()
        assert len(lines) == 2
        assert lines[0] == 'do shell script "afplay \\"/path/to/sound.aiff\\" &"'
        assert lines[1].startswith("display dialog")

    def test_no_sound(self):
        """No sound — single-line script without afplay."""
        result = _build_script("msg", title="t", buttons=("OK",), default_button="OK", sound=None)
        assert "\n" not in result
        assert "afplay" not in result

    def test_quote_escaping(self):
        """Double quotes in all user-provided strings are escaped."""
        result = _build_script('say "hi"', title='my "app"', buttons=('"Yes"',), default_button='"Yes"', sound=None)
        assert r"say \"hi\"" in result
        assert r"my \"app\"" in result
        assert r"\"Yes\"" in result

    def test_multiple_buttons(self):
        """Multiple buttons appear comma-separated inside braces."""
        result = _build_script("msg", title="t", buttons=("Cancel", "No", "Yes"), default_button="Yes", sound=None)
        assert 'buttons {"Cancel", "No", "Yes"}' in result

    @pytest.mark.parametrize(
        ("field", "value", "expected_fragment"),
        [
            ("message", 'line "one"', r"\"one\""),
            ("title", 'title "x"', r"\"x\""),
            ("message", "plain text", "plain text"),
            ("message", "back\\slash", "back\\slash"),
        ],
        ids=["msg-quotes", "title-quotes", "msg-plain", "msg-backslash"],
    )
    def test_parametrized_escaping(self, field, value, expected_fragment):
        """Various special characters are handled correctly."""
        kwargs = {"message": "m", "title": "t", "buttons": ("OK",), "default_button": "OK", "sound": None}
        kwargs[field] = value
        result = _build_script(**kwargs)
        assert expected_fragment in result


class TestParseButton:
    """Tests for osascript output parser."""

    def test_standard_output(self):
        """Standard single-word button label."""
        assert _parse_button("button returned:OK") == "OK"

    def test_multi_word_button(self):
        """Button label with spaces and apostrophe."""
        assert _parse_button("button returned:Don't Save") == "Don't Save"

    def test_empty_label(self):
        """Empty string after the prefix returns empty string."""
        assert _parse_button("button returned:") == ""

    def test_no_match(self):
        """Random string without the prefix returns None."""
        assert _parse_button("some random output") is None

    def test_empty_string(self):
        """Empty input returns None."""
        assert _parse_button("") is None

    def test_multiline_output(self):
        """Button line among other lines is still found."""
        stdout = "gave up:false\nbutton returned:OK\n"
        assert _parse_button(stdout) == "OK"

    @pytest.mark.parametrize(
        ("stdout", "expected"),
        [
            ("button returned:OK", "OK"),
            ("button returned:Cancel", "Cancel"),
            ("button returned:Don't Save", "Don't Save"),
            ("button returned:Yes Please", "Yes Please"),
        ],
        ids=["ok", "cancel", "apostrophe", "two-words"],
    )
    def test_parametrized_happy_path(self, stdout, expected):
        """Happy-path variants extracted correctly."""
        assert _parse_button(stdout) == expected
