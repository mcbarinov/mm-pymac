# Architecture Decision Records

## ADR-1: osascript for dialogs (not NSAlert)

`show_alert()` is a standalone utility — no NSApplication is running. NSAlert requires spinning up NSApplication + run loop for a single dialog, then tearing it down — heavyweight for a one-shot call. osascript handles all of that in an isolated subprocess. Sound playback is also trivial in AppleScript (`do shell script "afplay ..."`), whereas NSAlert would need separate handling. The ~100ms subprocess overhead is irrelevant when waiting for human input.
