import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

/* =========================================================================
   ARENA STRIKE - a browser FPS built with Three.js
   Single file, organized into clear sections:
     1. Texture helpers (procedural, no external image files needed)
     2. Scene / lighting / sky / level construction
     3. Player controller (movement, gravity, collision)
     4. Weapon viewmodel + shooting/raycasting
     5. Bot AI (single player)
     6. Networking (multiplayer via HTTP polling)
     7. HUD wiring
     8. Menus / game state / main loop
   ========================================================================= */

/* ---------------------------------------------------------------------- */
/* 1. TEXTURE HELPERS                                                     */
/* ---------------------------------------------------------------------- */

function makeCanvasTexture(draw, size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  draw(ctx, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function groundTexture() {
  return makeCanvasTexture((ctx, s) => {
    ctx.fillStyle = '#3a4a3f';
    ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 900; i++) {
      const x = Math.random() * s, y = Math.random() * s;
      const shade = 40 + Math.random() * 40;
      ctx.fillStyle = `rgba(${shade + 10},${shade + 25},${shade + 5},0.5)`;
      ctx.fillRect(x, y, 2 + Math.random() * 3, 2 + Math.random() * 3);
    }
    ctx.strokeStyle = 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 2;
    for (let i = 0; i <= s; i += s / 8) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, s); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(s, i); ctx.stroke();
    }
  }, 512);
}

function crateTexture() {
  return makeCanvasTexture((ctx, s) => {
    ctx.fillStyle = '#8a6535';
    ctx.fillRect(0, 0, s, s);
    for (let i = 0; i < 10; i++) {
      ctx.strokeStyle = `rgba(60,40,15,${0.3 + Math.random() * 0.3})`;
      ctx.lineWidth = 1 + Math.random() * 2;
      const y = Math.random() * s;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(s, y + (Math.random() * 10 - 5)); ctx.stroke();
    }
    ctx.strokeStyle = '#3d2a12';
    ctx.lineWidth = 8;
    ctx.strokeRect(4, 4, s - 8, s - 8);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(s, s); ctx.moveTo(s, 0); ctx.lineTo(0, s); ctx.stroke();
  }, 128);
}

function wallTexture() {
  return makeCanvasTexture((ctx, s) => {
    ctx.fillStyle = '#5b6068';
    ctx.fillRect(0, 0, s, s);
    const rows = 8, cols = 4;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const offset = (r % 2) * (s / cols / 2);
        const x = (c * s / cols + offset) % s;
        const y = r * s / rows;
        ctx.strokeStyle = 'rgba(20,22,26,0.6)';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, s / cols, s / rows);
      }
    }
    for (let i = 0; i < 300; i++) {
      ctx.fillStyle = `rgba(${90 + Math.random() * 40},${92 + Math.random() * 40},${96 + Math.random() * 40},0.4)`;
      ctx.fillRect(Math.random() * s, Math.random() * s, 2, 2);
    }
  }, 256);
}

function nameSprite(text, color = '#ffffff') {
  const canvas = document.createElement('canvas');
  canvas.width = 256; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  ctx.font = 'bold 34px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(0, 10, 256, 44);
  ctx.fillStyle = color;
  ctx.fillText(text.slice(0, 16), 128, 32);
  const tex = new THREE.CanvasTexture(canvas);
  const mat = new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(1.6, 0.4, 1);
  sprite.renderOrder = 999;
  return sprite;
}

/* ---------------------------------------------------------------------- */
/* 2. SCENE / LIGHTING / SKY / LEVEL                                      */
/* ---------------------------------------------------------------------- */

const ARENA_HALF = 40; // arena is 80x80

function buildSky(scene) {
  const skyGeo = new THREE.SphereGeometry(400, 24, 16);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    uniforms: {
      topColor: { value: new THREE.Color(0x3a6fc4) },
      bottomColor: { value: new THREE.Color(0xcfe8ff) },
    },
    vertexShader: `
      varying vec3 vWorldPos;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vWorldPos = wp.xyz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }
    `,
    fragmentShader: `
      varying vec3 vWorldPos;
      uniform vec3 topColor;
      uniform vec3 bottomColor;
      void main() {
        float h = normalize(vWorldPos).y;
        float t = clamp(h * 0.8 + 0.35, 0.0, 1.0);
        gl_FragColor = vec4(mix(bottomColor, topColor, t), 1.0);
      }
    `,
  });
  scene.add(new THREE.Mesh(skyGeo, skyMat));
  scene.fog = new THREE.Fog(0xcfe8ff, 45, 220);
}

function buildLighting(scene) {
  const hemi = new THREE.HemisphereLight(0xdfeeff, 0x33402a, 0.8);
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xfff4de, 1.6);
  sun.position.set(60, 90, 30);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -70;
  sun.shadow.camera.right = 70;
  sun.shadow.camera.top = 70;
  sun.shadow.camera.bottom = -70;
  sun.shadow.camera.near = 10;
  sun.shadow.camera.far = 220;
  sun.shadow.bias = -0.0015;
  scene.add(sun);
  scene.add(sun.target);
}

function box(w, h, d, mat) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function buildLevel(scene) {
  const colliders = []; // { box: THREE.Box3, mesh }

  // Ground
  const gTex = groundTexture();
  gTex.repeat.set(20, 20);
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(ARENA_HALF * 2, ARENA_HALF * 2),
    new THREE.MeshStandardMaterial({ map: gTex, roughness: 0.95 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // Perimeter walls
  const wTex = wallTexture();
  wTex.repeat.set(8, 1);
  const wallMat = new THREE.MeshStandardMaterial({ map: wTex, roughness: 0.85 });
  const wallH = 6, wallT = 1;
  const wallDefs = [
    [0, wallH / 2, -ARENA_HALF, ARENA_HALF * 2, wallH, wallT],
    [0, wallH / 2, ARENA_HALF, ARENA_HALF * 2, wallH, wallT],
    [-ARENA_HALF, wallH / 2, 0, wallT, wallH, ARENA_HALF * 2],
    [ARENA_HALF, wallH / 2, 0, wallT, wallH, ARENA_HALF * 2],
  ];
  for (const [x, y, z, w, h, d] of wallDefs) {
    const m = box(w, h, d, wallMat);
    m.position.set(x, y, z);
    scene.add(m);
    colliders.push({ box: new THREE.Box3().setFromObject(m), mesh: m });
  }

  // Crates / cover, laid out in a symmetric arena pattern
  const cTex = crateTexture();
  const crateMat = new THREE.MeshStandardMaterial({ map: cTex, roughness: 0.8 });
  const cratePositions = [
    [10, 0, 10], [-10, 0, 10], [10, 0, -10], [-10, 0, -10],
    [0, 0, 18], [0, 0, -18], [18, 0, 0], [-18, 0, 0],
    [6, 0, 0], [-6, 0, 0], [0, 0, 6], [0, 0, -6],
    [22, 0, 22], [-22, 0, 22], [22, 0, -22], [-22, 0, -22],
  ];
  for (const [x, , z] of cratePositions) {
    const size = 2 + (Math.abs(x * z) % 3) * 0.4;
    const m = box(size, size, size, crateMat);
    m.position.set(x, size / 2, z);
    m.rotation.y = (x * 13 + z * 7) % 6;
    scene.add(m);
    colliders.push({ box: new THREE.Box3().setFromObject(m), mesh: m });
  }

  // A couple of raised platforms for verticality
  const platMat = new THREE.MeshStandardMaterial({ map: wTex, roughness: 0.7 });
  const platforms = [[28, 1.5, 0], [-28, 1.5, 0], [0, 1.5, 28], [0, 1.5, -28]];
  for (const [x, y, z] of platforms) {
    const m = box(8, 1, 8, platMat);
    m.position.set(x, y, z);
    scene.add(m);
    colliders.push({ box: new THREE.Box3().setFromObject(m), mesh: m });
  }

  return colliders;
}

/* ---------------------------------------------------------------------- */
/* 3. PLAYER CONTROLLER                                                   */
/* ---------------------------------------------------------------------- */

const GRAVITY = 22;
const PLAYER_RADIUS = 0.5;
const EYE_HEIGHT = 1.7;
const WALK_SPEED = 6.2;
const SPRINT_SPEED = 9.5;
const JUMP_SPEED = 8.2;

class Player {
  constructor(camera) {
    this.camera = camera;
    this.position = new THREE.Vector3(0, EYE_HEIGHT, 6);
    this.velocity = new THREE.Vector3();
    this.onGround = true;
    this.health = 100;
    this.maxHealth = 100;
    this.alive = true;
    this.kills = 0;
    this.deaths = 0;
    this.keys = {};
    this.sprint = false;
    this.touchMove = { x: 0, y: 0 }; // set by the on-screen joystick on touch devices
  }

  respawn() {
    const angle = Math.random() * Math.PI * 2;
    const r = 5 + Math.random() * 10;
    this.position.set(Math.cos(angle) * r, EYE_HEIGHT, Math.sin(angle) * r);
    this.velocity.set(0, 0, 0);
    this.health = this.maxHealth;
    this.alive = true;
  }

  takeDamage(dmg) {
    if (!this.alive) return false;
    this.health = Math.max(0, this.health - dmg);
    if (this.health <= 0) {
      this.alive = false;
      this.deaths++;
      return true; // died
    }
    return false;
  }

  update(dt, colliders, controls) {
    if (!this.alive) return;

    const forward = new THREE.Vector3();
    controls.getDirection(forward);
    forward.y = 0;
    forward.normalize();
    const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0));

    const move = new THREE.Vector3();
    if (this.keys['KeyW']) move.add(forward);
    if (this.keys['KeyS']) move.sub(forward);
    if (this.keys['KeyD']) move.add(right);
    if (this.keys['KeyA']) move.sub(right);
    // On-screen joystick (touch devices): analog forward/strafe input.
    move.addScaledVector(forward, this.touchMove.y);
    move.addScaledVector(right, this.touchMove.x);
    if (move.lengthSq() > 1) move.normalize();

    const speed = (this.keys['ShiftLeft'] || this.keys['ShiftRight']) ? SPRINT_SPEED : WALK_SPEED;
    this.velocity.x = move.x * speed;
    this.velocity.z = move.z * speed;

    if (this.keys['Space'] && this.onGround) {
      this.velocity.y = JUMP_SPEED;
      this.onGround = false;
    }

    this.velocity.y -= GRAVITY * dt;

    // Integrate + collide against level colliders (simple sphere vs AABB push-out)
    const next = this.position.clone();
    next.x += this.velocity.x * dt;
    next.z += this.velocity.z * dt;
    next.y += this.velocity.y * dt;

    for (const c of colliders) {
      const b = c.box;
      const cx = THREE.MathUtils.clamp(next.x, b.min.x, b.max.x);
      const cy = THREE.MathUtils.clamp(next.y - 1.0, b.min.y, b.max.y); // approximate body center
      const cz = THREE.MathUtils.clamp(next.z, b.min.z, b.max.z);
      const dx = next.x - cx, dy = (next.y - 1.0) - cy, dz = next.z - cz;
      const distSq = dx * dx + dy * dy + dz * dz;
      if (distSq < PLAYER_RADIUS * PLAYER_RADIUS && distSq > 1e-6) {
        const dist = Math.sqrt(distSq);
        const push = (PLAYER_RADIUS - dist) / dist;
        next.x += dx * push;
        next.z += dz * push;
      }
    }

    // Ground clamp — also treat the tops of low obstacles (crates, platforms)
    // as walkable floors, so jumping has a purpose. Tall perimeter walls are
    // excluded so they behave as walls, not floors.
    let groundLevel = 0;
    for (const c of colliders) {
      const b = c.box;
      const h = b.max.y - b.min.y;
      if (h > 3.5) continue;
      if (next.x >= b.min.x && next.x <= b.max.x && next.z >= b.min.z && next.z <= b.max.z) {
        groundLevel = Math.max(groundLevel, b.max.y);
      }
    }
    const eyeTarget = groundLevel + EYE_HEIGHT;
    if (next.y <= eyeTarget) {
      next.y = eyeTarget;
      this.velocity.y = 0;
      this.onGround = true;
    } else {
      this.onGround = false;
    }

    // Arena bounds
    const b = ARENA_HALF - 1;
    next.x = THREE.MathUtils.clamp(next.x, -b, b);
    next.z = THREE.MathUtils.clamp(next.z, -b, b);

    this.position.copy(next);
    this.camera.position.copy(this.position);
  }
}

/* ---------------------------------------------------------------------- */
/* 4. WEAPON VIEWMODEL + SHOOTING                                         */
/* ---------------------------------------------------------------------- */

class Weapon {
  constructor(camera, scene) {
    this.camera = camera;
    this.scene = scene;
    this.ammo = 30;
    this.maxAmmo = 30;
    this.reloading = false;
    this.reloadTime = 1.4;
    this.reloadTimer = 0;
    this.fireRate = 0.11; // seconds between shots
    this.cooldown = 0;
    this.bobTime = 0;
    this.recoil = 0;

    this.group = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0x2a2d33, roughness: 0.4, metalness: 0.6 });
    const gripMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.8 });

    const body = box(0.09, 0.09, 0.55, bodyMat);
    body.position.set(0, 0, -0.1);
    const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.35, 8), bodyMat);
    barrel.rotation.z = Math.PI / 2;
    barrel.position.set(0, 0.02, -0.55);
    const grip = box(0.07, 0.22, 0.09, gripMat);
    grip.position.set(0, -0.16, 0.12);
    const mag = box(0.06, 0.18, 0.08, gripMat);
    mag.position.set(0, -0.14, -0.05);
    const sight = box(0.03, 0.05, 0.03, bodyMat);
    sight.position.set(0, 0.075, -0.2);

    this.group.add(body, barrel, grip, mag, sight);
    this.group.traverse(o => { o.castShadow = false; o.receiveShadow = false; });
    this.group.position.set(0.28, -0.28, -0.55);
    camera.add(this.group);

    // Muzzle flash light
    this.flash = new THREE.PointLight(0xffcf8a, 0, 6, 2);
    this.flash.position.set(0, 0.02, -0.75);
    this.group.add(this.flash);
  }

  get muzzleWorldPosition() {
    const p = new THREE.Vector3();
    this.group.getWorldPosition(p);
    const dir = new THREE.Vector3();
    this.camera.getWorldDirection(dir);
    return p.add(dir.multiplyScalar(0.5));
  }

  startReload() {
    if (this.reloading || this.ammo === this.maxAmmo) return;
    this.reloading = true;
    this.reloadTimer = this.reloadTime;
  }

  canFire() {
    return !this.reloading && this.cooldown <= 0 && this.ammo > 0;
  }

  fire() {
    this.ammo--;
    this.cooldown = this.fireRate;
    this.recoil = 1;
    this.flash.intensity = 6;
    if (this.ammo === 0) this.startReload();
  }

  update(dt, isMoving) {
    this.cooldown = Math.max(0, this.cooldown - dt);
    this.flash.intensity = Math.max(0, this.flash.intensity - dt * 40);

    if (this.reloading) {
      this.reloadTimer -= dt;
      if (this.reloadTimer <= 0) {
        this.reloading = false;
        this.ammo = this.maxAmmo;
      }
    }

    // Bob + recoil animation
    this.bobTime += dt * (isMoving ? 8 : 2);
    const bobX = Math.sin(this.bobTime) * (isMoving ? 0.012 : 0.003);
    const bobY = Math.abs(Math.cos(this.bobTime)) * (isMoving ? 0.01 : 0.002);
    this.recoil = Math.max(0, this.recoil - dt * 6);

    this.group.position.set(
      0.28 + bobX,
      -0.28 + bobY + this.recoil * 0.04,
      -0.55 + this.recoil * 0.08
    );
    this.group.rotation.x = -this.recoil * 0.15;
  }
}

function createTracer(scene, from, to) {
  const geo = new THREE.BufferGeometry().setFromPoints([from, to]);
  const mat = new THREE.LineBasicMaterial({ color: 0xfff4c2, transparent: true, opacity: 0.9 });
  const line = new THREE.Line(geo, mat);
  scene.add(line);
  const start = performance.now();
  function fade() {
    const t = (performance.now() - start) / 90;
    if (t >= 1) { scene.remove(line); geo.dispose(); mat.dispose(); return; }
    mat.opacity = 0.9 * (1 - t);
    requestAnimationFrame(fade);
  }
  requestAnimationFrame(fade);
}

/* ---------------------------------------------------------------------- */
/* 5. BOT AI (single player)                                              */
/* ---------------------------------------------------------------------- */

const BOT_COUNT = 5;
const BOT_SIGHT_RANGE = 26;
const BOT_ATTACK_RANGE = 22;

function buildBotMesh(color) {
  const group = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color, roughness: 0.6 });
  const headMat = new THREE.MeshStandardMaterial({ color: 0xe0b488, roughness: 0.7 });
  const eyeMat = new THREE.MeshStandardMaterial({ color: 0x14161a, roughness: 0.25 });

  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.35, 0.9, 4, 8), bodyMat);
  body.position.y = 0.9;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 10), headMat);
  head.position.y = 1.65;
  body.castShadow = true; head.castShadow = true;
  body.receiveShadow = true;

  // Eyes on the front face (local -Z, matching the camera's forward
  // convention) so other players can tell which way this character is
  // looking, not just which way their body is turned.
  const eyeGeo = new THREE.SphereGeometry(0.045, 8, 6);
  const eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.09, 1.68, -0.19);
  const eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(0.09, 1.68, -0.19);

  group.add(body, head, eyeL, eyeR);
  group.userData.bodyMesh = body;
  group.userData.headMesh = head;
  return group;
}

class Bot {
  constructor(scene, id, colliders) {
    this.id = id;
    this.scene = scene;
    this.colliders = colliders;
    this.health = 100;
    this.maxHealth = 100;
    this.alive = true;
    this.state = 'patrol';
    this.fireCooldown = 0;
    this.waypoint = new THREE.Vector3();
    this.nextWaypointTimer = 0;

    const colors = [0xd14b4b, 0x4b8fd1, 0x59c17a, 0xc99b3f, 0xa15fd1];
    this.mesh = buildBotMesh(colors[id % colors.length]);
    this.nameTag = nameSprite('BOT ' + (id + 1), '#ff8a6b');
    this.nameTag.position.y = 2.05;
    this.mesh.add(this.nameTag);
    scene.add(this.mesh);
    this.respawn();
  }

  respawn() {
    const angle = Math.random() * Math.PI * 2;
    const r = 15 + Math.random() * 20;
    this.mesh.position.set(Math.cos(angle) * r, 0, Math.sin(angle) * r);
    this.health = this.maxHealth;
    this.alive = true;
    this.mesh.visible = true;
    this.state = 'patrol';
    this.pickWaypoint();
  }

  pickWaypoint() {
    const b = ARENA_HALF - 4;
    this.waypoint.set((Math.random() * 2 - 1) * b, 0, (Math.random() * 2 - 1) * b);
    this.nextWaypointTimer = 4 + Math.random() * 3;
  }

  takeDamage(dmg) {
    if (!this.alive) return false;
    this.health = Math.max(0, this.health - dmg);
    if (this.health <= 0) {
      this.alive = false;
      this.mesh.visible = false;
      this._respawnTimer = 3.5;
      return true;
    }
    return false;
  }

  hasLineOfSight(playerPos) {
    const from = this.mesh.position.clone(); from.y = 1.3;
    const to = playerPos.clone();
    const dir = to.clone().sub(from);
    const dist = dir.length();
    dir.normalize();
    const ray = new THREE.Raycaster(from, dir, 0, dist);
    const meshes = this.colliders.map(c => c.mesh);
    const hits = ray.intersectObjects(meshes, false);
    return hits.length === 0;
  }

  update(dt, playerPos, playerAlive, onShoot) {
    if (!this.alive) {
      this._respawnTimer -= dt;
      if (this._respawnTimer <= 0) this.respawn();
      return;
    }

    const pos = this.mesh.position;
    const toPlayer = playerPos.clone().sub(pos); toPlayer.y = 0;
    const distToPlayer = toPlayer.length();

    if (playerAlive && distToPlayer < BOT_SIGHT_RANGE && this.hasLineOfSight(playerPos)) {
      this.state = distToPlayer < BOT_ATTACK_RANGE ? 'attack' : 'chase';
    } else if (this.state !== 'patrol') {
      this.state = 'patrol';
      this.pickWaypoint();
    }

    let moveDir = null;
    if (this.state === 'patrol') {
      this.nextWaypointTimer -= dt;
      const toWp = this.waypoint.clone().sub(pos); toWp.y = 0;
      if (toWp.length() < 1.5 || this.nextWaypointTimer <= 0) this.pickWaypoint();
      else moveDir = toWp.normalize();
    } else if (this.state === 'chase') {
      moveDir = toPlayer.clone().normalize();
    } else if (this.state === 'attack') {
      // strafe a little while shooting
      const perp = new THREE.Vector3(-toPlayer.z, 0, toPlayer.x).normalize();
      moveDir = perp.multiplyScalar(Math.sin(performance.now() * 0.001 + this.id) * 0.6);
    }

    if (moveDir) {
      const speed = this.state === 'chase' ? 3.6 : 2.0;
      const next = pos.clone().addScaledVector(moveDir, speed * dt);
      // simple collider avoidance
      let blocked = false;
      for (const c of this.colliders) {
        const b = c.box;
        if (next.x > b.min.x - 0.4 && next.x < b.max.x + 0.4 &&
            next.z > b.min.z - 0.4 && next.z < b.max.z + 0.4 &&
            b.min.y < 1.6) { blocked = true; break; }
      }
      if (!blocked) {
        const bnd = ARENA_HALF - 1.5;
        next.x = THREE.MathUtils.clamp(next.x, -bnd, bnd);
        next.z = THREE.MathUtils.clamp(next.z, -bnd, bnd);
        pos.x = next.x; pos.z = next.z;
      }
    }

    if (toPlayer.lengthSq() > 0.0001) {
      // -Z is "forward" for these meshes (matching how camera.rotation.y
      // works for real players), so the eyes on the head point correctly.
      const targetAngle = Math.atan2(-toPlayer.x, -toPlayer.z);
      this.mesh.rotation.y = targetAngle;
    }

    this.fireCooldown -= dt;
    if (this.state === 'attack' && this.fireCooldown <= 0 && playerAlive) {
      this.fireCooldown = 0.9 + Math.random() * 0.6;
      const accuracy = THREE.MathUtils.clamp(1 - distToPlayer / BOT_SIGHT_RANGE, 0.15, 0.8);
      const hit = Math.random() < accuracy;
      const from = pos.clone(); from.y = 1.4;
      const to = playerPos.clone();
      onShoot(from, to, hit);
    }
  }
}

/* ---------------------------------------------------------------------- */
/* 6. NETWORKING (multiplayer via HTTP polling — no extra libraries)      */
/* ---------------------------------------------------------------------- */

class Network {
  constructor() {
    this.base = '';
    this.id = null;
    this.name = '';
    this.connected = false;
    this.lastEventTime = 0;
    this.remotePlayers = new Map(); // id -> latest state
    this._rejoining = false;
  }

  async connect(serverAddr, name) {
    this.base = serverAddr.replace(/\/$/, '');
    this.name = name;
    const res = await fetch(this.base + '/api/join', {
      method: 'POST', body: JSON.stringify({ name }),
    });
    if (!res.ok) throw new Error('Could not reach server');
    const data = await res.json();
    this.id = data.id;
    this.connected = true;
    this.lastEventTime = 0;
    return this.id;
  }

  // Single round trip: send our position/health AND receive the current
  // world state + new events together. This is what runs every tick —
  // previously this took 3 separate HTTP requests, now it's 1.
  async sync(pos, ry, health, eventHandler) {
    if (!this.connected) return;
    try {
      const res = await fetch(this.base + '/api/sync', {
        method: 'POST',
        body: JSON.stringify({
          id: this.id, x: pos.x, y: pos.y, z: pos.z, ry, health,
          since: this.lastEventTime,
        }),
      });
      if (res.status === 400 && !this._rejoining) {
        this._rejoining = true;
        try { await this.connect(this.base, this.name); }
        finally { this._rejoining = false; }
        return;
      }
      const data = await res.json();
      this.remotePlayers = new Map(Object.entries(data.players || {}));
      for (const ev of (data.events || [])) {
        this.lastEventTime = Math.max(this.lastEventTime, ev.t);
        if (eventHandler) eventHandler(ev);
      }
    } catch (e) { /* ignore transient network errors */ }
  }

  // Lightweight one-off position ping — used the instant a player enters
  // the arena, so their session is fresh without waiting for the next tick.
  async sendUpdate(pos, ry, health) {
    if (!this.connected) return;
    try {
      const res = await fetch(this.base + '/api/update', {
        method: 'POST',
        body: JSON.stringify({ id: this.id, x: pos.x, y: pos.y, z: pos.z, ry, health }),
      });
      if (res.status === 400 && !this._rejoining) {
        this._rejoining = true;
        try { await this.connect(this.base, this.name); }
        finally { this._rejoining = false; }
      }
    } catch (e) { /* ignore transient network errors */ }
  }

  async sendShoot(origin, dir) {
    if (!this.connected) return;
    try {
      await fetch(this.base + '/api/shoot', {
        method: 'POST',
        body: JSON.stringify({
          id: this.id, ox: origin.x, oy: origin.y, oz: origin.z,
          dx: dir.x, dy: dir.y, dz: dir.z,
        }),
      });
    } catch (e) { /* ignore */ }
  }

  async sendHit(targetId, damage) {
    if (!this.connected) return null;
    try {
      const res = await fetch(this.base + '/api/hit', {
        method: 'POST',
        body: JSON.stringify({ shooterId: this.id, targetId, damage }),
      });
      return await res.json();
    } catch (e) { return null; }
  }

  async leave() {
    if (!this.connected) return;
    try {
      await fetch(this.base + '/api/leave', { method: 'POST', body: JSON.stringify({ id: this.id }) });
    } catch (e) { /* ignore */ }
    this.connected = false;
  }
}

/* ---------------------------------------------------------------------- */
/* 7. HUD WIRING                                                          */
/* ---------------------------------------------------------------------- */

const hud = {
  healthFill: document.getElementById('health-fill'),
  healthNum: document.getElementById('health-num'),
  ammoCur: document.getElementById('ammo-cur'),
  ammoMax: document.getElementById('ammo-max'),
  reloadHint: document.getElementById('reload-hint'),
  kills: document.getElementById('hud-kills'),
  deaths: document.getElementById('hud-deaths'),
  killfeed: document.getElementById('killfeed'),
  hitmarker: document.getElementById('hitmarker'),
  vignette: document.getElementById('damage-vignette'),
  mpStatus: document.getElementById('mp-connection-status'),
};

function updateHealthHud(health, maxHealth) {
  const pct = Math.max(0, health / maxHealth) * 100;
  hud.healthFill.style.width = pct + '%';
  hud.healthNum.textContent = Math.round(health);
  if (pct < 30) hud.healthFill.style.background = 'linear-gradient(90deg,#e04b4b,#ff8a6b)';
  else hud.healthFill.style.background = 'linear-gradient(90deg,#35d16b,#7cf29a)';
}

function updateAmmoHud(cur, max, reloading) {
  hud.ammoCur.textContent = cur;
  hud.ammoMax.textContent = max;
  hud.reloadHint.classList.toggle('hidden', !reloading);
}

function updateScoreHud(kills, deaths) {
  hud.kills.textContent = kills;
  hud.deaths.textContent = deaths;
}

function flashHitmarker() {
  hud.hitmarker.classList.remove('show');
  void hud.hitmarker.offsetWidth;
  hud.hitmarker.classList.add('show');
}

function flashDamage() {
  hud.vignette.classList.add('show');
  setTimeout(() => hud.vignette.classList.remove('show'), 220);
}

function pushKillfeed(killer, victim) {
  const div = document.createElement('div');
  div.className = 'kf-item';
  div.innerHTML = `<span class="kf-killer">${escapeHtml(killer)}</span> eliminated <span class="kf-victim">${escapeHtml(victim)}</span>`;
  hud.killfeed.appendChild(div);
  setTimeout(() => div.remove(), 4000);
  while (hud.killfeed.children.length > 5) hud.killfeed.removeChild(hud.killfeed.firstChild);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/* ---------------------------------------------------------------------- */
/* 8. GAME STATE / MENUS / MAIN LOOP                                      */
/* ---------------------------------------------------------------------- */

const screens = {
  menu: document.getElementById('menu-screen'),
  lock: document.getElementById('lock-screen'),
  death: document.getElementById('death-screen'),
  loading: document.getElementById('loading-screen'),
  hud: document.getElementById('hud'),
};

function showOnly(names) {
  for (const key of Object.keys(screens)) {
    screens[key].classList.toggle('hidden', !names.includes(key));
  }
}
showOnly(['menu']);

// ---- Three.js core setup ----
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(78, window.innerWidth / window.innerHeight, 0.05, 500);
camera.rotation.order = 'YXZ';

buildSky(scene);
buildLighting(scene);
const colliders = buildLevel(scene);

const controls = new PointerLockControls(camera, document.body);
const player = new Player(camera);
player.camera.position.copy(player.position);
const weapon = new Weapon(camera, scene);
scene.add(camera);

const raycaster = new THREE.Raycaster();
const clock = new THREE.Clock();

let mode = null; // 'single' | 'multi'
let bots = [];
let remoteMeshes = new Map(); // id -> {group, nameTag, lastState, targetPos}
let network = new Network();
let gameActive = false;

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onWindowResize);
onWindowResize();

// ---- Input ----
const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
let touchPlaying = false; // analogous to controls.isLocked, but for touch devices
function isPlaying() { return controls.isLocked || touchPlaying; }

window.addEventListener('keydown', (e) => {
  player.keys[e.code] = true;
  if (e.code === 'KeyR') weapon.startReload();
  if (e.code === 'Escape' && touchPlaying) { touchPlaying = false; showOnly(['lock']); }
});
window.addEventListener('keyup', (e) => { player.keys[e.code] = false; });

let mouseFiring = false;
document.addEventListener('mousedown', (e) => {
  if (e.button === 0 && controls.isLocked) mouseFiring = true;
});
document.addEventListener('mouseup', (e) => {
  if (e.button === 0) mouseFiring = false;
});

controls.addEventListener('unlock', () => {
  mouseFiring = false;
  if (gameActive) showOnly(['lock']);
});

const btnLock = document.getElementById('btn-lock');
if (isTouchDevice) btnLock.textContent = 'TAP TO PLAY';
btnLock.addEventListener('click', () => {
  if (isTouchDevice) {
    touchPlaying = true;
    document.getElementById('touch-controls').classList.remove('hidden');
    showOnly(['hud']);
  } else {
    controls.lock();
  }
  if (mode === 'multi') network.sendUpdate(player.position, camera.rotation.y, player.health);
});
controls.addEventListener('lock', () => {
  showOnly(['hud']);
  if (mode === 'multi') network.sendUpdate(player.position, camera.rotation.y, player.health);
});

// ---- Touch controls (joystick move, drag look, fire/jump/reload buttons) ----
let touchFiring = false;
if (isTouchDevice) {
  const joystickZone = document.getElementById('touch-joystick-zone');
  const joystickKnob = document.getElementById('joystick-knob');
  const lookZone = document.getElementById('touch-look-zone');
  const fireBtn = document.getElementById('touch-fire');
  const jumpBtn = document.getElementById('touch-jump');
  const reloadBtn = document.getElementById('touch-reload');

  const JOY_RADIUS = 55;
  const LOOK_SENSITIVITY = 0.0035;
  let joyTouchId = null, joyCenter = { x: 0, y: 0 };
  let lookTouchId = null, lookLast = { x: 0, y: 0 };

  joystickZone.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const t = e.changedTouches[0];
    joyTouchId = t.identifier;
    joyCenter = { x: t.clientX, y: t.clientY };
  }, { passive: false });

  joystickZone.addEventListener('touchmove', (e) => {
    e.preventDefault();
    for (const t of e.changedTouches) {
      if (t.identifier !== joyTouchId) continue;
      let dx = t.clientX - joyCenter.x;
      let dy = t.clientY - joyCenter.y;
      const dist = Math.min(JOY_RADIUS, Math.hypot(dx, dy)) || 0;
      const angle = Math.atan2(dy, dx);
      const kx = Math.cos(angle) * dist, ky = Math.sin(angle) * dist;
      joystickKnob.style.transform = `translate(${kx}px, ${ky}px)`;
      player.touchMove.x = kx / JOY_RADIUS;
      player.touchMove.y = -ky / JOY_RADIUS; // screen-up (negative dy) = forward
    }
  }, { passive: false });

  function endJoystick(e) {
    for (const t of e.changedTouches) {
      if (t.identifier !== joyTouchId) continue;
      joyTouchId = null;
      player.touchMove.x = 0;
      player.touchMove.y = 0;
      joystickKnob.style.transform = 'translate(0px, 0px)';
    }
  }
  joystickZone.addEventListener('touchend', endJoystick);
  joystickZone.addEventListener('touchcancel', endJoystick);

  lookZone.addEventListener('touchstart', (e) => {
    e.preventDefault();
    const t = e.changedTouches[0];
    lookTouchId = t.identifier;
    lookLast = { x: t.clientX, y: t.clientY };
  }, { passive: false });

  lookZone.addEventListener('touchmove', (e) => {
    e.preventDefault();
    for (const t of e.changedTouches) {
      if (t.identifier !== lookTouchId) continue;
      const dx = t.clientX - lookLast.x;
      const dy = t.clientY - lookLast.y;
      lookLast = { x: t.clientX, y: t.clientY };
      camera.rotation.y -= dx * LOOK_SENSITIVITY;
      camera.rotation.x -= dy * LOOK_SENSITIVITY;
      const limit = Math.PI / 2 - 0.01;
      camera.rotation.x = THREE.MathUtils.clamp(camera.rotation.x, -limit, limit);
    }
  }, { passive: false });

  function endLook(e) {
    for (const t of e.changedTouches) {
      if (t.identifier === lookTouchId) lookTouchId = null;
    }
  }
  lookZone.addEventListener('touchend', endLook);
  lookZone.addEventListener('touchcancel', endLook);

  fireBtn.addEventListener('touchstart', (e) => {
    e.preventDefault();
    fireBtn.classList.add('active');
    touchFiring = true;
  }, { passive: false });
  function stopFire(e) { e.preventDefault(); fireBtn.classList.remove('active'); touchFiring = false; }
  fireBtn.addEventListener('touchend', stopFire, { passive: false });
  fireBtn.addEventListener('touchcancel', stopFire, { passive: false });

  jumpBtn.addEventListener('touchstart', (e) => { e.preventDefault(); jumpBtn.classList.add('active'); player.keys['Space'] = true; }, { passive: false });
  function stopJump(e) { e.preventDefault(); jumpBtn.classList.remove('active'); player.keys['Space'] = false; }
  jumpBtn.addEventListener('touchend', stopJump, { passive: false });
  jumpBtn.addEventListener('touchcancel', stopJump, { passive: false });

  reloadBtn.addEventListener('touchstart', (e) => { e.preventDefault(); weapon.startReload(); }, { passive: false });
}

// ---- Menu wiring ----
const nameInput = document.getElementById('name-input');
const serverInput = document.getElementById('server-input');
document.getElementById('btn-singleplayer').addEventListener('click', startSinglePlayer);
document.getElementById('btn-multiplayer').addEventListener('click', () => {
  document.getElementById('mp-options').classList.remove('hidden');
  serverInput.value = window.location.origin;
});
document.getElementById('btn-connect').addEventListener('click', startMultiPlayer);

function playerName() {
  return (nameInput.value || 'Player').trim().slice(0, 16) || 'Player';
}

function startSinglePlayer() {
  mode = 'single';
  bots = [];
  for (let i = 0; i < BOT_COUNT; i++) bots.push(new Bot(scene, i, colliders));
  beginMatch();
}

async function startMultiPlayer() {
  const statusEl = document.getElementById('mp-status');
  statusEl.textContent = 'Connecting...';
  try {
    const addr = serverInput.value.trim() || window.location.origin;
    await network.connect(addr, playerName());
    statusEl.textContent = 'Connected as ' + playerName();
    mode = 'multi';
    beginMatch();
  } catch (e) {
    statusEl.textContent = 'Could not connect. Check the address and try again.';
  }
}

function beginMatch() {
  player.respawn();
  weapon.ammo = weapon.maxAmmo;
  updateHealthHud(player.health, player.maxHealth);
  updateAmmoHud(weapon.ammo, weapon.maxAmmo, false);
  updateScoreHud(player.kills, player.deaths);
  gameActive = true;
  showOnly(['lock']);
  clock.getDelta(); // reset
}

// ---- Shooting ----
function tryFire() {
  if (!weapon.canFire() || !player.alive) return;
  weapon.fire();

  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  const origin = camera.position.clone();

  // slight spread
  const spread = 0.008;
  dir.x += (Math.random() - 0.5) * spread;
  dir.y += (Math.random() - 0.5) * spread;
  dir.normalize();

  raycaster.set(origin, dir);
  raycaster.far = 200;

  const targets = [];
  const targetMap = new Map();
  if (mode === 'single') {
    for (const b of bots) {
      if (!b.alive) continue;
      targets.push(b.mesh.userData.bodyMesh, b.mesh.userData.headMesh);
      targetMap.set(b.mesh.userData.bodyMesh, b);
      targetMap.set(b.mesh.userData.headMesh, b);
    }
  } else if (mode === 'multi') {
    for (const [id, rm] of remoteMeshes) {
      targets.push(rm.group.userData.bodyMesh, rm.group.userData.headMesh);
      targetMap.set(rm.group.userData.bodyMesh, id);
      targetMap.set(rm.group.userData.headMesh, id);
    }
  }

  const worldColliders = colliders.map(c => c.mesh);
  const allObjects = [...targets, ...worldColliders];
  const hits = raycaster.intersectObjects(allObjects, false);

  let tracerEnd = origin.clone().addScaledVector(dir, 60);
  if (hits.length > 0) {
    const hit = hits[0];
    tracerEnd = hit.point;

    if (targetMap.has(hit.object)) {
      const isHead = hit.object.parent && hit.object.parent.userData.headMesh === hit.object;
      const damage = isHead ? 13 : 7;
      flashHitmarker();

      if (mode === 'single') {
        const bot = targetMap.get(hit.object);
        const killed = bot.takeDamage(damage);
        if (killed) {
          player.kills++;
          updateScoreHud(player.kills, player.deaths);
          pushKillfeed(playerName(), 'Bot ' + (bot.id + 1));
        }
      } else if (mode === 'multi') {
        const targetId = targetMap.get(hit.object);
        network.sendHit(targetId, damage).then(res => {
          if (res && res.killed) {
            player.kills++;
            updateScoreHud(player.kills, player.deaths);
          }
        });
      }
    }
  }

  createTracer(scene, weapon.muzzleWorldPosition, tracerEnd);
  if (mode === 'multi') network.sendShoot(origin, dir);
}

/* -- Bots shooting the player -- */
function botShootsPlayer(from, to, hit) {
  const tracerEnd = hit ? to.clone() : to.clone().add(new THREE.Vector3((Math.random() - 0.5) * 3, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 3));
  createTracer(scene, from, tracerEnd);
  if (hit && player.alive) {
    const died = player.takeDamage(4 + Math.random() * 3);
    updateHealthHud(player.health, player.maxHealth);
    flashDamage();
    if (died) onPlayerDeath('a bot');
  }
}

function onPlayerDeath(killerLabel) {
  updateScoreHud(player.kills, player.deaths);
  document.getElementById('death-text').textContent = 'YOU DIED';
  document.getElementById('death-sub').textContent = 'Eliminated by ' + killerLabel + '. Respawning...';
  showOnly(['death']);
  setTimeout(() => {
    player.respawn();
    weapon.ammo = weapon.maxAmmo;
    weapon.reloading = false;
    updateHealthHud(player.health, player.maxHealth);
    updateAmmoHud(weapon.ammo, weapon.maxAmmo, false);
    if (isPlaying()) showOnly(['hud']); else showOnly(['lock']);
  }, 2200);
}

// ---- Multiplayer remote player rendering ----
function remoteGroundY(state) {
  // state.y is the other player's eye height (camera Y). Convert that to
  // how far their mesh's feet should be above ground, so jumping and
  // standing on crates/platforms is actually visible to everyone else.
  return Math.max(0, (typeof state.y === 'number' ? state.y : EYE_HEIGHT) - EYE_HEIGHT);
}

function ensureRemoteMesh(id, state) {
  if (remoteMeshes.has(id)) return remoteMeshes.get(id);
  const group = buildBotMesh(0x4b8fd1);
  const tag = nameSprite(state.name || 'Player', '#7fe7ff');
  tag.position.y = 2.05;
  group.add(tag);
  scene.add(group);
  const rm = { group, tag, targetPos: new THREE.Vector3(state.x, remoteGroundY(state), state.z), targetRy: state.ry || 0 };
  remoteMeshes.set(id, rm);
  return rm;
}

function removeRemoteMesh(id) {
  const rm = remoteMeshes.get(id);
  if (rm) {
    scene.remove(rm.group);
    remoteMeshes.delete(id);
  }
}

function syncRemotePlayers() {
  const seen = new Set();
  for (const [id, state] of network.remotePlayers) {
    seen.add(id);
    const rm = ensureRemoteMesh(id, state);
    rm.targetPos.set(state.x, remoteGroundY(state), state.z);
    rm.targetRy = state.ry || 0;
    rm.group.visible = state.health > 0;
  }
  for (const id of Array.from(remoteMeshes.keys())) {
    if (!seen.has(id)) removeRemoteMesh(id);
  }
}

let networkTimer = 0;
function updateNetworking(dt) {
  networkTimer += dt;
  if (networkTimer < 0.05) return;
  networkTimer = 0;

  network.sync(player.position, camera.rotation.y, player.health, (ev) => {
    if (ev.type === 'kill') pushKillfeed(ev.killer, ev.victim);
    if (ev.type === 'hit' && ev.targetId === network.id && player.alive) {
      const died = player.takeDamage(ev.damage);
      updateHealthHud(player.health, player.maxHealth);
      flashDamage();
      if (died) onPlayerDeath('another player');
    }
    if (ev.type === 'shoot' && remoteMeshes.has(ev.id)) {
      const rm = remoteMeshes.get(ev.id);
      const from = new THREE.Vector3(ev.ox, ev.oy, ev.oz);
      const dir = new THREE.Vector3(ev.dx, ev.dy, ev.dz).normalize();
      createTracer(scene, from, from.clone().addScaledVector(dir, 40));
    }
  }).then(syncRemotePlayers);

  hud.mpStatus.textContent = network.connected
    ? `LAN MATCH \u00b7 ${remoteMeshes.size} other player(s) online`
    : '';
}

/* ---- Main animation loop ---- */
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  if (gameActive && isPlaying()) {
    player.update(dt, colliders, controls);

    const isMoving = player.keys['KeyW'] || player.keys['KeyA'] || player.keys['KeyS'] || player.keys['KeyD'] ||
      Math.abs(player.touchMove.x) > 0.05 || Math.abs(player.touchMove.y) > 0.05;
    weapon.update(dt, !!isMoving);
    updateAmmoHud(weapon.ammo, weapon.maxAmmo, weapon.reloading);

    if (mouseFiring || touchFiring) tryFire();

    if (mode === 'single') {
      for (const b of bots) {
        b.update(dt, player.position, player.alive, botShootsPlayer);
      }
    } else if (mode === 'multi') {
      updateNetworking(dt);
      for (const [, rm] of remoteMeshes) {
        rm.group.position.lerp(rm.targetPos, Math.min(1, dt * 10));
        rm.group.rotation.y += (rm.targetRy - rm.group.rotation.y) * Math.min(1, dt * 10);
      }
    }
  }

  renderer.render(scene, camera);
}

showOnly(['menu']);
document.getElementById('loading-screen').classList.add('hidden');
requestAnimationFrame(animate);

window.addEventListener('beforeunload', () => { network.leave(); });
