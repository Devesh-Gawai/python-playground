"""core/calibration.py — ArUco detection + homography matrix computation.

Workflow
--------
1. Phone POSTs a base-64 JPEG frame to /calibrate.
2. calibrate_from_b64() decodes it, detects the four ArUco markers
   (IDs 0-3, one at each corner of the printed template), and computes
   a perspective-homography H that maps camera-pixel coords → normalised
   keyboard coords  (0,0) = top-left marker  →  (1,1) = bottom-right marker.
3. transform_finger() applies H each frame to map MediaPipe fingertip
   positions (normalised 0-1 image coords) → keyboard coords.
"""
from __future__ import annotations

import base64
import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

log = logging.getLogger(__name__)

# ── ArUco setup ──────────────────────────────────────────────────────────────
_DICT   = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
_PARAMS = cv2.aruco.DetectorParameters()

# Destination points in normalised keyboard space for each marker ID.
# ID 0 → top-left (0,0), ID 1 → top-right (1,0),
# ID 2 → bottom-left (0,1), ID 3 → bottom-right (1,1).
_DST: Dict[int, np.ndarray] = {
    0: np.array([0.0, 0.0], dtype=np.float32),
    1: np.array([1.0, 0.0], dtype=np.float32),
    2: np.array([0.0, 1.0], dtype=np.float32),
    3: np.array([1.0, 1.0], dtype=np.float32),
}


# ── Module-level calibration state ───────────────────────────────────────────
class _State:
    homography:   Optional[np.ndarray] = None
    frame_width:  int = 1280
    frame_height: int = 720
    calibrated:   bool = False
    marker_ids:   List[int] = []

    def reset(self) -> None:
        self.homography   = None
        self.calibrated   = False
        self.marker_ids   = []


_state = _State()


# ── Internal helpers ─────────────────────────────────────────────────────────

def _detect(image: np.ndarray) -> Tuple[List, Optional[np.ndarray]]:
    """Return (corners, ids) from an OpenCV BGR image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(_DICT, _PARAMS)
    corners, ids, _ = detector.detectMarkers(gray)
    return corners, ids


def _compute_homography(
    corners: List, ids: np.ndarray
) -> Optional[np.ndarray]:
    """Given ArUco corners + ids, compute the homography H:
    camera_pixel → normalised keyboard (0-1)."""
    flat_ids = ids.flatten().tolist()
    required = set(_DST.keys())
    if not required.issubset(set(flat_ids)):
        return None

    src_pts, dst_pts = [], []
    for marker_id, dst in _DST.items():
        idx     = flat_ids.index(marker_id)
        corner  = corners[idx][0]            # shape (4, 2)
        center  = corner.mean(axis=0)        # marker centre in pixels
        src_pts.append(center)
        dst_pts.append(dst)

    src = np.array(src_pts, dtype=np.float32)
    dst = np.array(dst_pts, dtype=np.float32)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if H is None or mask is None or mask.sum() < 4:
        return None
    return H


# ── Public API ────────────────────────────────────────────────────────────────

def calibrate_from_b64(image_b64: str, width: int, height: int) -> dict:
    """Decode a base-64 JPEG, detect ArUco markers, compute homography.

    Returns a dict with keys: ok (bool), message (str), detected_markers (list).
    On success also stores the homography in module state.
    """
    _state.reset()

    try:
        raw   = base64.b64decode(image_b64)
        arr   = np.frombuffer(raw, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception as exc:
        return {"ok": False, "message": f"Image decode failed: {exc}", "detected_markers": []}

    if image is None:
        return {"ok": False, "message": "cv2.imdecode returned None", "detected_markers": []}

    corners, ids = _detect(image)

    if ids is None:
        return {"ok": False, "message": "No ArUco markers detected", "detected_markers": []}

    found = ids.flatten().tolist()
    log.info("ArUco markers detected: %s", found)

    if len(found) < 4:
        missing = sorted(set(_DST.keys()) - set(found))
        return {
            "ok": False,
            "message": f"Only {len(found)}/4 markers found. Missing IDs: {missing}",
            "detected_markers": found,
        }

    H = _compute_homography(corners, ids)
    if H is None:
        return {
            "ok": False,
            "message": "Homography computation failed (collinear markers?)",
            "detected_markers": found,
        }

    _state.homography   = H
    _state.frame_width  = width
    _state.frame_height = height
    _state.calibrated   = True
    _state.marker_ids   = found

    log.info("Calibration OK — frame %dx%d, H=\n%s", width, height, H)
    return {"ok": True, "message": "Calibration successful", "detected_markers": found}


def is_calibrated() -> bool:
    return _state.calibrated


def transform_finger(norm_x: float, norm_y: float) -> Optional[Tuple[float, float]]:
    """Map a MediaPipe normalised fingertip (0-1 in image) to keyboard coords (0-1).

    Returns None if not calibrated.
    """
    if not _state.calibrated or _state.homography is None:
        return None

    # Convert normalised → pixel
    px = norm_x * _state.frame_width
    py = norm_y * _state.frame_height

    pt = np.array([[[px, py]]], dtype=np.float32)
    dst = cv2.perspectiveTransform(pt, _state.homography)
    kx, ky = float(dst[0, 0, 0]), float(dst[0, 0, 1])

    # FIX: Invert X-axis because camera feed is mirrored
    kx = 1.0 - kx
    
    return kx, ky


def get_state_summary() -> dict:
    return {
        "calibrated":      _state.calibrated,
        "frame_size":      [_state.frame_width, _state.frame_height],
        "marker_ids":      _state.marker_ids,
    }
