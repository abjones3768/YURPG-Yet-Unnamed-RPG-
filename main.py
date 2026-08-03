import pygame
import sys
import constants
from vortex import Vortex
from menus import Menu
from dungeon import Dungeon
from renderer import Renderer
from battle_grid import BattleGrid
from shadowcaster import Shadowcaster
from combatActors import *

# This script launches the game.

"""
TODO:
- Make hovering over battle grid tile color it with partially transparent red cube
- Make hovering over battle grid obstacles call recursive function that makes all tiles
  in the obstacle partially transparent (same if an actor is blocked by one)
- Make function to spawn chests and loot in chests by level/rarity,
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
#                                               #
# M to toggle between top down and isometric    #
# Click on floor/door tiles to move to them     #
# Q to quit                                     #
#################################################


# Move this to actor class
# Accepts clicked tile as input and outputs path to it
# import dungeon and renderer in combatActors

# Load sprites used for isometric rendering and scale them up to 32x32
# Use sprite.image for drawing and sprite.rect for collision detection in isometric mode
def load_images():
    images = [
        pygame.image.load("Resources/Images/CUBE_FLOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WALL.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_DOOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WATER.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_CHEST.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_WARRIOR.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_ENEMY.png").convert_alpha(),
    ]
    for i, img in enumerate(images):
        images[i] = pygame.transform.scale(img, (constants.TILE_SIZE * 2, constants.TILE_SIZE * 2))
    return images

# Load audio
def load_audio():
    sfx = [
        pygame.mixer.Sound("Resources/SFX/GAME_OVER.mp3"),
        pygame.mixer.Sound("Resources/SFX/LEVEL_UP.mp3"),
        pygame.mixer.Sound("Resources/SFX/MELEE_ATTACK.mp3"),
        pygame.mixer.Sound("Resources/SFX/OPEN_DOOR.mp3"),
        pygame.mixer.Sound("Resources/SFX/VICTORY.mp3"),
        pygame.mixer.Sound("Resources/SFX/BUTTON_CLICK.mp3"),
        pygame.mixer.Sound("Resources/SFX/ILLEGAL_MOVE.mp3"),
        pygame.mixer.Sound("Resources/SFX/ITEM_FOUND.mp3"),
        pygame.mixer.Sound("Resources/SFX/MAGIC.mp3"),
    ]
    music = [
        "Resources/Music/MENU_THEME.wav"
    ]
    return sfx, music


# Initialization
pygame.init()
pygame.mixer.init()
game_state = constants.MENU_STATE
prev_game_state = None
info = pygame.display.Info()
screen_width = info.current_w                                           # get user screen width
screen_height = info.current_h                                          # get user screen height
screen = pygame.display.set_mode((screen_width, screen_height))         # main graphics surface
viewport_cols = screen_width // constants.TILE_SIZE                     # screen width in tile space
viewport_rows = screen_height // constants.TILE_SIZE                    # screen height in tile space
dungeon_cols = viewport_cols * 10                                       # dungeon width in tile space
dungeon_rows = viewport_rows * 10                                       # dungeon height in tile space
clock = pygame.time.Clock()
images = load_images()
sounds, music = load_audio()
rend_mode = constants.TOP_DOWN
combat_check_timer = 0                                                  # Keeps time between enemy detection checks
game_time = 0                                                           # Global game time
move_start_time = 0                                                     # Stores time when movement is started
move_elapsed_time = 0                                                   # Tracks time between movements along path
move_path_nodes = None                                                  # Used for pathfinding to build path
move_path = None                                                        # List of tiles along path from A to B
move_step_count = 0                                                     # Used to track movement along path
move_dest = None                                                        # Stores clicked tile to move to
has_moved = False                                                       # Signals renderer to redraw isometric battle grid after movement
speed = 4                                                               # Movement px per frame
start_combat = False                                                    # Signals renderer to construct new isometric grid for combat
illegal_move = False                                                    # Signals out-of-bounds move during combat
changed_rooms = False                                                   # Signals that player has changed rooms in the dungeon
mvmt_actor = None
menu_event = None
menu_key = None

pygame.mixer.music.load(music[constants.MENU_THEME])
menu = Menu(screen_width, screen_height, game_state, screen, sounds, pygame.mixer.music)
main_background = Vortex(screen_width, screen_height, 600, screen)
dungeon = None
player = None
shadowcaster = None
renderer = None
battle_grid = None
aggro_enemies = []
enemies_aggroed = False

# Game loop
run = True
while run:

    ########################################################
                        # MENU STATE #
    ########################################################
    if game_state == constants.RESETTING:
        dungeon = Dungeon(constants.TILE_SIZE, 1, 1, dungeon_cols, dungeon_rows, 64, 20)
        dungeon.generateDungeon()
        game_state = constants.EXPLORATION_STATE
        player = Player(dungeon.player_tile%dungeon_cols*constants.TILE_SIZE, dungeon.player_tile//dungeon_cols*constants.TILE_SIZE, dungeon.player_tile, "TEST", 2)
        shadowcaster = Shadowcaster(dungeon_cols, dungeon_rows)
        shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, 32, dungeon, player, game_state, battle_grid, aggro_enemies)
        renderer = Renderer(viewport_cols, viewport_rows)
        battle_grid = BattleGrid(viewport_cols*constants.TILE_SIZE, viewport_rows*constants.TILE_SIZE)
        game_state = constants.EXPLORATION_STATE
        prev_game_state = constants.RESETTING
        menu.menu_state = constants.IN_GAME
        rend_mode = constants.TOP_DOWN
        start_combat = False
        has_moved = False
        aggro_enemies.clear()
        continue
    
    # On each frame, clear and redraw the screen
    screen.fill((0, 0, 0))

    if game_state == constants.MENU_STATE:
        if menu.menu_state != constants.IN_GAME and menu.menu_state != constants.COMBAT_MENU:
            main_background.play_vortex(screen_width, screen_height, screen)
        menu.display_menu()
        if menu.menu_state == constants.NEW_GAME:
            game_state = constants.RESETTING
            prev_game_state = constants.MENU_STATE
            continue
        elif menu.menu_state == constants.IN_GAME:
            game_state = prev_game_state
            prev_game_state = constants.MENU_STATE

    else:
        # x,y offsets used for smooth movement of player/camera between tiles
        vp_pos, offsets = renderer.renderTilemap(screen_width, screen_height, rend_mode, images, dungeon, player, shadowcaster, start_combat, has_moved, viewport_cols, viewport_rows, constants.TILE_SIZE, screen, game_state, aggro_enemies, battle_grid)
    
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
            if len(aggro_enemies) > 0:
                battle_grid.enemies.extend(aggro_enemies)
                enemies_ready = 0
                if not enemies_aggroed:
                    enemies_aggroed = True  # set this to false after combat triggered
                    enemy_move_start = pygame.time.get_ticks()
                else:
                    if pygame.time.get_ticks() - enemy_move_start > 10:
                        for enemy in aggro_enemies:
                            next_tile = enemy.path_to_player[enemy.move_step]
                            x_dist = abs(player.x - enemy.x)
                            y_dist = abs(player.y - enemy.y)
                            if enemy.move_step < len(enemy.path_to_player) - 8:
                                next_tile = enemy.path_to_player[enemy.move_step]
                                dx = (next_tile%dungeon_cols)*constants.TILE_SIZE
                                dy = (next_tile//dungeon_cols)*constants.TILE_SIZE
                                if dx > enemy.x:
                                    enemy.x += speed
                                elif dx < enemy.x:
                                    enemy.x -= speed
                                elif dy > enemy.y:
                                    enemy.y += speed
                                elif dy < enemy.y:
                                    enemy.y -= speed
                                if enemy.x == dx and enemy.y == dy:
                                    enemy.prev_tile = enemy.cur_tile
                                    enemy.cur_tile = next_tile
                                    dungeon.tiles[enemy.prev_tile] = constants.FLOOR
                                    dungeon.tiles[enemy.cur_tile] = constants.ENEMY
                                    enemy.move_step += 1
                            else:
                                enemies_ready += 1
                                if enemies_ready == len(aggro_enemies):
                                    rend_mode = constants.ISOMETRIC
                                    start_combat = True
                                    game_state = constants.COMBAT_STATE
                                    prev_game_state = constants.EXPLORATION_STATE
                                    break


            # TOP-DOWN CONTROLS
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:

                    # TEST - REMOVE ONCE COMBAT IS IMPLEMENTED
                    #if e.key == pygame.K_m:
                        #rend_mode = constants.ISOMETRIC
                        #start_combat = True
                        #game_state = constants.COMBAT_STATE

                    # To bring up menus from overworld
                    if e.key == pygame.K_ESCAPE:
                        menu.menu_state = constants.OPTIONS_MENU
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.EXPLORATION_STATE
                    elif e.key == pygame.K_i:
                        menu.menu_state = constants.INVENTORY
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.EXPLORATION_STATE
                    elif e.key == pygame.K_k:
                        menu.menu_state = constants.SKILL_MENU
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.EXPLORATION_STATE

                # EXPLORATION MOVEMENT
                if e.type == pygame.MOUSEBUTTONDOWN:
                    dest_col = (int(e.pos[0] - offsets[0]) // constants.TILE_SIZE) + vp_pos[0]
                    dest_row = (int(e.pos[1] - offsets[1]) // constants.TILE_SIZE) + vp_pos[1]
                    move_dest = dest_row * dungeon_cols + dest_col
                    dest_tile_val = dungeon.tiles[move_dest]
                    if dest_tile_val == constants.FLOOR or dest_tile_val == constants.DOOR:
                        move_path = player.move(dest_row * dungeon_cols + dest_col, dungeon, game_state, battle_grid)
                        if move_path:
                            mvmt_actor = player
                            move_step_count = 0
                            game_state = constants.MOVING_STATE
                            prev_game_state = constants.EXPLORATION_STATE
                            move_start_time = pygame.time.get_ticks()
                    elif dest_tile_val == constants.CHEST:
                        dist = abs(player.cur_tile - move_dest)
                        if dist == 1 or dist == dungeon_cols:
                            for item in dungeon.current_room.chests[move_dest]:
                                player.inventory.append(item)
                            sounds[constants.ITEM_FOUND].play()
                            dungeon.tiles[move_dest] = constants.FLOOR
                            del dungeon.current_room.chests[move_dest]

        ########################################################
                            # MOVING STATE #
        ########################################################

        # MOVE PLAYER ALONG PATH TO DESTINATION TILE AT INCREMENT OF 'SPEED'
        # PER FRAME UNTIL EITHER DESTINATION IS REACHED OR PATH IS CUT SHORT
        # DUE TO ILLEGAL MOVE.

        # NEED TO MODIFY TO DO A CHECK TO SEE IF len(move_path) IS LESS
        # THAN THE ACTOR'S MOVEMENT RANGE.

        # ALSO NEED TO MODIFY SO THAT IF CLICKED TILE IS A CHEST, IT STOPS
        # PLAYER AT TILE BEFORE IT AND OPENS THE CHEST.
        elif game_state == constants.MOVING_STATE:
            illegal_move = False
            if move_step_count < len(move_path) and (mvmt_actor is player or move_step_count <= mvmt_actor.movementRange):
                next_tile = move_path[move_step_count]
                dx = (next_tile%dungeon_cols)*constants.TILE_SIZE
                dy = (next_tile//dungeon_cols)*constants.TILE_SIZE
                if pygame.time.get_ticks() - move_start_time > 10:
                    is_destination = False
                    if dx > mvmt_actor.x:
                        mvmt_actor.x += speed
                    elif dx < mvmt_actor.x:
                        mvmt_actor.x -= speed
                    elif dy > mvmt_actor.y:
                        mvmt_actor.y += speed
                    elif dy < mvmt_actor.y:
                        mvmt_actor.y -= speed
                    if mvmt_actor.x == dx and mvmt_actor.y == dy:
                        mvmt_actor.prev_tile = mvmt_actor.cur_tile
                        mvmt_actor.cur_tile = next_tile
                        if mvmt_actor is player:
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
                                has_moved = True
                                move_step_count += 1
                        else:
                            move_step_count += 1
                    move_start_time = pygame.time.get_ticks()
            else:
                game_state = prev_game_state
                prev_game_state = constants.MOVING_STATE
                if mvmt_actor is player:
                    #shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, 32, dungeon, player, game_state, battle_grid, aggro_enemies)
                    if changed_rooms:
                        changed_rooms = False
                        if dungeon.in_room:
                            dungeon.current_room = dungeon.get_current_room(player)
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

                # To bring up menus from combat
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        menu.menu_state = constants.OPTIONS_MENU
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.COMBAT_STATE
                    elif e.key == pygame.K_i:
                        menu.menu_state = constants.INVENTORY
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.COMBAT_STATE
                    elif e.key == pygame.K_k:
                        menu.menu_state = constants.SKILL_MENU
                        game_state = constants.MENU_STATE
                        prev_game_state = constants.COMBAT_STATE
                    
                    #elif e.key == pygame.K_m:
                        #rend_mode = constants.TOP_DOWN
                        #game_state = constants.EXPLORATION_STATE

                # MOUSE CLICK INPUT HANDLING
                # RIGHT NOW THIS IS JUST FOR MOVEMENT
                # NEED TO MODIFY TO PROCESS MENU CLICK INPUT IF MENU BUTTON IS CLICKED
                # OR MOVEMENT IF A GRID TILE IS CLICKED
                # IDEA: YOU HAVE TO CLICK 'MOVE' BUTTON ON TURN AND THEN IT LETS YOU
                # CLICK ON A TILE TO MOVE TO
                if e.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = (int(e.pos[0]), int(e.pos[1]))
                    dest_row, dest_col = renderer.get_iso_tile(player, click_pos, dungeon)
                    move_dest = dest_row * dungeon_cols + dest_col
                    has_moved = True

                    if dungeon.tiles[move_dest] == constants.FLOOR:
                        move_path = player.move(dest_row * dungeon_cols + dest_col, dungeon, game_state, battle_grid)
                        if move_path and player.movementRange >= len(move_path)-1:
                            mvmt_actor = player
                            move_step_count = 0
                            game_state = constants.MOVING_STATE
                            prev_game_state = constants.COMBAT_STATE
                            move_start_time = pygame.time.get_ticks()
            
            ##############################################
            # PUT COMBAT LOGIC FOR EACH FRAME BELOW HERE #
            ##############################################
            #
            # battle_grid is a subset of tiles out of the greater dungeon.
            # Each time combat is started, it updates its actor list to
            # store all enemies currently in combat so they are easily accessible.
            #
            #       - access combat actors:   battle_grid.actors
            #
            # I also updated the Actor base class so that for any actor you can easily
            # get their position, tile_type and tile index in the dungeon.
            #
            #
            # MOVEMENT:
            #
            # Player movement is handled above in MOVEMENT state when a valid floor tile is clicked.
            #
            # For enemy's to follow the path to their target after calling their move function,
            # here is what we need to do:
            #
            #       - Since they are going to move towards the player until within attack range,
            #         call their move function with the player's tile as the destination.
            #         To access the current player tile:  dungeon.player_tile
            #
            #       - When an enemy chooses to move on their turn, call their move function:
            #               move_path = move(dungeon.player_tile, dungeon, game_state, battle_grid) and then
            #         
            #       - Then do this, same as for the player to initiate MOVEMENT state and start the timer:
            #            if move_path:
            #                mvmt_actor = actor
            #                move_step_count = 0
            #                game_state = constants.MOVING_STATE
            #                prev_game_state = constants.COMBAT_STATE
            #                move_start_time = pygame.time.get_ticks()
            #
            #       - This will initiate MOVING_STATE and the enemy will just move however many
            #         tiles their movementRange allows on the quickest path to the player.
            #               
            #       - There are 2 things we need to add:
            #
            #               1.  Currenly there is no visual cue for if you try to move to a tile
            #                   outside your mvmt range, but I'll add that.
            #
            #               2.  I still need to implement a check for the player that doesn't let you click
            #                   on a tile with 

    pygame.display.flip()
    game_time = clock.tick(60)
    if not menu.playing:
        pygame.quit()
        sys.exit() 