import pygame
import sys
import pathfinder
import renderer
import tile_types
from dungeon import Dungeon
from shadowcaster import Shadowcaster

# This script launches the game.

"""
TODO:
- Finish dungeon template system
- Implement isometric rendering mode for combat
- Implement algorithm for spawning enemies, items, and portal
- Finish implementing state logic
- Integrate with menus and combat system
- Refactor code into functions where necessary
"""

### Constants ###
WIN_WIDTH = 1280                                                # Screen resolution width
WIN_HEIGHT = 720                                                # Screen resolution height
TILE_SIZE = 16                                                  # Width/height of each tile

# Game states
EXPLORATION_STATE = 0
COMBAT_STATE = 1
MENU_STATE = 2
MOVING_STATE = 3

### Controls (edit once menus are done) ###
# Click mouse to move
# Press q to quit

# Initialization
pygame.init()
viewport_cols = WIN_WIDTH // TILE_SIZE                          # viewport horizontal tile count
viewport_rows = WIN_HEIGHT // TILE_SIZE                         # viewport vertical tile count
dungeon_cols = viewport_cols * 10                               # dungeon horizontal tile count
dungeon_rows = viewport_rows * 10                               # dungeon vertical tile count
game_state = EXPLORATION_STATE                                  # game state dictates what happens in game loop
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))       # surface to draw graphics to
clock = pygame.time.Clock()                                     # game clock
speed = 4                                                       # px/frame of movement

# Variables used to track player movement
move_start_time = 0
move_elapsed_time = 0
move_path_nodes = None
move_path = None
move_step_count = 0
move_dest = None

# Casts shadows on tiles outside of the player's field of view
# and makes shadow tiles visible once in field of view.
shadowcaster = Shadowcaster(dungeon_cols, dungeon_rows)

# Procedurally generate a dungeon using binary spatial partitioning
dungeon = Dungeon(TILE_SIZE, 0, 0, dungeon_cols, dungeon_rows, 80)
dungeon.generateDungeon()

# Later change player to player object
player = [
    (dungeon.player_tile%dungeon_cols)*TILE_SIZE,
    (dungeon.player_tile//dungeon_cols)*TILE_SIZE
]

# Game loop
run = True
while run:
    # On each frame, clear and redraw the screen
    screen.fill((36, 31, 49))
    vp_pos = renderer.renderTilemap(dungeon, player, shadowcaster, viewport_cols, viewport_rows, TILE_SIZE, screen)

    # Controls for exploration state
    if game_state == EXPLORATION_STATE:
        for e in pygame.event.get():
            # on quit
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()
            # Get clicked tile using click event position and
            # pass it to pathfinder
            if e.type == pygame.MOUSEBUTTONDOWN:

                # Make this a function with viewport position as input
                # and destination tile as output that can be passed into
                # pathfinder
                viewport_col = vp_pos % dungeon_cols
                viewport_row = vp_pos // dungeon_cols
                dest_col = (int(e.pos[0]) // TILE_SIZE) + viewport_col
                dest_row = (int(e.pos[1]) // TILE_SIZE) + viewport_row
                move_dest = dest_row * dungeon_cols + dest_col

                if dungeon.tiles[move_dest] == tile_types.FLOOR or dungeon.tiles[move_dest] == tile_types.DOOR:
                    move_path_nodes = pathfinder.findPath(dungeon, move_dest)
                    cur = move_dest
                    move_path = [cur]
                    while cur != dungeon.player_tile:
                        cur = move_path_nodes[cur][3]
                        move_path.insert(0, cur)
                    move_step_count = 0
                    game_state = MOVING_STATE
                    move_start_time = pygame.time.get_ticks()

    elif game_state == MOVING_STATE:
        # Make this a function
        if move_step_count < len(move_path):
            next_tile = move_path[move_step_count]
            dx = (next_tile%dungeon_cols)*TILE_SIZE
            dy = (next_tile//dungeon_cols)*TILE_SIZE
            if pygame.time.get_ticks() - move_start_time > 10:
                if dx > player[0]:
                    player[0] = min(player[0] + speed, dx)
                elif dx < player[0]:
                    player[0] = max(player[0] - speed, dx)
                elif dy > player[1]:
                    player[1] = min(player[1] + speed, dy)
                elif dy < player[1]:
                    player[1] = max(player[1] - speed, dy)
                if player[0] == dx and player[1] == dy:
                    if dungeon.tiles[next_tile] == tile_types.DOOR:
                        dungeon.open_door(next_tile)
                    dungeon.player_tile = next_tile
                    move_step_count += 1
                move_start_time = pygame.time.get_ticks()
        else:
            game_state = EXPLORATION_STATE

    pygame.display.flip()
    clock.tick(60)