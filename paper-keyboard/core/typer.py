"""core/typer.py — pynput key injection, native OS keyboard events.

Key-code strings (from keyboard_map.py) are resolved to pynput Key / KeyCode
objects at call time so this module has no hard dependency order.

Supported code formats
----------------------
  "a", "b", "1", "[", ...  → KeyCode.from_char(code)
  "enter", "space", "tab", "backspace", "shift", "shift_r",
  "ctrl", "ctrl_r", "alt", "alt_r", "esc", "delete", "home",
  "end", "up", "down", "left", "right", "caps_lock",
  "cmd", "cmd_r", "menu"   → pynput.keyboard.Key.<name>
"""
from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)

try:
    from pynput.keyboard import Controller, Key, KeyCode
    _kb = Controller()
    _AVAILABLE = True
    log.info("pynput keyboard controller ready")
except Exception as exc:
    log.warning("pynput unavailable — key injection disabled: %s", exc)
    _AVAILABLE = False
    Key = None          # type: ignore
    KeyCode = None      # type: ignore
    _kb = None


# Full mapping of code strings → pynput Key enum values
_SPECIAL: dict = {}

def _build_special() -> None:
    global _SPECIAL
    if not _AVAILABLE or Key is None:
        return
    _SPECIAL = {
        "enter":     Key.enter,
        "backspace": Key.backspace,
        "space":     Key.space,
        "tab":       Key.tab,
        "shift":     Key.shift,
        "shift_r":   Key.shift_r,
        "ctrl":      Key.ctrl,
        "ctrl_r":    Key.ctrl_r,
        "alt":       Key.alt,
        "alt_r":     Key.alt_r,
        "esc":       Key.esc,
        "delete":    Key.delete,
        "home":      Key.home,
        "end":       Key.end,
        "up":        Key.up,
        "down":      Key.down,
        "left":      Key.left,
        "right":     Key.right,
        "caps_lock": Key.caps_lock,
        "cmd":       Key.cmd,
        "cmd_r":     Key.cmd_r,
        "menu":      Key.menu,
        # aliases
        "windows":   Key.cmd,
        "win":       Key.cmd,
        "rwin":      Key.cmd_r,
        "lalt":      Key.alt,
        "ralt":      Key.alt_r,
        "lshift":    Key.shift,
        "rshift":    Key.shift_r,
        "lctrl":     Key.ctrl,
        "rctrl":     Key.ctrl_r,
        "del":       Key.delete,
    }

_build_special()


def _resolve(code: str):
    """Convert a code string to a pynput key object, or None on failure."""
    if not _AVAILABLE:
        return None
    lower = code.lower()
    if lower in _SPECIAL:
        return _SPECIAL[lower]
    if len(code) == 1:
        try:
            return KeyCode.from_char(code)  # type: ignore[union-attr]
        except Exception:
            pass
    log.debug("Unknown key code: %r", code)
    return None


def type_key(code: str) -> bool:
    """Press and immediately release a key.  Returns True on success."""
    if not _AVAILABLE or _kb is None:
        log.debug("type_key skipped (pynput unavailable): %r", code)
        return False

    key = _resolve(code)
    if key is None:
        log.warning("type_key: could not resolve code %r", code)
        return False

    try:
        _kb.press(key)
        _kb.release(key)
        log.debug("type_key: pressed %r → %s", code, key)
        return True
    except Exception as exc:
        log.error("type_key error for %r: %s", code, exc)
        return False


def is_available() -> bool:
    return _AVAILABLE
