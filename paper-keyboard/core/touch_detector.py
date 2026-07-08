"""core/touch_detector.py — 5-layer velocity + acceleration touch validation.

Layers
------
L1  Spatial       – keyboard position (kx, ky) is within the valid key area
L2  Z-contact     – fingertip z OR tip-to-DIP image distance signals contact
L3  Downward vel  – fingertip was moving toward the paper in the past N frames
L4  Deceleration  – rate-of-change of z has dropped (finger has stopped)
L5  Stability     – (kx, ky) position has not drifted significantly
    + visibility  – MediaPipe confidence above threshold

A touch EVENT fires on the first frame where all 5 layers are satisfied
AND the debounce cooldown (managed by debounce.py) has expired.
"""
from __future__ import annotations

import collections
import math
import time
from dataclasses import dataclass, field
from typing import Deque, Optional, Tuple

from utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class TouchEvent:
    key_name:  str
    key_code:  str
    kx:        float
    ky:        float
    ts:        float = field(default_factory=time.time)


# ── Frame snapshot ────────────────────────────────────────────────────────────

@dataclass
class _Frame:
    # MediaPipe normalised image coords
    tip_x:  float
    tip_y:  float
    tip_z:  float
    dip_x:  float
    dip_y:  float
    palm_z: float
    # Derived
    img_dist:   float   # distance tip→DIP in image space
    z_score:    float   # tip_z - palm_z  (positive = tip below palm = toward paper)
    # Keyboard position (or None if not calibrated / out of range)
    kx: Optional[float]
    ky: Optional[float]
    # Visibility
    visible: bool
    ts: float


def _img_dist(tip_x, tip_y, dip_x, dip_y) -> float:
    return math.hypot(tip_x - dip_x, tip_y - dip_y)


# ── Detector ─────────────────────────────────────────────────────────────────

class TouchDetector:
    """Stateful detector — call update() with each incoming FingerPacket."""

    def __init__(self, cfg: dict):
        tc = cfg["touch"]
        self._z_thresh:      float = tc["z_contact_threshold"]
        self._img_thresh:    float = tc["img_dist_threshold"]
        self._vel_window:    int   = int(tc["velocity_window"])
        self._min_vel:       float = tc["min_downward_velocity"]
        self._stop_vel:      float = tc["stop_velocity_threshold"]
        self._stab_thresh:   float = tc["position_stability_px"]
        self._vis_thresh:    float = tc["visibility_threshold"]
        self._confirm_n:     int   = int(tc["confirm_frames"])

        self._history:   Deque[_Frame] = collections.deque(maxlen=max(self._vel_window + 2, 10))
        self._confirm:   int = 0        # consecutive frames passing all 5 layers

    # ── helpers ───────────────────────────────────────────────────────────

    def _z_velocity(self) -> Tuple[float, float]:
        """Return (mean_velocity, latest_velocity) of z_score over the window.
        Positive velocity = z_score increasing = finger moving toward paper."""
        hist = list(self._history)
        if len(hist) < 2:
            return 0.0, 0.0
        window = hist[-min(self._vel_window, len(hist)):]
        deltas = [window[i].z_score - window[i - 1].z_score
                  for i in range(1, len(window))]
        if not deltas:
            return 0.0, 0.0
        return sum(deltas) / len(deltas), deltas[-1]

    def _position_stable(self, kx: float, ky: float) -> bool:
        """True if recent kx/ky variance is below stability threshold."""
        hist = [f for f in self._history if f.kx is not None][-self._vel_window:]
        if len(hist) < 2:
            return True
        xs = [f.kx for f in hist]
        ys = [f.ky for f in hist]
        spread = max(max(xs) - min(xs), max(ys) - min(ys))
        return spread < self._stab_thresh

    # ── public ────────────────────────────────────────────────────────────

    def update(
        self,
        tip_x: float, tip_y: float, tip_z: float,
        dip_x: float, dip_y: float,
        palm_z: float,
        visible: bool,
        kx: Optional[float], ky: Optional[float],
        key_name: Optional[str], key_code: Optional[str],
    ) -> Optional[TouchEvent]:
        """Feed one frame. Returns a TouchEvent if a touch is detected, else None."""

        frame = _Frame(
            tip_x=tip_x, tip_y=tip_y, tip_z=tip_z,
            dip_x=dip_x, dip_y=dip_y,
            palm_z=palm_z,
            img_dist=_img_dist(tip_x, tip_y, dip_x, dip_y),
            z_score=tip_z - palm_z,
            kx=kx, ky=ky,
            visible=visible,
            ts=time.time(),
        )
        self._history.append(frame)

        # L1 – valid key position
        if kx is None or ky is None or key_name is None:
            self._confirm = 0
            return None

        # L5 – visibility
        if not visible:
            self._confirm = 0
            return None

        # L2 – contact signal (z OR image distance)
        z_contact   = frame.z_score > self._z_thresh
        img_contact = frame.img_dist < self._img_thresh
        if not (z_contact or img_contact):
            self._confirm = 0
            return None

        # L3 – downward velocity (mean positive over window)
        mean_vel, latest_vel = self._z_velocity()
        if mean_vel < self._min_vel:
            self._confirm = 0
            return None

        # L4 – deceleration (latest velocity dropping toward zero)
        if abs(latest_vel) > self._stop_vel * 3:
            # still moving fast — not a clean landing yet
            self._confirm = 0
            return None

        # L5b – position stability
        if not self._position_stable(kx, ky):
            self._confirm = 0
            return None

        # All 5 layers pass — accumulate confirmation frames
        self._confirm += 1
        if self._confirm >= self._confirm_n:
            self._confirm = 0   # reset so we don't re-fire next frame
            return TouchEvent(
                key_name=key_name,
                key_code=key_code or key_name,
                kx=kx,
                ky=ky,
            )

        return None

    def reset(self) -> None:
        self._history.clear()
        self._confirm = 0
