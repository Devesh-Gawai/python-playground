"""networking/server.py — FastAPI WebSocket hub + /calibrate REST endpoint.

Connection lifecycle
--------------------
  1. Phone opens GET /           → receives index.html
  2. Phone opens WS  /ws         → enters tracking loop
  3. Phone POSTs  /calibrate     → Python detects ArUco, returns homography result
  4. Every frame: phone sends FingerPacket → server processes → optionally
     broadcasts KeyEventPacket back to the same client

All heavy CV work is dispatched to a thread-pool executor so the async
event loop stays responsive.
"""
from __future__ import annotations

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

import core.calibration  as calibration
import core.keyboard_map as keyboard_map
import core.typer        as typer
from core.debounce       import Debouncer
from core.touch_detector import TouchDetector
from networking.models   import (
    CalibrationRequest, CalibrationResult,
    FingerPacket, KeyEventPacket, PongPacket,
    StatusPacket, ErrorPacket, parse_incoming,
)
from utils.diagnostics import Diagnostics
from utils.logger      import get_logger

log = get_logger(__name__)

# Populated by init()
_config:    dict = {}
_debouncer: Debouncer | None = None
_diag:      Diagnostics | None = None
_executor   = ThreadPoolExecutor(max_workers=2)

# One TouchDetector per active WebSocket connection
_connections: Set[WebSocket] = set()


# ── App factory ───────────────────────────────────────────────────────────────

def create_app(config: dict) -> FastAPI:
    global _config, _debouncer, _diag

    _config    = config
    _debouncer = Debouncer(config)
    _diag      = Diagnostics(config["diagnostics"])

    keyboard_map.init(config)

    app = FastAPI(title="PaperKeyboard", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static serving ────────────────────────────────────────────────────

    @app.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(Path(__file__).parent.parent / "index.html",
                            media_type="text/html")

    # ── Calibration REST ──────────────────────────────────────────────────

    @app.post("/calibrate")
    async def calibrate(req: CalibrationRequest) -> JSONResponse:
        loop = asyncio.get_running_loop()
        result: dict = await loop.run_in_executor(
            _executor,
            lambda: calibration.calibrate_from_b64(req.image, req.width, req.height),
        )
        status_code = 200 if result["ok"] else 422
        return JSONResponse(content=result, status_code=status_code)

    # ── WebSocket ─────────────────────────────────────────────────────────

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        _connections.add(ws)
        log.info("WS client connected  (total=%d)", len(_connections))

        # Per-connection touch detector (stateful history)
        detector = TouchDetector(_config)

        # Send initial status so the phone knows the server is alive
        await _send(ws, StatusPacket(
            calibrated=calibration.is_calibrated(),
            fps=0.0,
            avg_latency_ms=0.0,
        ).model_dump())

        last_status_ts = time.monotonic()

        try:
            while True:
                raw = await ws.receive_text()
                recv_ts = time.monotonic()

                pkt = parse_incoming(raw)
                if pkt is None:
                    await _send(ws, ErrorPacket(message="Unknown packet type").model_dump())
                    continue

                # ── Ping / pong ───────────────────────────────────────────
                if pkt.type == "ping":
                    await _send(ws, PongPacket(
                        client_ts=pkt.ts,
                        server_ts=int(time.time() * 1000),
                    ).model_dump())
                    continue

                # ── Finger tracking packet ────────────────────────────────
                fp: FingerPacket = pkt  # type: ignore[assignment]

                # Measure round-trip latency (client ts → server recv)
                latency_ms = (recv_ts * 1000) - fp.ts
                if _diag:
                    _diag.tick(latency_ms=latency_ms)

                # Map fingertip to keyboard coords
                kx: float | None = None
                ky: float | None = None
                key_dict = None

                if calibration.is_calibrated() and fp.visible:
                    pos = calibration.transform_finger(fp.tip.x, fp.tip.y)
                    if pos:
                        kx, ky = pos
                        key_dict = keyboard_map.get_key_at(kx, ky)

                # Touch detection
                event = detector.update(
                    tip_x=fp.tip.x, tip_y=fp.tip.y, tip_z=fp.tip.z,
                    dip_x=fp.dip.x, dip_y=fp.dip.y,
                    palm_z=fp.palm_z,
                    visible=fp.visible,
                    kx=kx, ky=ky,
                    key_name=key_dict["name"]  if key_dict else None,
                    key_code=key_dict["code"]  if key_dict else None,
                )

                if event and _debouncer and _debouncer.should_fire(event.key_name):
                    log.info("🔑  %s  (kx=%.3f ky=%.3f)", event.key_name, event.kx, event.ky)
                    _debouncer.play_tick()
                    # Inject key in thread pool (pynput blocks briefly)
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(_executor, typer.type_key, event.key_code)
                    # Notify phone
                    await _send(ws, KeyEventPacket(
                        key=event.key_name,
                        kx=round(event.kx, 4),
                        ky=round(event.ky, 4),
                    ).model_dump())

                # Periodic status broadcast (~1 Hz)
                now = time.monotonic()
                if now - last_status_ts >= 1.0:
                    last_status_ts = now
                    stats = _diag.stats() if _diag else {}
                    await _send(ws, StatusPacket(
                        calibrated=calibration.is_calibrated(),
                        fps=stats.get("fps", 0.0),
                        avg_latency_ms=stats.get("avg_latency_ms", 0.0),
                    ).model_dump())

        except WebSocketDisconnect:
            log.info("WS client disconnected")
        except Exception as exc:
            log.error("WS error: %s", exc, exc_info=True)
        finally:
            _connections.discard(ws)
            log.info("WS cleanup done  (remaining=%d)", len(_connections))

    return app


# ── Helper ────────────────────────────────────────────────────────────────────

async def _send(ws: WebSocket, data: dict) -> None:
    """Send JSON to a single WebSocket, swallowing send errors."""
    try:
        await ws.send_text(json.dumps(data))
    except Exception as exc:
        log.debug("WS send failed: %s", exc)
