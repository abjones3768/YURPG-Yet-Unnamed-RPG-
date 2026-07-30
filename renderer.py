import pygame
import constants

"""
TODO:
- Finish isometric mode
- For occlusion, make it so if actor sprite collides with a wall or door, or if you hover mouse over one,
  it calls recursive function that makes all it and all its neighbors become partially transparent
"""

def convert_to_iso(x, y):
    return [x*constants.iso_matrix[0][0] + y*constants.iso_matrix[0][1],
            x*constants.iso_matrix[1][0] + y*constants.iso_matrix[1][1]]

def renderTilemap(cam, mode, sprites, dungeon, p, sc, is_combat, moved_status, viewport_w, viewport_h, tile_size, surface, mouse_position):
    width = dungeon.map_width
    map = dungeon.tiles
    px = p[0]
    py = p[1]
    vp_start_col = cam[0] // tile_size
    vp_start_row = cam[1] // tile_size
    vp_end_col = min(width, vp_start_col + viewport_w + 1)
    vp_end_row = min(dungeon.map_height, vp_start_row + viewport_h + 1)
    x_offset = (vp_start_col * tile_size) - cam[0]
    y_offset = (vp_start_row * tile_size) - cam[1]
    px -= (vp_start_col * tile_size)
    py -= (vp_start_row * tile_size)

    # TOP DOWN MODE
    if mode == constants.TOP_DOWN:
        # Only run shadowcaster if player has moved
        if moved_status:
            sc.fov(p[0]//tile_size, p[1]//tile_size, 48, dungeon)

        # Convert each tile from world space to viewport space and draw to screen
        for row in range(vp_start_row, vp_end_row):
            for col in range(vp_start_col, vp_end_col):
                i = row * width + col
                x = (col * tile_size) - (vp_start_col * tile_size)
                y = (row * tile_size) - (vp_start_row * tile_size)
                if sc.tile_visibility[i]:
                    color = constants.tile_colors[map[i]]
                else:
                    color = constants.tile_colors[constants.SHADOW]
                pygame.draw.rect(surface, color, pygame.Rect(x + x_offset, y + y_offset, tile_size, tile_size))
        pygame.draw.rect(surface, constants.tile_colors[constants.PLAYER], pygame.Rect(px + x_offset, py + y_offset, tile_size, tile_size))
    
    # ISOMETRIC MODE
    else:
        if is_combat or moved_status:
            is_combat = not is_combat

            # max battle grid size: 60x40, centered around player within bounds
            room = dungeon.get_current_room()
            battle_grid = pygame.Surface((viewport_w*tile_size, viewport_h*tile_size))
            left  = max(room.x1, p[0]//constants.TILE_SIZE - 30)
            right = min(room.x2, p[0]//constants.TILE_SIZE + 30)
            top   = max(room.y1, p[1]//constants.TILE_SIZE - 20)
            bot   = min(room.y2, p[1]//constants.TILE_SIZE + 20)

        
            # calculate projection offsets and player position
            vp_center = [((viewport_w-1) * constants.TILE_SIZE) //2, ((viewport_h-1) * constants.TILE_SIZE) //2]
            grid_center = convert_to_iso(((left+right)//2 * tile_size*2) - (room.x1 * tile_size*2), ((top+bot)//2 * tile_size*2) - (room.y1 * tile_size*2))
            px = p[0]*2 - (room.x1 * tile_size*2)
            py = p[1]*2 - (room.y1 * tile_size*2)
            player_pos = convert_to_iso(px-tile_size*6, py-tile_size*6)
            player_pos[0] += (vp_center[0]-grid_center[0])
            player_pos[1] += (vp_center[1]-grid_center[1])

            for row in range(room.y1, room.y2):
                for col in range(room.x1, room.x2):
                    # Transform all tiles within the battle zone into isometric coordinates
                    # and then offset them to the center of the viewport                
                    if left <= col <= right and top <= row <= bot:
                        i = row * width + col
                        x = (col * tile_size*2) - (room.x1 * tile_size*2)
                        y = (row * tile_size*2) - (room.y1 * tile_size*2)
                        pos = convert_to_iso(x, y)
                        pos[0] += (vp_center[0]-grid_center[0])
                        pos[1] += (vp_center[1]-grid_center[1]) - constants.TILE_SIZE*2
                        if map[i] == constants.FLOOR:
                            battle_grid.blit(sprites[map[i]].image, pos)
                        elif map[i] == constants.WATER:
                            pos[1] += tile_size*2//2
                            battle_grid.blit(sprites[map[i]].image, pos)
                        elif map[i] == constants.WALL or map[i] == constants.DOOR:
                            battle_grid.blit(sprites[map[i]].image, pos)
                            for j in range(0, 3):
                                pos[1] -= tile_size*2//2
                                battle_grid.blit(sprites[map[i]].image, pos)
            battle_grid.blit(sprites[constants.PLAYER].image, (player_pos))
            surface.blit(battle_grid, (0, 0))
    return (x_offset, y_offset)