"""core/keyboard_map.py — Key bounding boxes in normalised keyboard space.

Coordinate system
-----------------
(0, 0) = centre of top-left ArUco marker
(1, 1) = centre of bottom-right ArUco marker

Because the printed template has the markers slightly inset from the paper
edges, the keyboard keys extend slightly outside [0, 1] in x (roughly
-0.095 … 1.095) and the Esc/Del row is at around y=0.055 while the space
bar bottom is near y=0.895.  All values are read from config.json and can
be tuned without touching code.

Key `code` field
----------------
  - Single character string → regular key  e.g. "a", "1", "["
  - Named key string        → special key  e.g. "enter", "backspace", "shift"
  (See core/typer.py for the full name→pynput mapping.)
"""
from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

# Populated once by init()
_LAYOUT: List[Dict] = []


# ── Builder helpers ──────────────────────────────────────────────────────────

def _key(name: str, code: str,
         x0: float, y0: float, x1: float, y1: float) -> Dict:
    return {
        "name": name,
        "code": code,
        "x0": round(x0, 5), "y0": round(y0, 5),
        "x1": round(x1, 5), "y1": round(y1, 5),
        "cx": round((x0 + x1) / 2, 5),
        "cy": round((y0 + y1) / 2, 5),
    }


def _build(cfg: dict) -> List[Dict]:
    """Build the full QWERTY layout from config values."""
    KW  = cfg["key_width"]       # 1-unit key width
    KH  = cfg["key_height"]      # row height
    XS  = cfg["x_start"]        # left edge of keyboard (Esc / ` key)

    # Row top-edges
    YE  = cfg["y_esc"]
    YN  = cfg["y_num"]
    YQ  = cfg["y_qwe"]
    YA  = cfg["y_asd"]
    YZ  = cfg["y_zxc"]
    YSP = cfg["y_spc"]
    YB  = cfg["y_bot"]           # bottom edge of space row

    keys: List[Dict] = []

    # ── ESC / DEL row (floaters above number row) ─────────────────────────
    keys.append(_key("Esc",    "esc",    XS,              YE, XS + KW * 1.5, YN))
    keys.append(_key("Del",    "delete", XS + KW * 14.0,  YE, XS + KW * 15.5, YN))

    # ── Number row ────────────────────────────────────────────────────────
    num_chars = [
        ("`",  "`"),  ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"),
        ("5",  "5"),  ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
        ("0",  "0"),  ("-", "-"), ("=", "="),
    ]
    x = XS
    for name, code in num_chars:
        keys.append(_key(name, code, x, YN, x + KW, YQ))
        x += KW
    # Backspace: 1.5 U wide
    keys.append(_key("Backspace", "backspace", x, YN, x + KW * 1.5, YQ))
    x += KW * 1.5
    # Home: fills remaining width to right edge
    keys.append(_key("Home", "home", x, YN, XS + KW * 15.5, YQ))

    # ── QWERTY row ────────────────────────────────────────────────────────
    # Tab: 1.5 U
    x = XS
    keys.append(_key("Tab", "tab", x, YQ, x + KW * 1.5, YA))
    x += KW * 1.5
    for ch in "QWERTYUIOP":
        keys.append(_key(ch, ch.lower(), x, YQ, x + KW, YA))
        x += KW
    keys.append(_key("[",  "[",   x, YQ, x + KW, YA)); x += KW
    keys.append(_key("]",  "]",   x, YQ, x + KW, YA)); x += KW
    keys.append(_key("\\", "\\",  x, YQ, x + KW, YA)); x += KW
    # End: fills remaining
    keys.append(_key("End", "end", x, YQ, XS + KW * 15.5, YA))

    # ── ASDF row ─────────────────────────────────────────────────────────
    x = XS
    keys.append(_key("CapsLock", "caps_lock", x, YA, x + KW * 1.75, YZ))
    x += KW * 1.75
    for ch in "ASDFGHJKL":
        keys.append(_key(ch, ch.lower(), x, YA, x + KW, YZ))
        x += KW
    keys.append(_key(";",  ";",  x, YA, x + KW, YZ)); x += KW
    keys.append(_key("'",  "'",  x, YA, x + KW, YZ)); x += KW
    # Enter: takes the rest of the row
    keys.append(_key("Enter", "enter", x, YA, XS + KW * 15.5, YZ))

    # ── ZXCV row ─────────────────────────────────────────────────────────
    x = XS
    keys.append(_key("LShift", "shift", x, YZ, x + KW * 2.25, YSP))
    x += KW * 2.25
    for ch in "ZXCVBNM":
        keys.append(_key(ch, ch.lower(), x, YZ, x + KW, YSP))
        x += KW
    keys.append(_key(",",  ",",  x, YZ, x + KW, YSP)); x += KW
    keys.append(_key(".",  ".",  x, YZ, x + KW, YSP)); x += KW
    keys.append(_key("/",  "/",  x, YZ, x + KW, YSP)); x += KW
    keys.append(_key("RShift", "shift_r", x, YZ, x + KW * 1.5, YSP)); x += KW * 1.5
    keys.append(_key("Up",  "up",  x, YZ, XS + KW * 15.5, YSP))

    # ── Space / modifier row ──────────────────────────────────────────────
    x = XS
    keys.append(_key("Ctrl",  "ctrl",  x, YSP, x + KW * 1.5, YB)); x += KW * 1.5
    keys.append(_key("Win",   "cmd",   x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("LAlt",  "alt",   x, YSP, x + KW,       YB)); x += KW
    # Spacebar: 5.5 U wide
    sp_end = x + KW * 5.5
    keys.append(_key("Space", "space", x, YSP, sp_end, YB)); x = sp_end
    keys.append(_key("RAlt",  "alt_r", x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("RWin",  "cmd_r", x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("Menu",  "menu",  x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("Left",  "left",  x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("Down",  "down",  x, YSP, x + KW,       YB)); x += KW
    keys.append(_key("Right", "right", x, YSP, XS + KW * 15.5, YB))

    return keys


# ── Public API ────────────────────────────────────────────────────────────────

def init(config: dict) -> None:
    """Build the layout from the keyboard_map section of config.json."""
    global _LAYOUT
    _LAYOUT = _build(config["keyboard_map"])
    log.info("KeyboardMap: %d keys loaded", len(_LAYOUT))


def get_key_at(kx: float, ky: float) -> Optional[Dict]:
    """Return the key dict whose bounding box contains (kx, ky), or None."""
    for k in _LAYOUT:
        if k["x0"] <= kx <= k["x1"] and k["y0"] <= ky <= k["y1"]:
            return k
    return None


def get_all_keys() -> List[Dict]:
    return list(_LAYOUT)


def get_key_by_name(name: str) -> Optional[Dict]:
    for k in _LAYOUT:
        if k["name"] == name:
            return k
    return None
