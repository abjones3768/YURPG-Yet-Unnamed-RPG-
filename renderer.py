import pygame
import constants
import math

"""
TODO:
- For occlusion, make it so if actor sprite collides with a wall or door, or if you hover mouse over one,
  it calls recursive function that makes all it and all its neighbors become partially transparent
"""

class Renderer:
    def __init__(self, viewport_w, viewport_h):
        self.iso_offset = []
        self.x_offset = 0
        self.y_offset = 0
        self.vp_pos = [0, 0]

    def get_iso_pos(self, room, row, col):
        x = (col * constants.TILE_SIZE*2) - (room.x1 * constants.TILE_SIZE*2)
        y = (row * constants.TILE_SIZE*2) - (room.y1 * constants.TILE_SIZE*2)
        pos = self.convert_to_iso(x, y)
        pos[0] += (self.iso_offset[0])
        pos[1] += (self.iso_offset[1]) - constants.TILE_SIZE*2
        return pos

    def get_iso_actor_pos(self, room, actor):
        px = actor.x*2 - (room.x1 * constants.TILE_SIZE*2)
        py = actor.y*2 - (room.y1 * constants.TILE_SIZE*2)
        pos = self.convert_to_iso(px-constants.TILE_SIZE*6, py-constants.TILE_SIZE*6)
        pos[0] += self.iso_offset[0]
        pos[1] += self.iso_offset[1]
        return pos

    def convert_to_iso(self, x, y):
        return [x*constants.iso_matrix[0][0] + y*constants.iso_matrix[0][1],
                x*constants.iso_matrix[1][0] + y*constants.iso_matrix[1][1]]

    def get_iso_tile(self, p, cursor_pos, dungeon):
        # Reverse viewport offset and apply inverse isometric matrix
        pos_x = cursor_pos[0] - self.iso_offset[0]
        pos_y = cursor_pos[1] - self.iso_offset[1] + constants.TILE_SIZE*2
        inverted_pos = [pos_x*constants.click_matrix[0][0] + pos_y*constants.click_matrix[0][1],
                        pos_x*constants.click_matrix[1][0] + pos_y*constants.click_matrix[1][1]]

        # Snap position to increments of 32 since iso tiles are x2 resolution
        # and then decrement by 1/2 tile to snap position to grid
        inverted_pos[0] = (math.floor(inverted_pos[0] / 32 + 0.5) * 32) - 16
        inverted_pos[1] = math.floor(inverted_pos[1] / 32 + 0.5) * 32

        # Convert to world tile
        cur_room = dungeon.get_current_room(p)
        col = int(inverted_pos[0] // (constants.TILE_SIZE * 2)) + cur_room.x1
        row = int(inverted_pos[1] // (constants.TILE_SIZE * 2)) + cur_room.y1
        return row, col

    # TEST
    def highlight_iso_tile(self, p, hover_pos, dungeon, highlight_sprite):
        row, col = self.get_iso_tile(p, hover_pos, dungeon)
        print(f"HIGHLIGHT: {col},{row} = {dungeon.tiles[row*dungeon.map_width+col]}")

    def renderTilemap(self, screen_w, screen_h, mode, images, dungeon, p, sc, is_combat, moved_status, viewport_w, viewport_h, tile_size, surface, state, aggro_enemies, battle_grid):
        tilemap = dungeon.tiles

        # TOP DOWN MODE
        if mode == constants.TOP_DOWN:
            cam_x = max(0, p.x-screen_w//2)
            cam_y = max(0, p.y-screen_h//2)
            self.vp_pos[0] = cam_x // tile_size
            self.vp_pos[1] = cam_y // tile_size
            vp_end_col = min(dungeon.map_width, self.vp_pos[0] + viewport_w + 1)
            vp_end_row = min(dungeon.map_height, self.vp_pos[1] + viewport_h + 1)
            px = p.x - (self.vp_pos[0] * tile_size)
            py = p.y - (self.vp_pos[1] * tile_size)
            self.x_offset = (self.vp_pos[0] * tile_size) - cam_x
            self.y_offset = (self.vp_pos[1] * tile_size) - cam_y

            # Only run shadowcaster if player has moved
            if moved_status:
                sc.fov(p.x//tile_size, p.y//tile_size, dungeon, p, state, battle_grid, aggro_enemies)

            # Convert each tile from world space to viewport space and draw to screen
            for row in range(self.vp_pos[1], vp_end_row):
                for col in range(self.vp_pos[0], vp_end_col):
                    i = row * dungeon.map_width + col
                    x = (col * tile_size) - (self.vp_pos[0] * tile_size)
                    y = (row * tile_size) - (self.vp_pos[1] * tile_size)
                    if sc.tile_visibility[i]:
                        if dungeon.tiles[i] != constants.ENEMY:
                            color = constants.tile_colors[tilemap[i]]
                    else:
                        color = constants.tile_colors[constants.SHADOW]
                    pygame.draw.rect(surface, color, pygame.Rect(x + self.x_offset, y + self.y_offset, tile_size, tile_size))
            for enemy in battle_grid.actors:
                en_x = enemy.x - (self.vp_pos[0] * tile_size)
                en_y = enemy.y - (self.vp_pos[1] * tile_size)
                pygame.draw.rect(surface, constants.tile_colors[constants.ENEMY], pygame.Rect(en_x + self.x_offset, en_y + self.y_offset, tile_size, tile_size))
            pygame.draw.rect(surface, constants.tile_colors[p.job], pygame.Rect(px + self.x_offset, py + self.y_offset, tile_size, tile_size))
    
        # ISOMETRIC MODE
        else:
            if is_combat:
                # max battle grid size: 60x40, centered around player within bounds
                room = dungeon.get_current_room(p)
                battle_grid.background.fill((0, 0, 0))
                battle_grid.foreground.fill((0, 0, 0, 0))
                self.iso_offset.clear()
                battle_grid.x1 = max(room.x1, p.x//constants.TILE_SIZE - 30)
                battle_grid.x2 = min(room.x2, p.x//constants.TILE_SIZE + 30)
                battle_grid.y1 = max(room.y1, p.y//constants.TILE_SIZE - 20)
                battle_grid.y2 = min(room.y2, p.y//constants.TILE_SIZE + 20)

                # Add all connected groups of wall/door tiles to sprite groups so they can
                # be made partially transparent when blocking an actor
                #for row in range(battle_grid.y1, battle_grid.y2):
                    #for col in range(battle_grid.x1, battle_grid.x2):
                        #i = row * dungeon.map_width + col
                        #if tilemap[i] == constants.WALL:
                            #battle_grid.obstacle_groups.append([])
                            #battle_grid.group_obstacles(tilemap, width, i, constants.WALL)
                        #elif tilemap[i] == constants.DOOR:
                            #battle_grid.obstacle_groups.append([])
                            #battle_grid.group_obstacles(tilemap, width, i, constants.DOOR)  

                # calculate projection offsets and player position
                vp_center = [((viewport_w-1) * constants.TILE_SIZE) //2, ((viewport_h-1) * constants.TILE_SIZE) //2]
                grid_center = self.convert_to_iso(((battle_grid.x1+battle_grid.x2)//2 * tile_size*2) - (room.x1 * tile_size*2), ((battle_grid.y1+battle_grid.y2)//2 * tile_size*2) - (room.y1 * tile_size*2))
                self.iso_offset.append(vp_center[0]-grid_center[0])
                self.iso_offset.append(vp_center[1]-grid_center[1])
                player_pos = self.get_iso_actor_pos(room, p)

                for row in range(battle_grid.y1, battle_grid.y2):
                    for col in range(battle_grid.x1, battle_grid.x2):             
                            i = row * dungeon.map_width + col
                            pos = self.get_iso_pos(room, row, col)
                            if tilemap[i] == constants.FLOOR or tilemap[i] == constants.CHEST or tilemap[i] == constants.ENEMY:
                                battle_grid.background.blit(images[constants.FLOOR], pos)
                            elif tilemap[i] == constants.WATER:
                                pos[1] += tile_size
                                battle_grid.background.blit(images[tilemap[i]], pos)
                            elif tilemap[i] == constants.WALL or tilemap[i] == constants.DOOR:
                                battle_grid.background.blit(images[tilemap[i]], pos)
                                for j in range(0, 3):
                                    pos[1] -= tile_size
                                    battle_grid.foreground.blit(images[tilemap[i]], pos)
                battle_grid.actors.sort(key=lambda actor: actor.cur_tile)
                for actor in battle_grid.actors:
                    if actor is p:
                        battle_grid.foreground.blit(images[p.job], (player_pos))
                    else:
                        battle_grid.foreground.blit(images[constants.ENEMY], self.get_iso_actor_pos(room, actor))
                surface.blit(battle_grid.background, (0, 0))
                surface.blit(battle_grid.foreground, (0, 0))
            elif moved_status:
                battle_grid.foreground.fill((0, 0, 0, 0))
                room = dungeon.get_current_room(p)
                render_actor_order = []

                # When drawing player after each move, check if the player sprite is
                # colliding with
                player_pos = self.get_iso_actor_pos(room, p)
                for row in range(battle_grid.y1, battle_grid.y2):
                    for col in range(battle_grid.x1, battle_grid.x2):
                            i = row * dungeon.map_width + col
                            pos = self.get_iso_pos(room, row, col)
                            pos[1] -= tile_size
                            if tilemap[i] == constants.WALL or tilemap[i] == constants.DOOR:
                                battle_grid.foreground.blit(images[tilemap[i]], pos)
                                for j in range(0, 2):
                                    pos[1] -= tile_size
                                    battle_grid.foreground.blit(images[tilemap[i]], pos)
                            pos[1] += tile_size
                battle_grid.actors.sort(key=lambda actor: actor.cur_tile)
                for actor in battle_grid.actors:
                    if actor is p:
                        battle_grid.foreground.blit(images[p.job], (player_pos))
                    else:
                        battle_grid.foreground.blit(images[constants.ENEMY], self.get_iso_actor_pos(room, actor))
                surface.blit(battle_grid.background, (0, 0))
                surface.blit(battle_grid.foreground, (0, 0))
            else:
                surface.blit(battle_grid.background, (0, 0))
                surface.blit(battle_grid.foreground, (0, 0))
        return self.vp_pos, (self.x_offset, self.y_offset)