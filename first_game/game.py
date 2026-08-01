from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import math
import threading
import time as py_time

# Initialize the game engine
app = Ursina()

# --- AAA SETUP: Lighting & Shadows ---
Entity.default_shader = lit_with_shadows_shader
DirectionalLight(y=10, z=10, shadows=True, color=color.white)
AmbientLight(color=color.rgba(120, 120, 120, 0.2))

# --- ENVIRONMENT ---
ground = Entity(model='plane', collider='box', scale=100, texture='grass', texture_scale=(10,10))
Sky()

# --- PLAYER SETUP ---
player = FirstPersonController(model='cube', y=0, color=color.orange, origin_y=-0.5, speed=8, collider='box')
player.cursor.visible = True

# --- WEAPON & GRAPHICS SETUP ---
gun = Entity(parent=camera, model='cube', position=(0.4, -0.2, 0.5), scale=(0.1, 0.1, 0.6), color=color.dark_gray)
muzzle_flash = Entity(parent=gun, z=0.4, model='quad', scale=0.3, color=color.yellow, enabled=False)

# --- UI ELEMENTS ---
score_text = Text(text='SCORE: 0', position=(-0.85, 0.45), scale=2, color=color.white)
game_over_text = Text(text='', position=(0, 0), origin=(0,0), scale=3, color=color.red, enabled=False)
instruction_text = Text(text='Press R to Restart', position=(0, -0.1), origin=(0,0), scale=1.5, color=color.light_gray, enabled=False)

# --- GAMEPLAY STATE ---
enemies = []
score = 0
game_time = 0
is_game_over = False

# --- FRONT 120-DEGREE SPAWNER (15m Distance) ---
def spawn_enemy():
    if is_game_over:
        return
    
    # Random angle offset within a 120-degree window (-60 to +60 degrees)
    angle_offset = random.uniform(-math.radians(60), math.radians(60))
    spawn_distance = 15.0
    
    # Get player forward direction vector flattened on the ground plane
    forward_dir = player.forward
    forward_dir.y = 0
    forward_dir = forward_dir.normalized()
    
    # Rotate vector by angle offset around the Y axis
    cos_a = math.cos(angle_offset)
    sin_a = math.sin(angle_offset)
    x = forward_dir.x * cos_a - forward_dir.z * sin_a
    z = forward_dir.x * sin_a + forward_dir.z * cos_a
    spawn_dir = Vec3(x, 0, z).normalized()
    
    spawn_pos = player.position + spawn_dir * spawn_distance
    spawn_pos.y = 1.0

    enemy = Entity(
        model='cube',
        color=color.rgb(180, 20, 20),
        scale=(1.2, 2.2, 1.2),
        position=spawn_pos,
        collider='box'
    )
    enemies.append(enemy)

def wave_spawner():
    while True:
        if not is_game_over:
            spawn_enemy()
        py_time.sleep(1.5)

# Start background spawner thread
threading.Thread(target=wave_spawner, daemon=True).start()

# --- SHOOTING & VISUAL GRAPHICS ---
def shoot():
    global score
    if is_game_over:
        return
    
    # Trigger Muzzle Flash effect
    muzzle_flash.enabled = True
    invoke(setattr, muzzle_flash, 'enabled', False, delay=0.05)
    
    # Raycast check for hit targets
    if mouse.hovered_entity and mouse.hovered_entity in enemies:
        hit_target = mouse.hovered_entity
        
        # Improved Bullet Graphics: Spawn a glowing particle spark effect on impact
        hit_effect = Entity(model='sphere', color=color.yellow, scale=0.4, position=hit_target.position)
        destroy(hit_effect, delay=0.08)
        
        enemies.remove(hit_target)
        destroy(hit_target)
        
        score += 100
        score_text.text = f'SCORE: {score}'

# --- GAME LOOP ---
def update():
    global game_time, score, is_game_over
    
    if is_game_over:
        if held_keys['r']:
            reset_game()
        return

    game_time += time.dt
    
    # Speed increases very slowly based on both survival time and score
    current_speed = 2.0 + (game_time * 0.05) + (score * 0.005)

    # Update enemy AI positions and check front-facing collisions
    for enemy in list(enemies):
        enemy.look_at(player)
        enemy.rotation_x = 0
        enemy.rotation_z = 0
        enemy.position += enemy.forward * current_speed * time.dt

        dist = distance(enemy, player)
        
        # Game Over triggered ONLY when an enemy in the front 120-degree region touches the player
        if dist < 1.5:
            to_enemy = (enemy.position - player.position)
            to_enemy.y = 0
            to_enemy = to_enemy.normalized()
            
            fwd = player.forward
            fwd.y = 0
            fwd = fwd.normalized()
            
            # Dot product >= 0.5 corresponds to the 120-degree front cone (cos(60 deg) = 0.5)
            if fwd.dot(to_enemy) >= 0.5:
                trigger_game_over()
                break

def trigger_game_over():
    global is_game_over
    is_game_over = True
    game_over_text.text = f"GAME OVER\nFinal Score: {score}"
    game_over_text.enabled = True
    instruction_text.enabled = True
    player.speed = 0

def reset_game():
    global score, game_time, is_game_over
    for e in enemies:
        destroy(e)
    enemies.clear()
    score = 0
    game_time = 0
    is_game_over = False
    score_text.text = 'SCORE: 0'
    game_over_text.enabled = False
    instruction_text.enabled = False
    player.speed = 8
    player.position = (0, 0, 0)

def input(key):
    if key == 'left mouse down':
        shoot()
    if key == 'escape':
        quit()

# Run the game application
app.run()