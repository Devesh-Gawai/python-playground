"""networking/models.py — Pydantic schemas + packet validation for every message type."""
from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


# ── Phone → Server ───────────────────────────────────────────────────────────

class LandmarkPoint(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    z: float  # MediaPipe depth; range ~(-0.3, +0.3) – not clamped


class FingerPacket(BaseModel):
    """Sent every animation frame once connected."""
    type: Literal["finger"]
    tip:      LandmarkPoint          # Landmark 8  – index fingertip
    dip:      LandmarkPoint          # Landmark 7  – index DIP joint
    pip:      LandmarkPoint          # Landmark 6  – index PIP joint
    mcp:      LandmarkPoint          # Landmark 5  – index MCP (knuckle)
    wrist:    LandmarkPoint          # Landmark 0  – wrist
    palm_z:   float                  # mean z of landmarks 0,5,9,13,17
    visible:  bool
    ts:       int                    # client unix-ms timestamp


class CalibrationRequest(BaseModel):
    """One-shot POST body for ArUco calibration."""
    image:  str   # base64 JPEG
    width:  int   # frame pixel width
    height: int   # frame pixel height

    @field_validator("image")
    @classmethod
    def image_nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("image must not be empty")
        return v


class PingPacket(BaseModel):
    type: Literal["ping"]
    ts:   int


# ── Server → Phone ───────────────────────────────────────────────────────────

class CalibrationResult(BaseModel):
    type:    Literal["calibration_result"] = "calibration_result"
    ok:      bool
    message: str
    detected_markers: List[int] = []


class KeyEventPacket(BaseModel):
    type:    Literal["key_event"] = "key_event"
    key:     str          # display name, e.g. "A", "Space", "Enter"
    kx:      float        # keyboard-normalised x (0-1)
    ky:      float        # keyboard-normalised y (0-1)


class StatusPacket(BaseModel):
    type:       Literal["status"] = "status"
    calibrated: bool
    fps:        float
    avg_latency_ms: float


class PongPacket(BaseModel):
    type:        Literal["pong"] = "pong"
    client_ts:   int
    server_ts:   int


class ErrorPacket(BaseModel):
    type:    Literal["error"] = "error"
    message: str


# ── Helper ───────────────────────────────────────────────────────────────────

def parse_incoming(raw: str) -> FingerPacket | PingPacket | None:
    """Parse a raw JSON string from the WebSocket into a typed model.
    Returns None if the packet type is unknown or malformed."""
    import json
    try:
        data = json.loads(raw)
        t = data.get("type")
        if t == "finger":
            return FingerPacket(**data)
        if t == "ping":
            return PingPacket(**data)
    except Exception:
        pass
    return None
