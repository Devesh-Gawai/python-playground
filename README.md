<div align="center">

<!-- ═══════════════════ BANNER ═══════════════════ -->

```
██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    P L A Y G R O U N D  —  build · break · learn
```

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Projects-3%20Active-2EA44F?style=for-the-badge&logo=github&logoColor=white"/>
  <img src="https://img.shields.io/badge/Domain-Games%20%7C%20CV%20%7C%20AI-FF6F00?style=for-the-badge&logo=lightning&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Actively%20Building-blueviolet?style=for-the-badge&logo=statuspage&logoColor=white"/>
  <img src="https://img.shields.io/github/stars/Devesh-Gawai/python-playground?style=for-the-badge&logo=github&color=yellow"/>
</p>

<p align="center">
  <strong>A collection of real, working Python projects — from browser FPS games to computer-vision input systems.</strong><br/>
  <em>Every project here is built from scratch, fully playable / runnable, and designed to push a concept as far as possible.</em>
</p>

<p align="center">
  <a href="#-paper-keyboard">📄 Paper Keyboard</a> &nbsp;·&nbsp;
  <a href="#-arena-strike">🎮 Arena Strike</a> &nbsp;·&nbsp;
  <a href="#-python-fps-survival">🔫 Python FPS Survival</a> &nbsp;·&nbsp;
  <a href="#-about-the-author">🧑‍💻 Author</a>
</p>

---

## 📦 Repository At a Glance

```
python-playground/
│
├── 📁 paper-keyboard/      ← Type on a printed sheet of paper with your phone camera
├── 📁 ARENA STRIKE/        ← Browser-based LAN multiplayer FPS (no installs for players)
├── 📁 first_game/          ← Desktop FPS survival shooter built in Python + Ursina
│
└── 📄 README.md            ← You are here
```

| # | Project | Category | Stack | Status |
|---|---------|----------|-------|--------|
| 01 | [📄 Paper Keyboard](#-paper-keyboard) | Computer Vision · Input System | Python · FastAPI · OpenCV · MediaPipe | `v1.0 — Stable` |
| 02 | [🎮 Arena Strike](#-arena-strike) | Web Game · Multiplayer | Three.js · Python HTTP · HTML/JS | `Playable` |
| 03 | [🔫 Python FPS Survival](#-python-fps-survival) | Desktop Game · AI | Python · Ursina Engine | `Playable` |

---

## 📄 Paper Keyboard

<p align="center">
  <img src="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/content-library/demonstration.gif" alt="Paper Keyboard Demo" width="750"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-ArUco%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/WebSocket-Real--Time-010101?style=for-the-badge&logo=socket.io&logoColor=white"/>
  <img src="https://img.shields.io/badge/Latency-~17ms-2EA44F?style=for-the-badge"/>
</p>

> **Type on paper. Control your computer. Zero hardware.**
> A printed A4 sheet + your smartphone + Python = a fully working keyboard.

### 💡 The Idea

What if you could keep the natural feeling of typing on a surface — without using an actual keyboard?

Paper Keyboard turns an ordinary printed sheet into a fully functional computer keyboard. Your **smartphone becomes the vision system**, your **finger becomes the input device**, and a **piece of paper** is the keyboard. Characters appear in *any* open app on your computer — Notepad, VS Code, your browser — in real time.

### 🔬 How It Works

```
╔══════════════════════════════════════════════════════════════════╗
║                    COMPLETE SIGNAL FLOW                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📱 PHONE (Overhead)               💻 COMPUTER                   ║
║  ├─ Camera captures paper          ├─ FastAPI + uvicorn server   ║
║  ├─ MediaPipe Hands (21 landmarks) ├─ ArUco marker detection     ║
║  ├─ Sends finger data via WS  ───► ├─ Homography calibration     ║
║  └─ Shows live hand skeleton       ├─ 5-Layer touch detection    ║
║                                    ├─ Keyboard key lookup        ║
║         📄 PAPER                   └─ pynput key injection       ║
║         ├─ ArUco markers (4 corners)          │                  ║
║         ├─ QWERTY layout printed              ▼                  ║
║         └─ Calibration reference      🖥️ Operating System        ║
║                   │                   └─ Characters typed in     ║
║     [Finger taps] │                      any open app            ║
║         ▼         ▼                                              ║
║  [5-Layer Validation] ──────────────────────► [KEY TYPED!]       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 🛡️ 5-Layer Touch Detection

Every keystroke passes through **5 independent validation layers** — preventing ghost presses, accidental touches, and adjacent-key confusion:

| Layer | Name | What it checks |
|-------|------|---------------|
| **L1** | Spatial | Finger is within the key's bounding box |
| **L2** | Z-Contact | Fingertip Z-depth signals contact with the surface |
| **L3** | Downward Velocity | Finger moving *toward* the paper (real key-press motion) |
| **L4** | Deceleration | Velocity dropping to zero — finger landing and stopping |
| **L5** | Stability + Visibility | Position is stable; MediaPipe confidence above threshold |

**All 5 must pass** before a keystroke fires.

### 📊 Performance

| Metric | Current |
|--------|---------|
| Touch Accuracy | 95 – 98% |
| End-to-End Latency | ~17 ms |
| Calibration Time | 2 – 3 seconds |
| Supported Keys | 68 (full QWERTY) |

### ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Server | Python · FastAPI · uvicorn |
| Vision (phone) | MediaPipe Tasks Vision · HTML5 Canvas |
| Vision (PC) | OpenCV 4.8 · ArUco marker detection · RANSAC Homography |
| Communication | WebSocket (JSON packets) |
| OS Control | pynput (native key injection) |
| Math | NumPy |

### 🚀 Quick Start

```bash
git clone https://github.com/Devesh-Gawai/python-playground.git
cd python-playground/paper-keyboard
pip install -r requirements.txt
python main.py
# → Open the printed URL on your phone, tap CALIBRATE, start typing!
```

<p align="center">
  <a href="https://github.com/Devesh-Gawai/python-playground/tree/main/paper-keyboard">
    <img src="https://img.shields.io/badge/📁%20View%20Full%20Source-paper--keyboard-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://youtu.be/SAW4xdRyefo">
    <img src="https://img.shields.io/badge/▶%20Watch%20on%20YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
  </a>
</p>

---

## 🎮 Arena Strike

<p align="center">
  <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/ARENA%20STRIKE/demo.gif?raw=true" alt="Arena Strike Demo" width="750"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Three.js-3D%20Engine-000000?style=for-the-badge&logo=threedotjs&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-HTTP%20Server-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Multiplayer-LAN%20Party-E74C3C?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Any%20Browser-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/Install-Zero%20(for%20players)-2EA44F?style=for-the-badge"/>
</p>

> **A first-person shooter that runs in any web browser — no installs, no accounts, no app stores.**
> One person starts the server; everyone else just opens a URL.

### 💡 The Idea

A fully 3D LAN multiplayer shooter you can have running in under two minutes — playable on any device with a browser. Players on phones get auto-detected touch controls; players on laptops get mouse-and-keyboard. The host laptop is the server; everyone else connects by typing a single URL.

### 🏗️ Architecture

```
HOST LAPTOP
  │
  ├── python3 server.py  ──►  serves client/ files over HTTP
  │                           handles multiplayer state (polling, ~20×/sec)
  │
  └── http://localhost:8000         ← host opens this
      http://192.168.x.x:8000      ← everyone else opens this

PLAYERS (any device, any OS, any browser)
  │
  ├── 💻 Laptop/Desktop  →  Mouse + WASD keyboard controls
  └── 📱 Phone/Tablet    →  Auto-detected on-screen joystick + buttons
```

### 🕹️ Game Modes

| Mode | Description |
|------|-------------|
| **Single Player** | You vs 5 AI bots — bots respawn and hunt you down |
| **Multiplayer** | Everyone on the same WiFi plays in the same arena, live |

### 🎮 Controls

| Platform | Movement | Look | Fire | Jump | Reload |
|----------|----------|------|------|------|--------|
| Desktop | `W A S D` + `Shift` (sprint) | Mouse | Hold `Left Click` | `Space` | `R` |
| Mobile | On-screen joystick (bottom-left) | Drag right side | `FIRE` button | `JUMP` button | `RELOAD` button |

### ⚡ Multiplayer Engine

```
OLD (3 HTTP requests per update cycle):
  GET /state  +  POST /position  +  POST /shoot  =  ~3× network overhead

NEW (single combined request, ~20×/sec):
  POST /sync  →  send + receive in one round-trip  =  far lower lag

Also added:
  ✓ Auto-reconnect if session expires on menu/loading screen
  ✓ Spawn protection (1.5 s invincibility) — standard shooter convention
  ✓ No-cache headers — you always load the latest version instantly
```

### 🚀 Quick Start

```bash
git clone https://github.com/Devesh-Gawai/python-playground.git
cd "python-playground/ARENA STRIKE"
python3 server.py
# → Open the localhost URL on this machine, share the network URL with others
```

No pip installs. No npm. No account. Pure Python + browser.

<p align="center">
  <a href="https://github.com/Devesh-Gawai/python-playground/tree/main/ARENA%20STRIKE">
    <img src="https://img.shields.io/badge/📁%20View%20Full%20Source-ARENA%20STRIKE-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
</p>

---

## 🔫 Python FPS Survival

<p align="center">
  <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/first_game/gameplay.gif?raw=true" alt="Python FPS Survival gameplay" width="750"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ursina-Game%20Engine-6C5CE7?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Genre-FPS%20Survival-E74C3C?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/AI-Enemy%20Pursuit-FF6F00?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Playable-2EA44F?style=for-the-badge"/>
</p>

> **A fast-paced desktop FPS survival game built entirely in Python.**
> Enemies spawn, advance, and hunt you down — survive as long as possible and push your score.

### 💡 The Idea

Core idea: **simple systems + responsive controls + escalating difficulty = an addictive survival loop.**

The game drops you into an open arena where enemies continuously spawn within a **120° front-facing combat cone**, move toward you, and get faster the longer you survive. One run is all it takes to get hooked.

### 🧠 Gameplay Loop

```
        ┌───────────────┐
        │     AIM       │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │    SHOOT      │  ← Raycast hit detection
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │  ELIMINATE    │  → +100 SCORE
        │    ENEMY      │  → enemy removed
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │  MORE ENEMIES │  → spawning faster
        │  MORE SPEED   │  → speed = 2.0 + (time × 0.05) + (score × 0.005)
        └───────┬───────┘
                │
                └──────────► REPEAT until GAME OVER → press R to restart
```

### 🎯 120° Front Combat System

Enemies don't spawn randomly around the map — they always appear from the **front-facing 120° arc**. This is both a design and a math decision:

```
-60°  ◄──────────  0°  ──────────►  +60°
                 PLAYER
              (you face here)
```

Game Over triggers only when an enemy from that same cone reaches you:

```python
if forward_vector.dot(to_enemy) >= 0.5:   # cos(60°) = 0.5
    trigger_game_over()
```

### 📈 Dynamic Difficulty

```python
current_speed = 2.0 + (game_time * 0.05) + (score * 0.005)
```

Every elimination raises your score → raises enemy speed. Surviving longer also raises speed independently. The two axes of pressure combine into a tight risk/reward loop.

### 🧩 Feature Table

| System | Implementation |
|--------|---------------|
| 🎯 Controls | Ursina `FirstPersonController` |
| 🔫 Shooting | Mouse-click raycast hit detection |
| 💥 Muzzle Flash | Visual feedback on every shot |
| ✨ Hit Effect | Glowing sphere on impact |
| 👾 Enemy AI | Continuous look-at + forward pursuit |
| 🧵 Spawner | Background thread, one enemy every ~1.5 s |
| 📈 Difficulty | Time + score compound formula |
| 🏆 Scoring | +100 per elimination, live HUD |
| 💀 Game State | Playing → Game Over → R to restart |
| 💡 Rendering | Ursina lit-with-shadows shader |

### 🚀 Quick Start

```bash
git clone https://github.com/Devesh-Gawai/python-playground.git
cd python-playground
pip install ursina
python first_game/game.py
```

<p align="center">
  <a href="https://github.com/Devesh-Gawai/python-playground/tree/main/first_game">
    <img src="https://img.shields.io/badge/📁%20View%20Full%20Source-first__game-181717?style=for-the-badge&logo=github&logoColor=white"/>
  </a>
</p>

---

## 🛠️ Tech Landscape

A birds-eye view of everything used across the playground:

```
╔══════════════════════════════════════════════════════════════════════╗
║                     PYTHON PLAYGROUND — TECH MAP                     ║
╠═══════════════╦══════════════════╦═══════════════════════════════════╣
║  LAYER        ║  PAPER KEYBOARD  ║  ARENA STRIKE    PYTHON FPS       ║
╠═══════════════╬══════════════════╬════════════════╦══════════════════╣
║  Language     ║  Python 3.8+     ║  Python 3 (srv)║  Python 3.x      ║
║  3D / Visual  ║  OpenCV          ║  Three.js       ║  Ursina Engine   ║
║  Server       ║  FastAPI/uvicorn ║  http.server    ║  —               ║
║  Comms        ║  WebSocket       ║  HTTP polling   ║  —               ║
║  Vision / AI  ║  MediaPipe       ║  —              ║  Raycasting      ║
║  Math         ║  NumPy / homog.  ║  Vector math    ║  Dot products    ║
║  OS Control   ║  pynput          ║  —              ║  —               ║
║  Client       ║  Phone browser   ║  Any browser    ║  Desktop         ║
║  Frontend     ║  HTML5 Canvas    ║  HTML/CSS/JS    ║  Ursina HUD      ║
╚═══════════════╩══════════════════╩════════════════╩══════════════════╝
```

**Badges across the whole repo:**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-FF6F00?style=flat-square&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Three.js-000000?style=flat-square&logo=threedotjs&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ursina-6C5CE7?style=flat-square&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/WebSocket-010101?style=flat-square&logo=socket.io&logoColor=white"/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>
  <img src="https://img.shields.io/badge/pynput-grey?style=flat-square&logo=keyboard&logoColor=white"/>
</p>

---

## ⚡ Clone & Run Any Project

```bash
# ── Clone the entire playground ──────────────────────────────────
git clone https://github.com/Devesh-Gawai/python-playground.git
cd python-playground

# ── Paper Keyboard ───────────────────────────────────────────────
cd paper-keyboard
pip install -r requirements.txt
python main.py

# ── Arena Strike (browser FPS) ───────────────────────────────────
cd "../ARENA STRIKE"
python3 server.py                # open localhost:8000 in your browser

# ── Python FPS Survival (desktop) ───────────────────────────────
cd ..
pip install ursina
python first_game/game.py
```

---

## 🗺️ What's Coming

```
PYTHON PLAYGROUND — ROADMAP
│
├── 📄 Paper Keyboard
│   ├── [v1.1]  150+ WPM speed · haptic feedback · adaptive drift correction
│   ├── [v1.5]  Two-finger typing · gesture shortcuts · multi-layout support
│   └── [v2.0]  ML touch model · offline mobile app · 10-finger support
│
├── 🎮 Arena Strike
│   ├── More weapons & maps
│   ├── Better bot AI
│   └── Sound effects + ambient audio
│
└── 🔫 Python FPS Survival
    ├── Multiple enemy types & wave-based difficulty
    ├── Health / armor system
    ├── Ammunition & reload mechanics
    └── High-score persistence
```

---

## 🧑‍💻 About the Author

<p align="center">
  <img src="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/content-library/solo.jpeg" alt="Devesh Kumar Gawai" width="150" style="border-radius: 50%;"/>
</p>

<p align="center">
  <strong>Devesh Kumar Gawai</strong><br/>
  Developer | Builder | Curious Learner
</p>

<p align="center">
  <em>"Learning one project at a time."</em>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/devesh-kumar-gawai-134346320">
    <img src="https://img.shields.io/badge/LinkedIn-Devesh%20Kumar%20Gawai-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://youtu.be/SAW4xdRyefo">
    <img src="https://img.shields.io/badge/YouTube-Watch%20Explanation-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/>
  </a>
  &nbsp;
  <a href="https://forms.gle/urB5CHxcRd7BSoAf9">
    <img src="https://img.shields.io/badge/Google%20Form-Contact%20Me-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  </a>
</p>

<p align="center">
  This playground exists because I believe the best way to learn is to <strong>build real things</strong> — not toy examples, but actual working software that solves a problem or creates an experience. Every project here started with a question:
</p>

<p align="center">
  <em>Paper Keyboard → "What if a piece of paper was a keyboard?"</em><br/>
  <em>Arena Strike → "Can I run a real multiplayer shooter with nothing but Python and a browser?"</em><br/>
  <em>Python FPS Survival → "How far can I push a game with just Python and a game engine?"</em>
</p>

<p align="center">
  The answers are all in this repo. ⭐
</p>

---

## 📬 Contact & Feedback

<p align="center">
  <a href="https://forms.gle/urB5CHxcRd7BSoAf9">
    <img src="https://img.shields.io/badge/📩%20Send%20Feedback%20or%20a%20Question-Google%20Form-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  </a>
</p>

| Channel | Link |
|---------|------|
| 💼 LinkedIn | [devesh-kumar-gawai-134346320](https://www.linkedin.com/in/devesh-kumar-gawai-134346320) |
| 🐛 GitHub Issues | [Report a bug](../../issues) |
| 💬 GitHub Discussions | [Ask a question](../../discussions) |
| 📋 Contact Form | [Google Form](https://forms.gle/urB5CHxcRd7BSoAf9) |

---

<p align="center">
  <strong>⭐ If any project here helped or inspired you, a star means a lot — it keeps the building going.</strong>
</p>

<p align="center">
  <sub>Built with Python · curiosity · and a refusal to stop at "good enough"</sub>
</p>
