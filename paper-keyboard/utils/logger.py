"""utils/logger.py — Structured logging with rotating file handler."""
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_dir: str = "logs", level_name: str = "INFO") -> None:
    """Configure root logger with console + rotating file output."""
    os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, level_name.upper(), logging.INFO)

    log_file = os.path.join(
        log_dir,
        f"paper_keyboard_{datetime.now().strftime('%Y%m%d')}.log"
    )

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── Rotating file handler (10 MB × 5 backups) ──────────────────────────
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)

    # ── Console handler ─────────────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(level)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # avoid duplicate handlers on hot-reload
    root.handlers.clear()
    root.addHandler(fh)
    root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger."""
    return logging.getLogger(name)
