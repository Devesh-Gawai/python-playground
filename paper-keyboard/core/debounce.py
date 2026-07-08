"""core/debounce.py — Per-key cooldown (anti-repeat) + audible tick on keypress.

Each key gets its own independent timestamp, so typing "ABA" quickly is
fine while holding down a single key will not repeat.
"""
from __future__ import annotations

import time
from typing import Dict

import numpy as np

from utils.logger import get_logger

log = get_logger(__name__)

# pygame is optional — if unavailable the tick is silently skipped
try:
    import pygame
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    _PYGAME_OK = True
except Exception as exc:
    log.warning("pygame not available, tick sound disabled: %s", exc)
    _PYGAME_OK = False


def _make_tick(freq_hz: int, duration_ms: int, volume: float) -> "pygame.mixer.Sound | None":
    """Generate a short sine-wave blip as a pygame Sound object."""
    if not _PYGAME_OK:
        return None
    try:
        sample_rate = 44100
        n_samples   = int(sample_rate * duration_ms / 1000)
        t           = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
        # Sine wave with a quick linear fade-out to avoid click
        wave = np.sin(2 * np.pi * freq_hz * t)
        fade = np.linspace(1.0, 0.0, n_samples)
        wave = (wave * fade * volume * 32767).astype(np.int16)
        # Make stereo by stacking the mono wave twice (for channels=2)
        wave_stereo = np.stack([wave, wave], axis=1)
        sound = pygame.sndarray.make_sound(wave)
        return sound
    except Exception as exc:
        log.warning("Tick generation failed: %s", exc)
        return None


class Debouncer:
    """Track per-key fire times and enforce a minimum interval."""

    def __init__(self, cfg: dict):
        tc = cfg["touch"]
        sc = cfg["sound"]
        self._cooldown_s: float = tc["cooldown_ms"] / 1000.0
        self._last_fire:  Dict[str, float] = {}

        # Build tick sound
        self._tick = None
        if sc.get("enabled", True):
            self._tick = _make_tick(
                freq_hz    = sc.get("frequency_hz", 820),
                duration_ms= sc.get("duration_ms",  18),
                volume     = sc.get("volume",        0.55),
            )

    def should_fire(self, key_name: str) -> bool:
        """Return True if enough time has passed since the last fire for this key."""
        now  = time.monotonic()
        last = self._last_fire.get(key_name, 0.0)
        if now - last >= self._cooldown_s:
            self._last_fire[key_name] = now
            return True
        return False

    def play_tick(self) -> None:
        """Play the click sound (non-blocking)."""
        if self._tick is not None:
            try:
                self._tick.play()
            except Exception:
                pass

    def reset(self) -> None:
        self._last_fire.clear()
