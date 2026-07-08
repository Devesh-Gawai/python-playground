"""main.py — Paper Keyboard entry point.

Run:  python main.py
Then open the printed URL on your phone browser.
"""
from __future__ import annotations

import json
import socket
import sys
from pathlib import Path


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.json"
    with open(cfg_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _print_qr(url: str) -> None:
    """Print a QR code for the URL using the qrcode library (optional)."""
    try:
        import qrcode                                   # type: ignore
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except ImportError:
        pass  # qrcode not installed — skip
    except Exception:
        pass


def _banner(url: str) -> None:
    sep = "─" * 54
    print(f"\n  🖐️   Paper Keyboard Server")
    print(f"  {sep}")
    print(f"  📡  Listening on : {url}")
    print(f"  📱  Open on phone: {url}")
    print(f"  {sep}")
    print()
    _print_qr(url)
    print()
    print("  Workflow:")
    print("  1. Mount phone overhead so all 4 ArUco markers are visible")
    print("  2. Tap CALIBRATE in the phone browser")
    print("  3. Start typing on the paper keyboard!")
    print(f"\n  {sep}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    config = _load_config()

    # Logging must be set up BEFORE any module imports that call get_logger()
    from utils.logger import setup_logging
    setup_logging(
        log_dir    = config["logging"]["log_dir"],
        level_name = config["logging"]["level"],
    )

    from utils.logger import get_logger
    log = get_logger("main")
    log.info("Paper Keyboard starting …")

    # Print banner AFTER logging so console output is ordered nicely
    host = config["server"]["host"]
    port = config["server"]["port"]
    ip   = _get_local_ip()
    url  = f"http://{ip}:{port}"
    _banner(url)

    # Create FastAPI app (initialises all core modules)
    from networking.server import create_app
    app = create_app(config)

    import uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="warning",   # uvicorn's own logger — keep quiet; ours handles it
        access_log=False,
    )


if __name__ == "__main__":
    main()
