"""utils/diagnostics.py — FPS counter, latency tracker, periodic reporter."""
import time
import collections
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class FPSCounter:
    """Rolling-window FPS counter."""

    def __init__(self, window: int = 60):
        self._ts: collections.deque = collections.deque(maxlen=window)

    def tick(self) -> None:
        self._ts.append(time.perf_counter())

    @property
    def fps(self) -> float:
        if len(self._ts) < 2:
            return 0.0
        span = self._ts[-1] - self._ts[0]
        return (len(self._ts) - 1) / span if span > 0 else 0.0


class LatencyTracker:
    """Rolling-window latency stats (milliseconds)."""

    def __init__(self, window: int = 120):
        self._samples: collections.deque = collections.deque(maxlen=window)

    def record(self, ms: float) -> None:
        self._samples.append(ms)

    @property
    def avg_ms(self) -> float:
        return sum(self._samples) / len(self._samples) if self._samples else 0.0

    @property
    def max_ms(self) -> float:
        return max(self._samples) if self._samples else 0.0

    @property
    def p95_ms(self) -> float:
        if not self._samples:
            return 0.0
        sorted_s = sorted(self._samples)
        idx = int(len(sorted_s) * 0.95)
        return sorted_s[min(idx, len(sorted_s) - 1)]


class Diagnostics:
    """Aggregates FPS + latency and logs a summary every N seconds."""

    def __init__(self, cfg: dict):
        self.enabled: bool = cfg.get("enabled", True)
        self._interval: float = cfg.get("fps_log_interval_s", 5.0)
        self.fps = FPSCounter()
        self.latency = LatencyTracker()
        self._last_log: float = time.time()

    def tick(self, latency_ms: Optional[float] = None) -> None:
        if not self.enabled:
            return
        self.fps.tick()
        if latency_ms is not None:
            self.latency.record(latency_ms)
        now = time.time()
        if now - self._last_log >= self._interval:
            self._last_log = now
            log.info(
                f"FPS={self.fps.fps:.1f}  "
                f"latency avg={self.latency.avg_ms:.1f}ms  "
                f"p95={self.latency.p95_ms:.1f}ms  "
                f"max={self.latency.max_ms:.1f}ms"
            )

    def stats(self) -> dict:
        return {
            "fps": round(self.fps.fps, 1),
            "avg_latency_ms": round(self.latency.avg_ms, 1),
            "p95_latency_ms": round(self.latency.p95_ms, 1),
        }
