# 🎮 Python FPS Survival — Ursina Game

<p align="center">
  <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/first_game/Screenshot%202026-08-01%20142525.png" alt="Python FPS Survival gameplay" width="900">
</p>

<p align="center">
  <strong>A fast-paced first-person survival shooter built from scratch in Python with the Ursina Engine.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Ursina-Game%20Engine-6C5CE7?style=for-the-badge" alt="Ursina">
  <img src="https://img.shields.io/badge/Genre-FPS%20Survival-E74C3C?style=for-the-badge" alt="FPS">
  <img src="https://img.shields.io/badge/Status-Playable-2EA44F?style=for-the-badge" alt="Playable">
</p>

---

## 🕹️ Game Overview

**Python FPS Survival** is a compact first-person shooter experiment focused on responsive gameplay, enemy spawning, aiming, raycast-based shooting, dynamic difficulty, scoring, lighting, shadows, and a simple game-over/restart loop.

The game drops the player into an open environment where enemies continuously spawn within a **120° front-facing combat cone** and move toward the player. Survive, aim, shoot, and keep the score climbing as the pressure gradually increases.

> **Core idea:** simple systems + responsive controls + escalating difficulty = an addictive survival loop.

---

## 🎬 Gameplay

<p align="center">
  <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/first_game/gameplay.gif" alt="Gameplay recording" width="900">
</p>

<p align="center">
  <em>🎯 Aim • 🔫 Shoot • 💥 Eliminate • 🏆 Survive</em>
</p>

---

## 📸 Game Screenshots

<table>
  <tr>
    <td width="50%" align="center">
      <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/first_game/Screenshot%202026-08-01%20142525.png" alt="Gameplay screenshot 1" width="100%">
      <br><sub><b>Combat View</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="https://github.com/Devesh-Gawai/python-playground/blob/main/first_game/Screenshot%202026-08-01%20142543.png" alt="Gameplay screenshot 2" width="100%">
      <br><sub><b>Survival Gameplay</b></sub>
    </td>
  </tr>
</table>

---

## ⚔️ Gameplay Features

| System | What it does |
|---|---|
| 🎯 **First-Person Controls** | Explore the environment using Ursina's `FirstPersonController`. |
| 🔫 **Raycast Shooting** | Mouse clicks perform hit detection against active enemies. |
| 💥 **Muzzle Flash** | Short visual feedback is triggered whenever the weapon fires. |
| ✨ **Impact Effect** | A temporary glowing sphere appears when an enemy is hit. |
| 👾 **Enemy Waves** | Enemies spawn continuously from the front combat zone. |
| 🧭 **120° Spawn Cone** | Enemies are positioned within a controlled front-facing field. |
| 🧠 **Enemy Chasing AI** | Enemies continuously face and move toward the player. |
| 📈 **Dynamic Difficulty** | Enemy movement speed increases with survival time and score. |
| 🏆 **Score System** | Every successful elimination awards **100 points**. |
| 💀 **Game Over State** | A front-facing enemy reaching the player ends the run. |
| 🔄 **Instant Restart** | Press `R` to reset the arena and start a new run. |
| 💡 **Lighting & Shadows** | Uses Ursina's lit-with-shadows shader for a stronger 3D presentation. |

---

## 🎮 Controls

| Input | Action |
|---|---|
| 🖱️ **Left Mouse Button** | Shoot |
| 🖱️ **Mouse** | Aim / Look around |
| ⌨️ **W A S D** | Move |
| ⌨️ **R** | Restart after Game Over |
| ⎋ **Esc** | Exit the game |

---

## 🧠 How the Game Works

```text
                    ┌──────────────────────┐
                    │     START GAME       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Spawn Enemy Wave   │
                    │    Every ~1.5 sec     │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌─────────────────────────────┐
                 │ Enemy appears in FRONT 120° │
                 │       combat region         │
                 └──────────────┬──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Enemy moves toward   │
                    │       player         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
          ┌─────────────┐             ┌─────────────┐
          │ Player      │             │ Player gets │
          │ shoots      │             │ approached  │
          └──────┬──────┘             └──────┬──────┘
                 │                           │
                 ▼                           ▼
          ┌─────────────┐             ┌─────────────┐
          │ Raycast hit │             │ Front cone? │
          │ enemy?      │             └──────┬──────┘
          └──────┬──────┘                    │
                 │                           ▼
                 ▼                    ┌─────────────┐
          +100 SCORE                 │ GAME OVER   │
          + Remove Enemy              └─────────────┘
                 │
                 └──────────────► NEXT WAVE
```

---

## 🔥 Difficulty System

The game is designed so that the longer you survive, the more intense the encounter becomes.

Enemy speed is calculated from both **survival time** and **score**:

```python
current_speed = 2.0 + (game_time * 0.05) + (score * 0.005)
```

### Difficulty progression

```text
START
  │
  ├── Enemy speed: 2.0
  │
  ▼
SURVIVAL TIME ──────────────┐
                            │
                            ▼
                        SPEED UP
                            ▲
                            │
SCORE ──────────────────────┘
```

This creates a lightweight **risk/reward loop**: every successful elimination increases the score, while surviving longer also makes enemies progressively faster.

---

## 🎯 Front 120° Combat System

Enemy spawning is intentionally restricted to the player's forward field instead of using completely random positions around the map.

The spawn angle is selected between:

```text
-60°  ◄──────────  0°  ──────────►  +60°
                 PLAYER
```

That produces a **120° front-facing combat zone**.

The same concept is used when checking whether an enemy collision should trigger Game Over:

```python
if fwd.dot(to_enemy) >= 0.5:
    trigger_game_over()
```

Because:

```text
cos(60°) = 0.5
```

the dot-product threshold represents the intended front-facing cone.

---

## 💥 Shooting Pipeline

```text
LEFT CLICK
    │
    ▼
┌──────────────────┐
│  Trigger muzzle  │
│      flash       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Check hovered    │
│     entity       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Is it an active  │
│     enemy?       │
└───────┬──────────┘
        │ YES
        ▼
┌──────────────────┐
│ Spawn hit effect │
│   +100 score     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Remove enemy     │
│ from game        │
└──────────────────┘
```

---

## 🏗️ Project Structure

```text
python-playground/
│
└── first_game/
    ├── game.py
    ├── Screenshot 2026-08-01 142525.png
    ├── Screenshot 2026-08-01 142543.png
    └── gameplay.gif
```

> The exact Python filename can be renamed to match the file currently stored in the `first_game` directory.

---

## 🧩 Technology Stack

<p align="center">

| Technology | Role |
|---|---|
| 🐍 **Python** | Core programming language |
| 🎮 **Ursina Engine** | 3D game engine and scene management |
| 🧍 **FirstPersonController** | FPS movement and camera control |
| 💡 **Ursina Shaders** | Lighting and shadow rendering |
| 📐 **Math** | Spawn-angle and direction calculations |
| 🧵 **Threading** | Background enemy spawning |
| ⏱️ **Time** | Frame timing and difficulty progression |

</p>

---

## 🔬 Technical Highlights

### 1. Dynamic Enemy Spawning

A dedicated background spawner continuously creates enemies:

```python
def wave_spawner():
    while True:
        if not is_game_over:
            spawn_enemy()
        py_time.sleep(1.5)
```

This keeps the enemy stream continuous while the main game loop handles movement and interaction.

### 2. Direction-Aware Spawning

The player's current forward vector is flattened onto the ground plane, rotated by a random angle, and used to determine the enemy's spawn position.

```python
angle_offset = random.uniform(
    -math.radians(60),
    math.radians(60)
)
```

### 3. Enemy Pursuit

Each enemy continuously looks toward the player and advances using its forward vector:

```python
enemy.look_at(player)
enemy.position += enemy.forward * current_speed * time.dt
```

### 4. Score Feedback

Every enemy elimination gives:

```text
+100 SCORE
```

and immediately updates the HUD.

### 5. Game State Management

The game uses a simple state machine:

```text
PLAYING ──────────────► GAME OVER
   ▲                       │
   │                       │ R
   └───────────────────────┘
```

---

## 🎨 Visual Design

The game combines several small visual systems to make the prototype feel more complete:

- 🌿 Large grass environment
- ☁️ Sky background
- 💡 Directional lighting
- 🌑 Dynamic shadows
- 🔫 First-person weapon model
- 🟡 Muzzle flash
- ✨ Hit feedback effect
- 🎯 Persistent crosshair
- 🏆 Score HUD
- 💀 Game-over overlay

The visual goal is not photorealism — it is to make a small Python prototype feel like a **complete playable game experiment**.

---

## 📊 Gameplay Loop

```text
        ┌───────────────┐
        │     AIM       │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │    SHOOT      │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │ ELIMINATE     │
        │    ENEMY      │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │ +100 SCORE    │
        └───────┬───────┘
                ▼
        ┌───────────────┐
        │ MORE PRESSURE │
        └───────┬───────┘
                │
                └──────────► REPEAT
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Devesh-Gawai/python-playground.git
cd python-playground
```

### 2. Install Ursina

```bash
pip install ursina
```

### 3. Run the game

```bash
python first_game/game.py
```

If your Python file has a different filename, replace `game.py` with the actual filename.

---

## 🛠️ Installation Requirements

- Python 3.x
- Ursina Engine
- A desktop environment capable of running a 3D application
- Mouse and keyboard

Install the main dependency with:

```bash
pip install ursina
```

---

## 📈 What I Practiced

Building this project provided hands-on practice with:

```text
Python Programming
      │
      ├── Object / Entity management
      ├── Functions & global game state
      ├── Loops & conditionals
      ├── Vector mathematics
      ├── Dot products
      ├── Randomized spawning
      ├── Threading
      ├── Real-time update loops
      └── Event-driven input
                │
                ▼
          GAME DEVELOPMENT
                │
                ├── Player movement
                ├── Enemy AI
                ├── Shooting
                ├── Collision logic
                ├── HUD
                ├── Game states
                └── Visual effects
```

---

## 🧪 Future Improvements

The current version is intentionally a compact prototype, leaving plenty of room for expansion:

- [ ] Multiple enemy types
- [ ] Health / armor system
- [ ] Reload and ammunition mechanics
- [ ] Weapon variety
- [ ] Sound effects and background music
- [ ] Explosion and particle systems
- [ ] Wave-based difficulty
- [ ] High-score persistence
- [ ] Main menu and pause menu
- [ ] Better environment assets
- [ ] More advanced enemy AI
- [ ] Improved animations
- [ ] Additional maps / arenas

---

## 🏆 Project Highlights

| Area | Implementation |
|---|---|
| 🎮 Game Type | First-Person Survival Shooter |
| 🐍 Language | Python |
| ⚙️ Engine | Ursina |
| 👾 Enemy System | Continuous spawning + pursuit |
| 🎯 Combat | Mouse-based shooting |
| 🧠 Targeting | Entity hit detection |
| 📈 Difficulty | Time + score based |
| 🏆 Scoring | 100 points / enemy |
| 💀 Game State | Playing / Game Over / Restart |
| 💡 Rendering | Lighting + shadows |
| 🎬 Media | Screenshots + gameplay recording |

---

## 👨‍💻 Project

**Python Playground — First Game**

Built as a hands-on Python game-development project to explore how programming concepts can be combined into an interactive real-time 3D experience.

<p align="center">
  <strong>🐍 Python + 🎮 Ursina + 🧠 Game Logic = 🚀 Playable Experience</strong>
</p>

---

<p align="center">
  <sub>Built with Python • Powered by Ursina • Designed as a learning-by-building project</sub>
</p>
