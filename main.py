import pygame
import sys
import pathfinder
import renderer
import constants
from dungeon import Dungeon
from shadowcaster import Shadowcaster

# This script launches the game.

"""
TODO:
- Make isometric battle grid interactive
- Implement saving/loading game
- Implement algorithm for spawning enemies, chests, etc
- Finish state logic
- Integrate with menus and combat system
- Refactor code into functions where necessary
"""

### Controls (edit once menus are done) ###
# Click mouse to move
# Press q to quit

# Move this to actor class
# Accepts clicked tile as input and outputs path to it
def move(dest, dungeon):
    path_map = pathfinder.findPath(dungeon, dest)
    cur = dest
    move_path = [cur]
    while cur != dungeon.player_tile:
        cur = path_map[cur][3]
        move_path.insert(0, cur)
    return move_path

# Load sprites used for isometric rendering and scale them up to 32x32
# Use sprite.image for drawing and sprite.rect for collision detection in isometric mode
def load_sprites():
    images = [
        pygame.image.load("Resources/Images/CUBE_FLOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WALL.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_DOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WATER.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_PLAYER.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_ENEMY.png").convert_alpha()
    ]
    sprites = []
    for i in range(0, len(images)):
        images[i] = pygame.transform.scale(images[i], (constants.TILE_SIZE * 2, constants.TILE_SIZE * 2))
        sprites.append(pygame.sprite.Sprite())
        sprites[i].image = images[i]
        sprites[i].rect = sprites[i].image.get_rect()
    return sprites

# Load audio
def load_audio():
    audio = [
        pygame.mixer.Sound("Resources/SFX/GAME_OVER.mp3"),
        pygame.mixer.Sound("Resources/SFX/LEVEL_UP.mp3"),
        pygame.mixer.Sound("Resources/SFX/MELEE_ATTACK.mp3"),
        pygame.mixer.Sound("Resources/SFX/OPEN_DOOR.mp3"),
        pygame.mixer.Sound("Resources/SFX/VICTORY.mp3")
    ]
    return audio

def convert_to_iso(x, y):
    return [x*constants.iso_matrix[0][0] + y*constants.iso_matrix[0][1],
            x*constants.iso_matrix[1][0] + y*constants.iso_matrix[1][1]]

# Transorm mouse position by inverse isometric matrix
# for tile hover/click handling in combat
def iso_cursor_transform(cursor_pos):
    return (cursor_pos[0]*constants.click_matrix[0][0] + cursor_pos[1]*constants.click_matrix[0][1],
            cursor_pos[0]*constants.click_matrix[1][0] + cursor_pos[1]*constants.click_matrix[1][1])

# Initialization
pygame.init()
pygame.mixer.init()
game_state = constants.EXPLORATION_STATE
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
viewport_cols = screen_width // constants.TILE_SIZE
viewport_rows = screen_height // constants.TILE_SIZE
dungeon_cols = viewport_cols * 10
dungeon_rows = viewport_rows * 10
clock = pygame.time.Clock()
sprites = load_sprites()
sounds = load_audio()
rend_mode = constants.TOP_DOWN
move_start_time = 0
move_elapsed_time = 0
move_path_nodes = None
move_path = None
move_step_count = 0
move_dest = None
has_moved = False
speed = 4
start_combat = False

# Generate dungeon
dungeon = Dungeon(constants.TILE_SIZE, 1, 1, dungeon_cols, dungeon_rows, 64, 20)
dungeon.generateDungeon()

# Player (change to instance of actor class)
player = [
    (dungeon.player_tile%dungeon_cols)*constants.TILE_SIZE,
    (dungeon.player_tile//dungeon_cols)*constants.TILE_SIZE
]

# Camera that follows player in top down mode
camera = [
    max(0, player[0] - screen_width // 2),
    max(0, player[1] - screen_height // 2)
]

# Casts shadows on tiles outside of the player's field of view initially
# and makes shadow tiles visible once in field of view.
# Run initial fov once on game start to light up starting position
shadowcaster = Shadowcaster(dungeon_cols, dungeon_rows)
shadowcaster.fov(player[0]//constants.TILE_SIZE, player[1]//constants.TILE_SIZE, 32, dungeon)

# Game loop
run = True
while run:
    # Get mouse position each frame for hover/click handling
    if rend_mode == constants.TOP_DOWN:
        mouse_pos = pygame.mouse.get_pos()
    else:
        mouse_pos = iso_cursor_transform(mouse_pos)

    # On each frame, clear and redraw the screen
    screen.fill((0, 0, 0))
    offsets = renderer.renderTilemap(camera, rend_mode, sprites, dungeon, player, shadowcaster, start_combat, has_moved, viewport_cols, viewport_rows, constants.TILE_SIZE, screen, mouse_pos)
    if has_moved:
        has_moved = False

    # Controls for exploration state
    if game_state == constants.EXPLORATION_STATE:
        for e in pygame.event.get():
            
            # on quit
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()
                
                # TEST - Toggle rendering mode - Change to toggle on enter/exit combat
                elif e.key == pygame.K_m:
                    if rend_mode == constants.TOP_DOWN:
                        rend_mode = constants.ISOMETRIC
                        start_combat = True
                    else:
                        rend_mode = constants.TOP_DOWN

            # Get clicked tile using click event position and
            # pass it to pathfinder
            if e.type == pygame.MOUSEBUTTONDOWN:
                viewport_col = camera[0] // constants.TILE_SIZE
                viewport_row = camera[1] // constants.TILE_SIZE
                dest_col = (int(mouse_pos[0] - offsets[0]) // constants.TILE_SIZE) + viewport_col
                dest_row = (int(mouse_pos[1] - offsets[1]) // constants.TILE_SIZE) + viewport_row
                move_dest = dest_row * dungeon_cols + dest_col
                if dungeon.tiles[move_dest] == constants.FLOOR or dungeon.tiles[move_dest] == constants.DOOR:
                    move_path = move(dest_row * dungeon_cols + dest_col, dungeon)
                    move_step_count = 0
                    game_state = constants.MOVING_STATE
                    move_start_time = pygame.time.get_ticks()

    elif game_state == constants.MOVING_STATE:
        # Movement along path to clicked tile
        # Only pan camera in top down mode
        if move_step_count < len(move_path):
            next_tile = move_path[move_step_count]
            dx = (next_tile%dungeon_cols)*constants.TILE_SIZE
            dy = (next_tile//dungeon_cols)*constants.TILE_SIZE
            if pygame.time.get_ticks() - move_start_time > 10:
                if dx > player[0]:
                    player[0] += speed
                    if not rend_mode == constants.ISOMETRIC:
                        camera[0] += speed
                elif dx < player[0]:
                    player[0] -= speed
                    if not rend_mode == constants.ISOMETRIC:
                        camera[0] -= speed
                elif dy > player[1]:
                    player[1] += speed
                    if not rend_mode == constants.ISOMETRIC:
                        camera[1] += speed
                elif dy < player[1]:
                    player[1] -= speed
                    if not rend_mode == constants.ISOMETRIC:
                        camera[1] -= speed
                if player[0] == dx and player[1] == dy:
                    if dungeon.tiles[next_tile] == constants.DOOR:
                        sounds[constants.OPEN_DOOR].play()
                        dungeon.open_door(next_tile)
                    dungeon.player_tile = next_tile
                    has_moved = True
                    move_step_count += 1
                move_start_time = pygame.time.get_ticks()
        else:
            game_state = constants.EXPLORATION_STATE

    #elif game_state == constants.COMBAT_STATE:

    pygame.display.flip()
    clock.tick(60)