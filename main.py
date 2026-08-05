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
from combatLogic import *
from combatDefines import *

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
        pygame.image.load("Resources/Images/CUBE_ROGUE.png").convert_alpha(),
        pygame.image.load("Resources/Images/CUBE_MAGE.png").convert_alpha(),
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
        pygame.mixer.Sound("Resources/SFX/GOBLIN_AGGRO.mp3"),
        pygame.mixer.Sound("Resources/SFX/EXIT_UNLOCKED.mp3"),
        #pygame.mixer.Sound("Resources/SFX/KEY_FOUND.mp3")
    ]
    sfx[constants.OPEN_DOOR].set_volume(0.5)
    music = [
        "Resources/Music/MENU_THEME.wav",
        "Resources/Music/COMBAT_THEME.wav"
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
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SRCALPHA)         # main graphics surface
viewport_cols = screen_width // constants.TILE_SIZE                     # screen width in tile space
viewport_rows = screen_height // constants.TILE_SIZE                    # screen height in tile space
dungeon_cols = viewport_cols * 10                                       # dungeon width in tile space
dungeon_rows = viewport_rows * 10                                       # dungeon height in tile space
clock = pygame.time.Clock()
images = load_images()
sounds, music = load_audio()
rend_mode = constants.TOP_DOWN
game_time = 0                                                           # Global game time
move_start_time = 0                                                     # Stores time when movement is started
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

# Combat init and junk
battleTimer = {}                                                        # Dict of integers that uses actor pointers as an index
turn_loop = True                                                        # Tracks beginning of battle loop
actor_turn = None                                                          # Pointer to current actor that has turn
turns = None
ended_moving = False

pygame.mixer.music.load(music[constants.MENU_THEME])
pygame.mixer.music.set_volume(0.5)
menu = Menu(screen_width, screen_height, game_state, screen, sounds, pygame.mixer.music)
main_background = Vortex(screen_width, screen_height, 600, screen)
dungeon = None
player = None
shadowcaster = None
renderer = None
battle_grid = None
aggro_enemies = []
enemies_aggroed = False
cur_combat_actor = 0
game_over = False

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
        job = menu.get_player_job()
        player = Player(dungeon.player_tile%dungeon_cols*constants.TILE_SIZE, dungeon.player_tile//dungeon_cols*constants.TILE_SIZE, dungeon.player_tile, "TEST", job)
        dungeon.fill_rooms(player)
        shadowcaster = Shadowcaster(dungeon_cols, dungeon_rows)
        shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, dungeon, player, game_state, battle_grid, aggro_enemies)
        renderer = Renderer(viewport_cols, viewport_rows)
        battle_grid = BattleGrid(viewport_cols*constants.TILE_SIZE, viewport_rows*constants.TILE_SIZE)
        game_state = constants.EXPLORATION_STATE
        prev_game_state = constants.RESETTING
        menu.menu_state = constants.IN_GAME
        rend_mode = constants.TOP_DOWN
        start_combat = False
        has_moved = False
        enemies_aggroed = False
        combat_started = False
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
        #############################################################
                            # EXPLORATION STATE #
        #############################################################
        if game_state == constants.EXPLORATION_STATE:

            # Condense this and combine code common with MOVING_STATE into function
            if len(aggro_enemies) > 0:
                if not enemies_aggroed:
                    sounds[constants.GOBLIN_AGGRO].play()
                    enemies_aggroed = True
                    enemy_move_start = pygame.time.get_ticks()
                    battle_grid.actors.extend(aggro_enemies)
                else:
                    if pygame.time.get_ticks() - enemy_move_start > 200:
                        for enemy in aggro_enemies:
                            if enemy.move_step < len(enemy.path_to_player) - 10:
                                next_tile = enemy.path_to_player[enemy.move_step]
                                if enemy.move_step == 0 or dungeon.tiles[next_tile] != constants.ENEMY:
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
                                        del dungeon.enemies[enemy.prev_tile]
                                        dungeon.enemies[enemy.cur_tile] = enemy
                                        dungeon.tiles[enemy.prev_tile] = constants.FLOOR
                                        dungeon.tiles[enemy.cur_tile] = constants.ENEMY
                                        enemy.move_step += 1
                                elif enemy.move_step == len(enemy.path_to_player) - 11:
                                    enemy.path_to_player = enemy.move(player.cur_tile, dungeon, game_state, battle_grid)
                                    enemy.move_step = 0
                            else:
                                aggro_enemies.pop(aggro_enemies.index(enemy))
                                if len(aggro_enemies) == 0:
                                    battle_grid.actors.append(player)
                                    rend_mode = constants.ISOMETRIC
                                    start_combat = True
                                    game_state = constants.COMBAT_STATE
                                    prev_game_state = constants.EXPLORATION_STATE
                                    enemies_aggroed = False
                                    pygame.mixer.music.load(music[constants.COMBAT_THEME])
                                    pygame.mixer.music.set_volume(0.3)
                                    pygame.mixer.music.play(-1)

            # TOP-DOWN KEY-PRESS CONTROLS
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:

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

                # EXPLORATION MOUSE CLICK HANDLERS
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
                            player.inventory.append(dungeon.current_room.chests[move_dest])
                            sounds[constants.ITEM_FOUND].play()
                            dungeon.tiles[move_dest] = constants.FLOOR
                            del dungeon.current_room.chests[move_dest]
                    elif dest_tile_val == constants.ENEMY_CORPSE:
                        dist = abs(player.cur_tile - move_dest)
                        if dist == 1 or dist == dungeon_cols:
                            if random.random() > 0.5:
                                sounds[constants.ITEM_FOUND].play()
                                enemy = dungeon.enemies[move_dest]
                                for item in enemy.inventory:
                                    player.inventory.append(item)
                            else:
                                sounds[constants.ILLEGAL_MOVE].play()
                            del dungeon.enemies[move_dest]
                            dungeon.tiles[move_dest] = constants.FLOOR
                    elif dest_tile_val == constants.LOCKED_DOOR:
                        dist = abs(player.cur_tile - move_dest)
                        if dist == 1 or dist == dungeon_cols:
                            if constants.KEY in player.inventory:
                                sounds[constants.EXIT_UNLOCKED].play()
                                dungeon.open_door(move_dest, constants.LOCKED_DOOR, constants.EXIT)
                            else:
                                sounds[constants.ILLEGAL_MOVE].play()
                    elif dest_tile_val == constants.EXIT:
                        pass
                        # Level complete

        ########################################################
                            # MOVING STATE #
        ########################################################

        # MOVE ACTOR ALONG PATH TO DESTINATION TILE AT INCREMENT OF 'SPEED'
        # PER FRAME UNTIL EITHER DESTINATION IS REACHED OR PATH IS CUT SHORT
        # DUE TO ILLEGAL MOVE OR HITTING MAX MOVEMENT RANGE.

        elif game_state == constants.MOVING_STATE:
            if len(aggro_enemies) > 0:
                game_state = constants.EXPLORATION_STATE
                prev_game_state = constants.MOVING_STATE
            else:
                illegal_move = False
                if move_step_count < len(move_path) and (mvmt_actor is player or move_step_count <= mvmt_actor.movementRange):
                    next_tile = move_path[move_step_count]
                    dx = (next_tile%dungeon_cols)*constants.TILE_SIZE
                    dy = (next_tile//dungeon_cols)*constants.TILE_SIZE
                    if pygame.time.get_ticks() - move_start_time > 10:
                        if dx > mvmt_actor.x:
                            mvmt_actor.x += speed
                        elif dx < mvmt_actor.x:
                            mvmt_actor.x -= speed
                        elif dy > mvmt_actor.y:
                            mvmt_actor.y += speed
                        elif dy < mvmt_actor.y:
                            mvmt_actor.y -= speed
                        if mvmt_actor.x == dx and mvmt_actor.y == dy:
                            if mvmt_actor is player:
                                mvmt_actor.prev_tile = mvmt_actor.cur_tile
                                mvmt_actor.cur_tile = next_tile
                                if dungeon.tiles[next_tile] == constants.DOOR:
                                    if rend_mode == constants.TOP_DOWN:
                                        sounds[constants.OPEN_DOOR].play()
                                        dungeon.open_door(next_tile, constants.DOOR, constants.FLOOR)
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
                                del dungeon.enemies[mvmt_actor.cur_tile]
                                mvmt_actor.prev_tile = mvmt_actor.cur_tile
                                mvmt_actor.cur_tile = next_tile
                                dungeon.enemies[mvmt_actor.cur_tile] = mvmt_actor
                                move_step_count += 1
                                has_moved = True
                                dungeon.tiles[mvmt_actor.prev_tile] = constants.FLOOR
                                dungeon.tiles[mvmt_actor.cur_tile] = constants.ENEMY
                        move_start_time = pygame.time.get_ticks()
                else:
                    game_state = prev_game_state
                    prev_game_state = constants.MOVING_STATE
                    if mvmt_actor is player:
                        if changed_rooms:
                            changed_rooms = False
                            if dungeon.in_room:
                                dungeon.current_room = dungeon.get_current_room(player)
                            else:
                                dungeon.current_room = None


        ########################################################
                            # COMBAT STATE #
        ########################################################
        
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

                # COMBAT MOUSE CLICK HANDLING
                # NEED TO ADD LOGIC FOR CLICKING MENU BUTTONS
                if e.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = (int(e.pos[0]), int(e.pos[1]))
                    dest_row, dest_col = renderer.get_iso_tile(player, click_pos, dungeon)
                    move_dest = dest_row * dungeon_cols + dest_col
                    has_moved = True

                    if dungeon.tiles[move_dest] == constants.FLOOR:
                        mvmt_actor = player
                        move_path = mvmt_actor.move(dest_row * dungeon_cols + dest_col, dungeon, game_state, battle_grid)
                        if move_path and mvmt_actor.movementRange >= len(move_path)-1:
                            move_step_count = 0
                            game_state = constants.MOVING_STATE
                            prev_game_state = constants.COMBAT_STATE
                            move_start_time = pygame.time.get_ticks()
                        else:
                            sounds[constants.ILLEGAL_MOVE].play()
                            
            # TURN-BASED COMBAT LOGIC
            if game_state == constants.MOVING_STATE:
                print("moving")
                ended_moving = True
            else:
                if ended_moving:
                    turn_loop = True
                    ended_moving = False
                if not turns and turn_loop: # Get list of turns
                    turns = battleGetTurns(battle_grid.actors, battleTimer)
                    alreadyMoved = False
                if turns and turn_loop: # Retrieve first turn in list
                    actor_turn = turns.pop(0)
                    turn_loop = False
                if not isinstance(actor_turn, Player): # If actor is not player (is enemy)
                    # If enemy is 1 tile away from player, attack. Else, move.
                    dist = abs(actor_turn.cur_tile - player.cur_tile)
                    if dist == 1 or dist == dungeon_cols:
                        attack = random.choice(actor_turn.attackList)
                        damage = attack(actor_turn, player)                        
                        print(f"{actor_turn.name} dealt {damage} damage to {player.name}!")
                        if player.health < 1:
                            print(f"{player.name} defeated!") 
                            battleTimer.pop(player)
                            
                            # GAME OVER - play sound effect, wait a few seconds, and then go to main menu
                            if not game_over:
                                sounds[constants.GAME_OVER].play()
                                game_over_start = pygame.time.get_ticks()
                                game_over = True

                        turn_loop = True
                    else:
                        move_path = actor_turn.move(player.cur_tile, dungeon, game_state, battle_grid)
                        if move_path:
                            move_path.pop(-1)
                            mvmt_actor = actor_turn
                            move_step_count = 0
                            game_state = constants.MOVING_STATE
                            prev_game_state = constants.COMBAT_STATE
                            move_start_time = pygame.time.get_ticks()
                        if dist == 1 or dist == dungeon_cols: 
                            pass 
                        else:
                            turn_loop = True
                else:
                    action = 0
                    while action < 1 or action > 5:
                        action = int(input(f"Choose an option for {actor_turn.name}.\n1. Move\n2. Attack\n3. Magic\n4. Items\n5. Wait\n"))
                    if action == MOVE:
                        if alreadyMoved:
                            print("Already moved.")
                        else:
                            input("player move (hit enter after clicking)")
                            turn_loop = True
                    if action == ATTACK:
                        attack = ""
                        while attack not in {'U', 'D', 'L', 'R'}:
                            print("Choose a direction to attack (U/D/L/R)")
                            attack = input()
                            attack.strip()
                        if attack == 'U': target_tile = actor_turn.cur_tile - dungeon_cols
                        if attack == 'D': target_tile = actor_turn.cur_tile + dungeon_cols
                        if attack == 'L': target_tile = actor_turn.cur_tile - 1
                        if attack == 'R': target_tile = actor_turn.cur_tile + 1
                        target = None
                        for actor in battle_grid.actors:
                            if target_tile == actor.cur_tile:
                                target = actor
                        if isinstance(target, Actor): # If attack is targeting a square with an actor
                            damage = playerAttack(actor_turn, target)
                            sounds[constants.MELEE_ATTACK].play()                        
                            print(f"{actor_turn.name} dealt {damage} damage to {target.name}!")
                            if target.health < 1:
                                print(f"{target.name} defeated!")
                                sounds[constants.GOBLIN_AGGRO].play()
                                has_moved = True
                                if actor_turn is player:
                                    actor_turn.gainExp(target.level)
                                battleTimer.pop(target)
                                battle_grid.actors.pop(battle_grid.actors.index(target))
                                dungeon.tiles[target.cur_tile] = constants.ENEMY_CORPSE
                        else:
                            print("Miss!")
                    if action == MAGIC:
                        print("Magic: ")
                        magicNum = len(actor_turn.magicAttacks)
                        for i in range(len(actor_turn.magicAttacks)):
                            print(f"{i + 1}. {actor_turn.magicAttacks[i]}")
                        choice = int(input("Choose a spell."))
                        while choice > magicNum or choice < 1:
                            choice = int(input("Choose a spell."))
                        attack = ""
                        while attack not in {'U', 'D', 'L', 'R'}:
                            print("Choose a direction to attack (U/D/L/R)")
                            attack = input()
                            attack.strip()
                        if attack == 'U': target_tile = actor_turn.cur_tile - dungeon_cols
                        if attack == 'D': target_tile = actor_turn.cur_tile + dungeon_cols
                        if attack == 'L': target_tile = actor_turn.cur_tile - 1
                        if attack == 'R': target_tile = actor_turn.cur_tile + 1
                        target = None
                        for actor in battle_grid.actors:
                            if target_tile == actor.cur_tile:
                                target = actor
                        sounds[constants.MAGIC].play()
                        damage = actor_turn.magicAttacks[choice - 1](actor_turn, target)
                        print(f"{actor_turn.name} dealt {damage} damage to {target.name}!")
                        if actor.health < 1:
                            has_moved = True
                            sounds[constants.GOBLIN_AGGRO].play()
                            print(f"{target.name} defeated!") 
                            actor.gainExp(target.level)
                            battleTimer.pop(target)
                            battle_grid.actors.pop(battle_grid.actors.index(target))
                            dungeon.tiles[target.cur_tile] = constants.ENEMY_CORPSE
                    if action == ITEMS:
                        print("Items: ")
                        itemNum = len(actor_turn.inventory)
                        for i in range(itemNum):
                            print(f"{i + 1}. {actor_turn.inventory[i]}. ", end="")
                            if actor_turn.items[actor_turn.inventory[i]] == 0:
                                print("None available.", end="")
                            print("")
                        choice = int(input("Choose an item."))
                        while choice > itemNum or choice < 1 or actor_turn.items[actor_turn.inventory[choice - 1]] == 0:
                            choice = int(input("Choose an item."))
                        itemDict[actor_turn.inventory[choice - 1]].usageFunction(actor_turn)
                        print(f"{actor_turn.name} used {itemDict[actor_turn.inventory[choice - 1]].name}. {itemDict[actor_turn.inventory[choice - 1]].usageMessage}")
                        actor_turn.items[actor_turn.inventory[choice - 1]] -= 1
    
                    if action == WAIT:
                        pass
                    turn_loop = True
                if len(battle_grid.actors) == 1 and battle_grid.actors[0] is player:
                    battleTimer.clear()
                    battle_grid.actors.clear()
                    game_state = constants.EXPLORATION_STATE
                    prev_game_state = constants.COMBAT_STATE
                    turns = False
                    turn_loop = False
                    rend_mode = constants.TOP_DOWN
                    sounds[constants.VICTORY].play()
                    pygame.mixer.music.stop()
                    shadowcaster.fov(player.x//constants.TILE_SIZE, player.y//constants.TILE_SIZE, dungeon, player, game_state, battle_grid, aggro_enemies)
                elif game_over:
                    if pygame.time.get_ticks() - game_over_start > 3000:
                        game_state = MENU_STATE
                        prev_game_state = None
                        menu.menu_state = MAIN_MENU

        # x,y offsets used for smooth movement of player/camera between tiles
        vp_pos, offsets = renderer.renderTilemap(screen_width, screen_height, rend_mode, images, dungeon, player, shadowcaster, start_combat, has_moved, viewport_cols, viewport_rows, constants.TILE_SIZE, screen, game_state, aggro_enemies, battle_grid)
    
        # Tells renderer to run shadowcaster if player moves in top down mode,
        # or to update the battle grid after actor movement if in combat
        if has_moved:
            has_moved = False

        # Triggers initial battle grid projection in renderer
        if start_combat:
            start_combat = False

    pygame.display.flip()
    game_time = clock.tick(60)
    run = menu.playing
pygame.quit()
sys.exit()