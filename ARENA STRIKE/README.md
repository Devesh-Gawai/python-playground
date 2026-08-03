# Arena Strike — Setup & Play Guide

A first-person shooter you run from your own laptop. You (and anyone else on
your WiFi) play it in a normal web browser — nobody needs to install
anything except you, once, to start the server.

No programming knowledge needed to run this. Just follow the steps below.

---

## 1. What you need

- **Python 3** installed on the laptop that will act as the "host" (the one
  that stores the game files). You said you already have this. To check,
  open a terminal/command prompt and type:
  ```
  python3 --version
  ```
  (On Windows it might be `python --version` instead — either is fine.)
- No other installs. The server uses only what comes built into Python.
- All players' devices need to be on the **same WiFi network** as the host
  laptop.
- All players need internet access at least the *first* time they play,
  because the 3D graphics library (Three.js) loads from a public CDN link
  in the game page. After that first load, browsers usually cache it.

---

## 2. Folder contents

```
fps-game/
  server.py          <- run this to start the game server
  client/
    index.html        <- the game page
    style.css          <- visual styling
    game.js             <- the actual game code
  README.md          <- this guide
```

Don't rename or move files inside `client/` — `server.py` expects them
to stay exactly where they are, right next to it in a folder called
`client`.

---

## 3. How to start the game

1. Open a terminal (Command Prompt / PowerShell on Windows, Terminal on
   Mac/Linux) and navigate into the `fps-game` folder. For example:
   ```
   cd path/to/fps-game
   ```
2. Run:
   ```
   python3 server.py
   ```
3. You'll see something like:
   ```
   ============================================================
    LAN FPS server is running
   ============================================================
    On THIS computer, open:      http://localhost:8000
    On OTHER devices (same WiFi): http://192.168.1.42:8000
   ============================================================
    Press Ctrl+C to stop the server.
   ```
4. **On the host laptop**, open a browser and go to `http://localhost:8000`.
5. **On any other phone/tablet/laptop** on the same WiFi, open a browser
   and type in the "Network URL" shown in your terminal (the one that
   looks like `http://192.168.x.x:8000`). That's it — no app, no install.

Leave the terminal window open while people are playing — closing it (or
pressing Ctrl+C) shuts the server down for everyone.

---

## 4. How to play

- **Single Player**: pick a name, click "Single Player" — you're dropped
  into the arena against 5 AI bots. Kill them for points; they respawn
  after a few seconds.
- **Multiplayer**: pick a name, click "Multiplayer," then "Connect & Play"
  (the server address is filled in automatically). Everyone who joins the
  same server URL is in the same match, live.

**Controls (keyboard + mouse):**
| Key | Action |
|---|---|
| Mouse | Look around |
| W A S D | Move |
| Shift | Sprint |
| Space | Jump |
| Left Click (hold) | Shoot |
| R | Reload |
| Esc | Release mouse / pause |

**Controls (phone/tablet touchscreen):** the game automatically shows
on-screen controls on touch devices — no keyboard/mouse needed:
- Bottom-left: drag the joystick to move
- Right side of the screen: drag to look around
- Bottom-right: FIRE button (hold for continuous fire), JUMP, and RELOAD
  buttons

Tap "TAP TO PLAY" to enter the arena (touch devices don't use mouse
pointer-lock, so this works without any special permissions).

Click anywhere on the "Click to enter the arena" screen to lock your mouse
into look-mode. Press Esc to get your mouse back at any time.

On phones/tablets, the on-screen controls make it fully playable — you'll
still get the most precise aim from a laptop with a mouse, but touch play
works for both single-player and multiplayer now.

---

## 5. Stopping the server

Click back into the terminal window and press `Ctrl+C`. This ends the
match for everyone connected.

---

## 6. Troubleshooting

**"Other devices can't connect"**
- Make sure every device is on the exact same WiFi network (not a guest
  network — some routers isolate guest WiFi from itself, which blocks
  this).
- Some antivirus/firewall software blocks incoming connections to Python.
  If a connection dialog pops up asking to "allow" `python3` on
  networks, click **Allow**.
- Double check the IP address printed in the terminal hasn't changed
  (it can change if you reconnect to WiFi) — just re-check the terminal
  output.

**"The game page is blank / stuck on Loading"**
- Make sure the host laptop has internet access (needed to load the 3D
  graphics library the first time).
- Try a hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac).

**"python3: command not found"**
- On Windows, try `python server.py` instead of `python3 server.py`.
- If neither works, Python isn't installed or isn't on your system PATH —
  reinstalling Python from python.org and checking "Add to PATH" during
  install fixes this.

**"I connected to multiplayer but the arena looks empty / other players
aren't visible"**
- Each player only appears to others once they've actually clicked/tapped
  past the "Click/Tap to enter the arena" screen — until then, their
  device isn't sending position updates yet, and after a few seconds of
  no updates the server drops them from the match. Make sure everyone
  has clicked/tapped into the arena, not just connected from the menu.
- Confirm everyone typed/kept the exact same server address (it should
  match the "Network URL" from the host's terminal, e.g.
  `http://192.168.1.42:8000`, not `localhost` on non-host devices).

**Multiplayer feels laggy**
- The game now sends and receives updates in a single combined request
  about 20 times a second (previously it took 3 separate requests per
  update), which noticeably cuts the delay between someone moving/shooting
  and everyone else seeing it. It's still simple HTTP polling rather than
  a persistent connection, so it's built for a smooth small LAN party, not
  competitive-twitch precision at internet scale.
- If a player sits on a menu/loading screen for a while before actually
  entering the arena, their session used to occasionally expire before
  their first move — the game now automatically reconnects them behind
  the scenes if that happens, so this shouldn't come up anymore.

**Right after respawning, a few shots don't seem to register**
- That's intentional — for about 1.5 seconds after spawning or
  respawning, a player has brief spawn protection (a common shooter
  convention) so they can't be killed again the instant they reappear.
  After that window, hits register normally.

**"I updated the files but the game still behaves like the old version"**
- Browsers (especially on phones) can cache the game's files. The server
  now sends headers telling browsers never to cache them, so this should
  no longer happen going forward — but if you're not seeing a change you
  just made, do a hard refresh (Ctrl+Shift+R / Cmd+Shift+R on desktop) or
  fully close and reopen the browser tab on mobile, and double-check you
  replaced *all* the files (`server.py` and everything in `client/`), not
  just some of them.

---

## 7. Honest expectations

This is a real, playable, good-looking browser FPS with working
single-player bots and working local-network multiplayer — built with
Three.js, running entirely from files on your laptop. It is **not** a
copy of a modern Call of Duty game; that's a different scale of project
(large studios, years of work, custom engines). If you want to keep
building on this later, everything is plain HTML/CSS/JS and Python, so
it's straightforward for anyone (or any AI coding assistant) to extend —
more weapons, more maps, better bot AI, sounds, etc.
