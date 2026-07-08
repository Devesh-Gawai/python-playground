<p align="center">
  <img src="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/assets/keyboard_format.png" alt="Paper Keyboard Template" width="700"/>
</p>

<h1 align="center">📄 Paper Keyboard</h1>

<p align="center">
  <strong>Type on paper. Control your computer. Zero hardware required.</strong><br/>
  A printed sheet + your smartphone + Python = a fully working keyboard.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Version%201.0-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

---

## 🎬 See It In Action

<p align="center">
  <img src="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/content-library/demonstration.gif" alt="Paper Keyboard Live Demo" width="700"/>
</p>

<p align="center">
  <a href="https://youtu.be/SAW4xdRyefo">
    <img src="https://img.shields.io/badge/▶%20Watch%20Full%20Explanation%20on%20YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube Explanation"/>
  </a>
</p>

<p align="center">
  <a href="https://github.com/Devesh-Gawai/python-playground/blob/main/paper-keyboard/content-library/explanation.mp4">📽️ Watch Explanation Video (GitHub)</a>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <a href="https://github.com/Devesh-Gawai/python-playground/blob/main/paper-keyboard/content-library/demonstration.mp4">🎥 Watch Demonstration Video (GitHub)</a>
</p>

---

## 💡 What is Paper Keyboard?

**Paper Keyboard** is a touchless typing system that converts an ordinary A4 printed sheet into a fully functional computer keyboard — no Bluetooth, no sensors, no expensive hardware.

Your **smartphone becomes the vision system**, your **finger becomes the input device**, and a **simple piece of paper** becomes the keyboard.

> *"What if I could keep the natural feeling of typing on a surface — without using an actual keyboard?"*
> That single question started this entire project.

---

## ✨ Features at a Glance

| 🎯 Core | 🔧 Technical |
|--------|------------|
| ✅ Full QWERTY layout (68 keys) | ✅ Real-time ArUco marker detection |
| ✅ Tap to type on any application | ✅ Perspective homography calibration |
| ✅ Works in Notepad, VS Code, Browser | ✅ MediaPipe 21-landmark hand tracking |
| ✅ Calibrates in under 3 seconds | ✅ 5-layer touch validation engine |
| ✅ No cloud — fully local processing | ✅ WebSocket real-time communication |
| ✅ ~17ms end-to-end latency | ✅ pynput native OS key injection |
| ✅ Sub-100ms touch response | ✅ Per-key cooldown anti-repeat |
| ✅ Works with most smartphones | ✅ Structured logging & diagnostics |

---

## 🧠 How It Works

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
║                   │                   └─ Characters type in      ║
║     [Finger taps] │                      any open app            ║
║         ▼         ▼                                              ║
║  [5-Layer Validation] ──────────────────────► [KEY TYPED!]       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### 🛡️ The 5-Layer Touch Detection System

Every keystroke must pass through **5 independent validation layers**:

| Layer | Name | What It Checks |
|-------|------|---------------|
| **L1** | Spatial | Finger is within key bounding box |
| **L2** | Z-Contact | Fingertip Z-depth or distance to DIP joint signals contact |
| **L3** | Downward Velocity | Finger moving toward the paper (simulates a real key press) |
| **L4** | Deceleration | Velocity dropping toward zero (finger landing and stopping) |
| **L5** | Stability + Visibility | Position is stable; MediaPipe confidence is high |

**All 5 must pass** before a keystroke fires — preventing ghost presses, accidental touches, and adjacent key confusion.

---

## 📁 Project Structure

<p align="center">
  <img src="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/content-library/paper_keyboard_file_structure.png" alt="Paper Keyboard File Structure" width="700"/>
</p>

```
paper_keyboard/
│
├── 📄 main.py                   ← Entry point — run this to start
├── 📄 index.html                ← Mobile web app (camera + hand tracking UI)
├── ⚙️  config.json               ← All tunable settings (no code edits needed)
├── 📋 requirements.txt           ← Python dependencies
│
├── 📁 core/                      ← All processing logic
│   ├── calibration.py           → ArUco detection + homography matrix
│   ├── keyboard_map.py          → 68-key QWERTY bounding box layout
│   ├── touch_detector.py        → 5-layer touch validation
│   ├── debounce.py              → Per-key cooldown + tick sound
│   └── typer.py                 → pynput OS key injection
│
├── 📁 networking/                ← Server and communication
│   ├── server.py                → FastAPI + WebSocket hub
│   └── models.py                → Pydantic packet schemas
│
├── 📁 utils/                     ← Utilities
│   ├── logger.py                → Structured rotating-file logger
│   └── diagnostics.py          → FPS and latency monitoring
│
├── 📁 assets/
│   └── keyboard_format.png      → Print this! (A4 keyboard template)
│
└── 📁 logs/                      ← Auto-generated session logs
```

---

## ⚙️ Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                    │
├─────────────────────────────────────────────────────────┤
│  CLIENT (Phone Browser)       SERVER (Python)           │
│  ├─ HTML5 Canvas              ├─ FastAPI + uvicorn      │
│  ├─ MediaPipe Tasks Vision    ├─ OpenCV 4.8 (ArUco)    │
│  ├─ WebSocket (JSON packets)  ├─ NumPy (math)          │
│  └─ Real-time FPS counter     ├─ Pydantic (validation) │
│                               ├─ pynput (OS control)   │
│  VISION                       └─ pygame (audio)        │
│  ├─ ArUco Marker Detection                             │
│  ├─ RANSAC Homography                                  │
│  ├─ MediaPipe Hand Landmarks                           │
│  └─ Perspective Transform                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Installation

### Requirements

- Python 3.8 or higher
- A smartphone with Chrome or Safari
- A printed A4 copy of the keyboard template
- Computer and phone on the **same WiFi network**

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Devesh-Gawai/python-playground.git
cd python-playground/paper-keyboard
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary>📦 What gets installed?</summary>

```
fastapi          → Web server framework
uvicorn          → ASGI server
websockets       → Real-time communication
opencv-contrib   → Computer vision + ArUco detection
numpy            → Numerical operations
pynput           → OS keyboard injection
pydantic         → Data validation
pygame           → Tick sound (optional)
qrcode           → QR code for easy phone access
```
</details>

### Step 3 — Print the Keyboard Template

Download and print at **100% scale (A4 size)**:

<p align="center">
  <a href="https://raw.githubusercontent.com/Devesh-Gawai/python-playground/main/paper-keyboard/assets/keyboard_format.png">
    <img src="https://img.shields.io/badge/⬇️%20Download%20Keyboard%20Template-Print%20at%20100%25%20A4-blue?style=for-the-badge"/>
  </a>
</p>

> ⚠️ **Important:** All 4 ArUco markers (corner squares) must be fully visible in the camera frame.

### Step 4 — Start the Server

```bash
python main.py
```

**Expected output:**

```
🖐️   Paper Keyboard Server
────────────────────────────────────────────────────────
📡  Listening on : http://192.168.1.100:8000
📱  Open on phone: http://192.168.1.100:8000
────────────────────────────────────────────────────────

Workflow:
1. Mount phone overhead so all 4 ArUco markers are visible
2. Tap CALIBRATE in the phone browser
3. Start typing on the paper keyboard!
```

A **QR code** is printed automatically — just scan it with your phone camera to open the app instantly.

---

## 🚀 How to Use

**1 — Mount your phone overhead**

```
         📱 (Camera pointing down)
          │
          │  ~25-35cm above paper
          │
    ┌─────▼──────────────┐
    │ [ArUco] .......... [ArUco]  │  ← All 4 corner markers
    │ ...QWERTY keyboard......... │     must be visible
    │ [ArUco] .......... [ArUco]  │
    └────────────────────────┘
```

**2 — Open the website on your phone**

Navigate to the URL shown in terminal (e.g., `http://192.168.1.100:8000`)

Allow camera permissions when prompted.

**3 — Tap CALIBRATE**

The system detects the 4 ArUco markers and maps your keyboard.
Status shows: `Calibrated ✓ markers: 0,1,2,3`

**4 — Open any text editor on your computer and start typing!**

```
Terminal logs every detected key:
  🔑  A  (kx=0.234 ky=0.456)
  🔑  Space  (kx=0.483 ky=0.860)
  🔑  Enter  (kx=0.987 ky=0.760)
```

---

## ⚡ Configuration (No Code Needed)

All settings live in **`config.json`** — tune without touching any Python files.

### Touch Sensitivity

```json
"touch": {
  "z_contact_threshold": 0.012,       // Lower = more sensitive to finger depth
  "img_dist_threshold": 0.100,        // Higher = more forgiving distance check
  "velocity_window": 3,               // Frames to check for velocity
  "min_downward_velocity": 0.0005,    // Lower = easier to trigger
  "confirm_frames": 1,                // 1=fast, 2=accurate (try both)
  "cooldown_ms": 100,                 // Lower = faster typing
  "position_stability_px": 0.025,     // Lower = stops adjacent key confusion
  "visibility_threshold": 0.50        // MediaPipe confidence minimum
}
```

### Recommended Presets

| Use Case | `cooldown_ms` | `confirm_frames` | `position_stability_px` |
|----------|--------------|-----------------|------------------------|
| **Accurate** (daily use) | 200 | 2 | 0.020 |
| **Balanced** (default) | 150 | 1 | 0.025 |
| **Fast** (speed test) | 80 | 1 | 0.030 |

---

## 📊 Performance

| Metric | Current | Target |
|--------|---------|--------|
| Typing Speed | 100–120 WPM | 140+ WPM |
| Touch Accuracy | 95–98% | 99%+ |
| End-to-End Latency | 17–22ms | <10ms |
| Phone FPS (MediaPipe) | 10–11 FPS | 30 FPS |
| Calibration Time | 2–3 seconds | <2 seconds |

---

## 🔧 Common Issues & Fixes

<details>
<summary>❌ Calibration fails — "No ArUco markers detected"</summary>

**Causes:**
- Markers partially out of frame
- Poor or glaring lighting
- Paper printed too small

**Fixes:**
- Ensure all 4 corner markers are fully visible
- Use soft overhead lighting (avoid direct sunlight on paper)
- Print at exactly 100% scale (A4)
- Lower `min_perimeter` in config.json from 80 → 40

</details>

<details>
<summary>❌ Wrong letter typed — pressing H gets J</summary>

**Cause:** Position drift on adjacent keys

**Fix in config.json:**
```json
"position_stability_px": 0.020
```

</details>

<details>
<summary>❌ Typing feels too slow</summary>

**Fix in config.json:**
```json
"cooldown_ms": 80,
"confirm_frames": 1
```

</details>

<details>
<summary>❌ Sound warning in terminal — "Array must be 2-dimensional"</summary>

**Fix in core/debounce.py** (line ~20):
```python
# Change: channels=1
# To:     channels=2
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
```

Or simply disable sound in config.json:
```json
"sound": { "enabled": false }
```

</details>

<details>
<summary>❌ Can't connect phone to server</summary>

- Confirm both devices are on the **same WiFi network**
- Disable Windows Firewall temporarily or allow port 8000
- Try the QR code printed in terminal instead of typing the URL

</details>

---

## 🗺️ Roadmap

### ✅ Version 1.0 (Current)
- Full QWERTY typing on paper
- ArUco calibration + homography
- 5-layer touch detection
- WebSocket real-time communication
- Native OS key injection

### 🔄 Version 1.1 (In Progress)
- [ ] Faster typing speed (target: 150+ WPM)
- [ ] Improved adjacent key accuracy
- [ ] Haptic feedback via phone vibration
- [ ] Adaptive calibration drift correction

### 🔮 Version 1.5 (Planned)
- [ ] Both index fingers simultaneously
- [ ] Gesture shortcuts (swipe to delete, double-tap space)
- [ ] Multiple keyboard layouts (Dvorak, AZERTY, Cyrillic)
- [ ] Auto-recalibration if phone moves

### 🚀 Version 2.0 (Future)
- [ ] Machine learning touch model (user-specific)
- [ ] Offline mobile app (no server needed)
- [ ] Voice commands integration
- [ ] Full 10-finger touch-typing support

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

---

## 📬 Contact & Feedback

Have a question, bug report, or idea? I'd love to hear from you.

<p align="center">
  <a href="https://forms.gle/urB5CHxcRd7BSoAf9">
    <img src="https://img.shields.io/badge/📩%20Send%20Feedback%20or%20Question-Google%20Form-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  </a>
</p>

| Channel | Link |
|---------|------|
| 💼 LinkedIn | [devesh-kumar-gawai-134346320](https://www.linkedin.com/in/devesh-kumar-gawai-134346320) |
| 🐛 GitHub Issues | [Report a Bug](../../issues) |
| 💬 GitHub Discussions | [Ask a Question](../../discussions) |
| 📋 Contact Form | [Google Form](https://forms.gle/urB5CHxcRd7BSoAf9) |

---

## 🙏 Acknowledgments

This project was built with these amazing open-source tools:

| Tool | Purpose |
|------|---------|
| [Google MediaPipe](https://google.github.io/mediapipe/) | Real-time hand landmark detection |
| [OpenCV](https://opencv.org/) | ArUco marker detection + computer vision |
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python web framework |
| [pynput](https://pynput.readthedocs.io/) | Native OS keyboard control |

---

<p align="center">
  <strong>⭐ If this project helped or inspired you, please give it a star — it means a lot!</strong>
</p>

<p align="center">
  <em>Built with curiosity and continuous learning.</em><br/>
  <strong>Version 1.0 — the journey is just getting started. 🚀</strong>
</p>
