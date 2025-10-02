from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random, os

app = Ursina()

# Game state
cubes = []
score = 0
time_left = 60
paused = False
in_menu = True
game_over = False

# --- Load High Score from file ---
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            high_score = int(f.read().strip())
        except:
            high_score = 0
else:
    high_score = 0

# UI Elements (hidden until game starts)
score_text = Text(text="", position=(-0.85, 0.45), scale=2, color=color.white, enabled=False)
timer_text = Text(text="", position=(0.7, 0.45), scale=2, color=color.yellow, enabled=False)
pause_text = Text(text="PAUSED", origin=(0,0), scale=3, color=color.red, enabled=False)

# Menu UI
title_text = Text(text="CubeBlast", scale=3, origin=(0,0), y=0.3, color=color.azure)
start_button = Button(text="Start Game", scale=(0.2,0.1), y=0, color=color.green)
quit_button = Button(text="Quit", scale=(0.2,0.1), y=-0.15, color=color.red)

# Game Over UI
game_over_text = Text(text="GAME OVER", scale=3, origin=(0,0), y=0.25, color=color.red, enabled=False)
final_score_text = Text(text="", scale=2, origin=(0,0), y=0.05, color=color.white, enabled=False)
high_score_text = Text(text="", scale=2, origin=(0,0), y=-0.1, color=color.orange, enabled=False)
play_again_button = Button(text="Play Again", scale=(0.2,0.1), y=-0.3, color=color.green, enabled=False)
menu_button = Button(text="Return to Menu", scale=(0.25,0.1), y=-0.45, color=color.azure, enabled=False)
quit_button2 = Button(text="Quit", scale=(0.2,0.1), y=-0.6, color=color.red, enabled=False)

# Functions
def update_score():
    score_text.text = f"Score: {score}"

def update_timer():
    timer_text.text = f"Time: {max(0, int(time_left))}"

def spawn_cube():
    x = random.randint(-8, 8)
    z = random.randint(-8, 8)
    cube = Entity(
        model='cube',
        color=color.azure,
        scale=1,
        position=(x, 0.5, z),
        collider='box'
    )
    cubes.append(cube)

def reset_game():
    global score, time_left, paused, game_over
    for cube in cubes:
        destroy(cube)
    cubes.clear()
    score = 0
    time_left = 60
    paused = False
    game_over = False
    pause_text.enabled = False
    mouse.locked = True
    for i in range(20):
        spawn_cube()
    update_score()
    update_timer()
    score_text.enabled = True
    timer_text.enabled = True

def start_game():
    global in_menu, player
    in_menu = False
    # Hide menu UI
    title_text.enabled = False
    start_button.enabled = False
    quit_button.enabled = False
    # Hide game over UI
    game_over_text.enabled = False
    final_score_text.enabled = False
    high_score_text.enabled = False
    play_again_button.enabled = False
    menu_button.enabled = False
    quit_button2.enabled = False
    # Enable game
    reset_game()
    # Spawn player
    player = FirstPersonController()

def quit_game():
    application.quit()

def return_to_menu():
    global in_menu, game_over
    in_menu = True
    game_over = False
    # Hide game UI
    score_text.enabled = False
    timer_text.enabled = False
    pause_text.enabled = False
    # Destroy cubes & player
    for cube in cubes:
        destroy(cube)
    cubes.clear()
    if "player" in globals():
        destroy(player)
    # Show menu
    title_text.enabled = True
    start_button.enabled = True
    quit_button.enabled = True
    game_over_text.enabled = False
    final_score_text.enabled = False
    high_score_text.enabled = False
    play_again_button.enabled = False
    menu_button.enabled = False
    quit_button2.enabled = False

def show_game_over():
    global game_over, high_score
    game_over = True
    mouse.locked = False
    score_text.enabled = False
    timer_text.enabled = False
    pause_text.enabled = False

    # Update high score if beaten
    if score > high_score:
        high_score = score
        with open("highscore.txt", "w") as f:
            f.write(str(high_score))

    game_over_text.enabled = True
    final_score_text.enabled = True
    high_score_text.enabled = True
    final_score_text.text = f"Final Score: {score}"
    high_score_text.text = f"High Score: {high_score}"
    play_again_button.enabled = True
    menu_button.enabled = True
    quit_button2.enabled = True

# Button actions
start_button.on_click = start_game
quit_button.on_click = quit_game
play_again_button.on_click = start_game
menu_button.on_click = return_to_menu
quit_button2.on_click = quit_game

# Explosion effect (no sound)
def explode(entity):
    for i in range(10):
        debris = Entity(
            model='cube',
            color=entity.color,
            scale=0.2,
            position=entity.position + Vec3(
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5)
            )
        )
        debris.animate_position(
            debris.position + Vec3(
                random.uniform(-2, 2),
                random.uniform(1, 3),
                random.uniform(-2, 2)
            ),
            duration=0.5
        )
        debris.fade_out(0.7)

def input(key):
    global score, paused
    if in_menu or game_over:
        return

    if not paused and time_left > 0:
        if key == 'left mouse down':
            hit_info = mouse.hovered_entity
            if hit_info in cubes:
                explode(hit_info)
                destroy(hit_info)
                cubes.remove(hit_info)
                spawn_cube()
                score += 1
                update_score()

    if key == 'p':
        paused = not paused
        pause_text.enabled = paused
        mouse.locked = not paused

    if key == 'r':
        reset_game()

    if key == 'escape':
        application.quit()

def update():
    global time_left
    if not in_menu and not paused and not game_over:
        if time_left > 0:
            time_left -= time.dt
            update_timer()
        else:
            show_game_over()

# Sky & ground
Entity(model='plane', scale=50, texture='white_cube', texture_scale=(50,50), color=color.green, collider='box')
Sky()

app.run()
