import pygame
import sys
import pathfinder
import constants
from dungeon import Dungeon
from renderer import Renderer
from shadowcaster import Shadowcaster
from combatActors import *

# This script launches the game.

"""
TODO:
- Make hovering over battle grid tile color it with partially transparent red cube
- Make hovering over battle grid obstacles call recursive function that makes all tiles
  in the obstacle partially transparent (same if an actor is blocked by one)
- Use Actor objects for player/enemies.
- Make function to spawn actors, chests and loot in chests by level/rarity,
  including keys
- Implement portal room with 4 keyhole tiles that, when unlocked,
  activate a portal in center of room that renders vortex animation
- Go through portal to get to the next dungeon
- Make isometric battle grid interactive
- Implement saving/loading game
- Finish state logic
- Integrate with menus and combat system
- To implement save/load, create a dict containing every object that
  needs to be serialized and use pickle module to save/load to file
- Add remaining sfx
- Modify rects/cube faces to use sprite art
"""

#################################################
# CONTROLS (temporary until menus are added in) #
#################################################
#
# M to toggle between top down and isometric
# Click on floor/door tiles to move to them
# Q to quit

# Move this to actor class
# Accepts clicked tile as input and outputs path to it
# import dungeon and renderer in combatActors
def move(dest, dungeon, state, ren):
    path_map = pathfinder.findPath(dungeon, dest, state, ren.get_battle_grid())
    move_path = None
    if path_map:
        cur = dest
        move_path = [cur]
        while cur != dungeon.player_tile:
            cur = path_map[cur][3]
            move_path.insert(0, cur)
    return move_path

# Load sprites used for isometric rendering and scale them up to 32x32
# Use sprite.image for drawing and sprite.rect for collision detection in isometric mode
def load_images():
    images = [
        pygame.image.load("Resources/Images/CUBE_FLOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WALL.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_DOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WATER.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_PLAYER.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_ENEMY.png").convert_alpha()
    ]
    for i, img in enumerate(images):
        images[i] = pygame.transform.scale(img, (constants.TILE_SIZE * 2, constants.TILE_SIZE * 2))
    return images

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

# Initialization
pygame.init()
pygame.mixer.init()
game_state = constants.EXPLORATION_STATE
prev_game_state = None
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
viewport_cols = screen_width // constants.TILE_SIZE
viewport_rows = screen_height // constants.TILE_SIZE
dungeon_cols = viewport_cols * 10
dungeon_rows = viewport_rows * 10
clock = pygame.time.Clock()
images = load_images()
sounds = load_audio()
rend_mode = constants.TOP_DOWN
combat_check_timer = 0
game_time = 0
move_start_time = 0
move_elapsed_time = 0
move_path_nodes = None
move_path = None
move_step_count = 0
move_dest = None
has_moved = False
speed = 4
start_combat = False
illegal_move = False
changed_rooms = False

# Generate dungeon - change this once menus are done
dungeon = Dungeon(constants.TILE_SIZE, 1, 1, dungeon_cols, dungeon_rows, 64, 20)
dungeon.generateDungeon()

# Player (change to instance of actor class)
player = Player(dungeon.player_tile%dungeon_cols*constants.TILE_SIZE, dungeon.player_tile//dungeon_cols*constants.TILE_SIZE, "TEST", "Mage")

# FOV
shadowcaster = Shadowcaster(dungeon_cols, dungeon_rows)
shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, 32, dungeon)

# Draws tile graphics in either top down or isometric mode each frame
renderer = Renderer(viewport_cols, viewport_rows)

# Game loop
run = True
while run:
    combat_check_timer += game_time

    # On each frame, clear and redraw the screen
    screen.fill((0, 0, 0))

    # x,y offsets used for smooth movement of player/camera between tiles
    vp_pos, offsets = renderer.renderTilemap(screen_width, screen_height, rend_mode, images, dungeon, player, shadowcaster, start_combat, has_moved, viewport_cols, viewport_rows, constants.TILE_SIZE, screen)
    
    # Tells renderer to run shadowcaster if player moves in top down mode,
    # or to update the battle grid after actor movement if in combat
    if has_moved:
        has_moved = False

    # Triggers initial battle grid projection in renderer
    if start_combat:
        start_combat = False

    #############################################################
                        # EXPLORATION STATE #
    #############################################################
    if game_state == constants.EXPLORATION_STATE:

        # DEBUG - Remove these once combat/menus are done
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_m:
                    rend_mode = constants.ISOMETRIC
                    start_combat = True
                    game_state = constants.COMBAT_STATE

            # EXPLORATION MOVEMENT
            if e.type == pygame.MOUSEBUTTONDOWN:
                dest_col = (int(e.pos[0] - offsets[0]) // constants.TILE_SIZE) + vp_pos[0]
                dest_row = (int(e.pos[1] - offsets[1]) // constants.TILE_SIZE) + vp_pos[1]
                move_dest = dest_row * dungeon_cols + dest_col
                cur_tile = dungeon.tiles[move_dest]
                if cur_tile == constants.FLOOR or cur_tile == constants.DOOR:
                    move_path = move(dest_row * dungeon_cols + dest_col, dungeon, game_state, renderer)
                    if move_path:
                        move_step_count = 0
                        game_state = constants.MOVING_STATE
                        prev_game_state = constants.EXPLORATION_STATE
                        move_start_time = pygame.time.get_ticks()

    ##############################################################
    # COMMENT OUT THE CODE BELOW THIS IF YOU WANT TO BE ABLE TO
    # TOGGLE BETWEEN RENDERING MODES WITH 'M' KEY.
    #
    # UNCOMMENT THE CODE BELOW TO MAKE IT WHERE IT ENTERS COMBAT
    # WHEN YOU GET CLOSE ENOUGH TO AN ENEMY.
    #
    # WHEN AT LEAST 1 ENEMY IS DETECTED IN RANGE, IT WILL ENTER
    # COMBAT STATE - SEE BELOW.
    ##############################################################
        if combat_check_timer >= 0.2:
            combat_check_timer = 0   
            if dungeon.current_room:
                for enemy in dungeon.current_room.enemies:
                    x_dist = abs(player.x - enemy.x)
                    y_dist = abs(player.y - enemy.y)
                    if x_dist <= 32*constants.TILE_SIZE and y_dist <= 16*constants.TILE_SIZE:
                        rend_mode = constants.ISOMETRIC
                        start_combat = True
                        game_state = constants.COMBAT_STATE
                        break

    ########################################################
                        # MOVING STATE #
    ########################################################

    # MOVE PLAYER ALONG PATH TO DESTINATION TILE AT INCREMENT OF 'SPEED'
    # PER FRAME UNTIL EITHER DESTINATION IS REACHED OR PATH IS CUT SHORT
    # DUE TO ILLEGAL MOVE.
    # NEED TO MODIFY TO DO A CHECK TO SEE IF len(move_path) IS GREATER
    # THAN THE AMOUNT OF MOVEMENT AN ACTOR HAS BASED ON SPEED STAT.
    # ALSO NEED TO MODIFY SO THAT IF CLICKED TILE IS A CHEST, IT STOPS
    # PLAYER AT TILE BEFORE IT AND OPENS THE CHEST.
    elif game_state == constants.MOVING_STATE:
        illegal_move = False
        if move_step_count < len(move_path):
            next_tile = move_path[move_step_count]
            dx = (next_tile%dungeon_cols)*constants.TILE_SIZE
            dy = (next_tile//dungeon_cols)*constants.TILE_SIZE
            if pygame.time.get_ticks() - move_start_time > 10:
                if dx > player.x:
                    player.x += speed
                elif dx < player.x:
                    player.x -= speed
                elif dy > player.y:
                    player.y += speed
                elif dy < player.y:
                    player.y -= speed
                if player.x == dx and player.y == dy:
                    if dungeon.tiles[next_tile] == constants.DOOR:
                        if rend_mode == constants.TOP_DOWN:
                            sounds[constants.OPEN_DOOR].play()
                            dungeon.open_door(next_tile)
                            dungeon.in_room = not dungeon.in_room
                            changed_rooms = True
                        else:
                            illegal_move = True
                            game_state = prev_game_state
                            prev_game_state = constants.MOVING_STATE
                    if not illegal_move:
                        dungeon.player_tile = next_tile
                        has_moved = True
                        move_step_count += 1
                move_start_time = pygame.time.get_ticks()
        else:
            game_state = prev_game_state
            prev_game_state = constants.MOVING_STATE
            shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, 32, dungeon)
            if changed_rooms:
                changed_rooms = False
                if dungeon.in_room:
                    dungeon.current_room = dungeon.get_current_room()
                else:
                    dungeon.current_room = None


    ########################################################
                        # COMBAT STATE #
    ########################################################

    # COMBAT WILL ALTERNATE BETWEEN COMBAT STATE AND MENU STATE.
    # YOU SELECT A MENU OPTION ON YOUR TURN AND THEN IT WILL PERFORM THE ACTION
    # IF YOU SELECT TO MOVE ON YOUR TURN, IT WILL LET YOU CHOOSE A TILE TO MOVE TO
    # AND THEN IT WILL SWITCH TO MOVE STATE TO MOVE YOU, THEN RETURN HERE.
    
    elif game_state == constants.COMBAT_STATE:

        # FOR LATER USE TO HIGHLIGHT THE TILE BEING HOVERED OVER IN COMBAT
        #hover_pos = pygame.mouse.get_pos()
        #hover_tile = renderer.highlight_iso_tile(hover_pos, dungeon, images[constants.ENEMY])

        # PROCESS COMBAT INPUT
        for e in pygame.event.get():

            # DEBUG - Remove these once combat/menus are done
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_m:
                    rend_mode = constants.TOP_DOWN
                    game_state = constants.EXPLORATION_STATE

            # MOUSE CLICK INPUT HANDLING
            # RIGHT NOW THIS IS JUST FOR MOVEMENT
            # NEED TO MODIFY TO PROCESS MENU CLICK INPUT IF MENU BUTTON IS CLICKED
            # OR MOVEMENT IF A GRID TILE IS CLICKED
            # IDEA: YOU HAVE TO CLICK 'MOVE' BUTTON ON TURN AND THEN IT LETS YOU
            # CLICK ON A TILE TO MOVE TO
            if e.type == pygame.MOUSEBUTTONDOWN:
                click_pos = (int(e.pos[0]), int(e.pos[1]))
                dest_row, dest_col = renderer.get_iso_tile(click_pos, dungeon)
                move_dest = dest_row * dungeon_cols + dest_col
                has_moved = True
                cur_room = dungeon.get_current_room()
                if dungeon.tiles[move_dest] == constants.FLOOR:
                    move_path = move(dest_row * dungeon_cols + dest_col, dungeon, game_state, renderer)
                    if move_path:
                        move_step_count = 0
                        game_state = constants.MOVING_STATE
                        prev_game_state = constants.COMBAT_STATE
                        move_start_time = pygame.time.get_ticks()
        
        ####################################
        # COMBAT LOGIC FOR EACH FRAME HERE #
        ####################################


    ########################################################
                        # MENU STATE #
    ########################################################
    # WHEN WE COMBINE MENU CODE WITH THE MAIN FILE IT WILL GO HERE.
    elif game_state == constants.MENU_STATE:
        pass

    pygame.display.flip()
    game_time = clock.tick(60)