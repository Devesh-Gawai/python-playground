#!/usr/bin/env python3
"""
LAN FPS - Game Server
----------------------
Runs entirely on the Python standard library. No "pip install" needed.

What it does:
  1. Serves the game (the files in the "client" folder) as a website.
  2. Keeps track of every connected player's position/health in memory
     and lets clients poll for updates, which is how multiplayer works.

How to run it:
  python3 server.py

Then on THIS laptop, open:  http://localhost:8000
On any OTHER phone/laptop on the same WiFi, open the "Network URL"
that this script prints when it starts.
"""

import http.server
import json
import os
import socket
import threading
import time
import uuid

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client")

# ---------------------------------------------------------------------------
# In-memory game state (thread-safe via a single lock)
# ---------------------------------------------------------------------------
state_lock = threading.Lock()
players = {}      # id -> {name, x, y, z, ry, health, kills, deaths, last_seen}
events = []       # list of {t, type, ...}  -- shots / hits / kills / joins / leaves
EVENT_TTL = 8.0    # seconds an event stays in the buffer
PLAYER_TIMEOUT = 15.0  # seconds without an update before a player is dropped


def now():
    return time.time()


def prune():
    """Remove stale players and old events. Must be called with the lock held."""
    t = now()
    dead_ids = [pid for pid, p in players.items() if t - p["last_seen"] > PLAYER_TIMEOUT]
    for pid in dead_ids:
        name = players[pid]["name"]
        del players[pid]
        events.append({"t": t, "type": "leave", "id": pid, "name": name})
    while events and t - events[0]["t"] > EVENT_TTL:
        events.pop(0)


def get_local_ip():
    """Best-effort way to find the LAN IP other devices should use."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def apply_health_update(p, new_health):
    """Update a player's health, granting brief spawn protection on respawn
    (health going from 0 back up). Must be called with the lock held."""
    new_health = max(0, min(100, int(new_health)))
    if p["health"] <= 0 and new_health > 0:
        p["spawn_protected_until"] = now() + 1.5
    p["health"] = new_health


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    # Quiet the default logging so the console stays readable.
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        # Never let a browser cache the game files or API responses — this
        # matters a lot on mobile browsers, which cache aggressively and
        # would otherwise keep serving an old, already-fixed version of the
        # game after you update these files.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def _send_json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ---------------- GET ----------------
    def do_GET(self):
        if self.path.startswith("/api/state"):
            return self.handle_state()
        if self.path.startswith("/api/events"):
            return self.handle_events()
        # Fall back to serving static files from the client/ folder.
        return super().do_GET()

    # ---------------- POST ----------------
    def do_POST(self):
        if self.path == "/api/join":
            return self.handle_join()
        if self.path == "/api/update":
            return self.handle_update()
        if self.path == "/api/sync":
            return self.handle_sync()
        if self.path == "/api/shoot":
            return self.handle_shoot()
        if self.path == "/api/hit":
            return self.handle_hit()
        if self.path == "/api/leave":
            return self.handle_leave()
        self._send_json({"error": "unknown endpoint"}, 404)

    # ---------------- API implementations ----------------
    def handle_join(self):
        data = self._read_json()
        name = str(data.get("name") or "Player")[:20]
        pid = uuid.uuid4().hex[:8]
        with state_lock:
            prune()
            players[pid] = {
                "id": pid, "name": name,
                "x": 0.0, "y": 1.6, "z": 0.0, "ry": 0.0,
                "health": 100, "kills": 0, "deaths": 0,
                "last_seen": now(),
                "spawn_protected_until": now() + 1.5,
            }
            events.append({"t": now(), "type": "join", "id": pid, "name": name})
        self._send_json({"id": pid})

    def handle_update(self):
        data = self._read_json()
        pid = data.get("id")
        with state_lock:
            prune()
            p = players.get(pid)
            if not p:
                return self._send_json({"error": "not joined"}, 400)
            for k in ("x", "y", "z", "ry"):
                if k in data:
                    p[k] = float(data[k])
            if "health" in data:
                apply_health_update(p, data["health"])
            p["last_seen"] = now()
        self._send_json({"ok": True})

    def handle_sync(self):
        """Combined endpoint: send our own position/health AND receive the
        current world state + new events, in a single round trip instead of
        three separate requests. This is what the game normally uses every
        tick; /api/update and /api/state/events still exist separately for
        one-off calls (e.g. the very first update right when entering play)."""
        data = self._read_json()
        pid = data.get("id")
        since = data.get("since", 0)
        try:
            since = float(since)
        except (TypeError, ValueError):
            since = 0.0
        with state_lock:
            prune()
            p = players.get(pid)
            if not p:
                return self._send_json({"error": "not joined"}, 400)
            for k in ("x", "y", "z", "ry"):
                if k in data:
                    p[k] = float(data[k])
            if "health" in data:
                apply_health_update(p, data["health"])
            p["last_seen"] = now()

            others = {opid: op for opid, op in players.items() if opid != pid}
            out_events = [e for e in events if e["t"] > since and e.get("id") != pid]
        self._send_json({"players": others, "events": out_events, "serverTime": now()})

    def handle_state(self):
        qs = self.path.split("?", 1)
        self_id = None
        if len(qs) > 1:
            for part in qs[1].split("&"):
                if part.startswith("id="):
                    self_id = part[3:]
        with state_lock:
            prune()
            others = {pid: p for pid, p in players.items() if pid != self_id}
        self._send_json({"players": others, "serverTime": now()})

    def handle_shoot(self):
        data = self._read_json()
        with state_lock:
            events.append({
                "t": now(), "type": "shoot",
                "id": data.get("id"),
                "ox": data.get("ox"), "oy": data.get("oy"), "oz": data.get("oz"),
                "dx": data.get("dx"), "dy": data.get("dy"), "dz": data.get("dz"),
            })
        self._send_json({"ok": True})

    def handle_hit(self):
        data = self._read_json()
        shooter_id = data.get("shooterId")
        target_id = data.get("targetId")
        damage = int(data.get("damage", 10))
        killed = False
        blocked = False
        with state_lock:
            target = players.get(target_id)
            shooter = players.get(shooter_id)
            if target:
                if now() < target.get("spawn_protected_until", 0):
                    blocked = True
                else:
                    was_alive = target["health"] > 0
                    target["health"] = max(0, target["health"] - damage)
                    if was_alive and target["health"] == 0:
                        killed = True
                        target["deaths"] += 1
                        if shooter:
                            shooter["kills"] += 1
                        events.append({
                            "t": now(), "type": "kill",
                            "killer": shooter["name"] if shooter else "Someone",
                            "victim": target["name"],
                        })
                    events.append({
                        "t": now(), "type": "hit",
                        "shooterId": shooter_id, "targetId": target_id, "damage": damage,
                    })
        self._send_json({"ok": True, "killed": killed, "blocked": blocked})

    def handle_leave(self):
        data = self._read_json()
        pid = data.get("id")
        with state_lock:
            if pid in players:
                name = players[pid]["name"]
                del players[pid]
                events.append({"t": now(), "type": "leave", "id": pid, "name": name})
        self._send_json({"ok": True})

    def handle_events(self):
        qs = self.path.split("?", 1)
        since = 0.0
        self_id = None
        if len(qs) > 1:
            for part in qs[1].split("&"):
                if part.startswith("since="):
                    try:
                        since = float(part[6:])
                    except ValueError:
                        since = 0.0
                if part.startswith("id="):
                    self_id = part[3:]
        with state_lock:
            out = [e for e in events if e["t"] > since and e.get("id") != self_id]
        self._send_json({"events": out, "serverTime": now()})


def main():
    if not os.path.isdir(STATIC_DIR):
        print(f"ERROR: could not find the 'client' folder next to server.py at {STATIC_DIR}")
        return

    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), GameHandler)
    local_ip = get_local_ip()

    print("=" * 60)
    print(" LAN FPS server is running")
    print("=" * 60)
    print(f" On THIS computer, open:      http://localhost:{PORT}")
    print(f" On OTHER devices (same WiFi): http://{local_ip}:{PORT}")
    print("=" * 60)
    print(" Press Ctrl+C to stop the server.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
