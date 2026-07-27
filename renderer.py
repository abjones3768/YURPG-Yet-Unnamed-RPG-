import pygame

"""
TODO:
- Create isometric rendering mode for combat that draws only the current room scaled up to the viewport
"""
tile_types = {
    -1: (36, 31, 49),
    0 : (125, 120, 130),
    1 : (94, 92, 100),
    2 : (125, 88, 55),
    3 : (0, 102, 255)
}

background = 

def renderTilemap(dungeon, p, rc, viewport_w, viewport_h, tile_size, surface):
    # Condense this into 1 function to calculate viewport pos
    width = dungeon.map_width
    map = dungeon.tiles
    px = p[0]
    py = p[1]
    vp_x = max(0, px - viewport_w * tile_size // 2)
    vp_y = max(0, py - viewport_h * tile_size // 2)
    vp_start_col = vp_x // tile_size
    vp_start_row = vp_y // tile_size
    vp_end_col = min(width, vp_start_col + viewport_w + 1)
    vp_end_row = min(dungeon.map_height, vp_start_row + viewport_h + 1)
    x_offset = (vp_start_col * tile_size) - vp_x
    y_offset = (vp_start_row * tile_size) - vp_y
    px -= (vp_start_col * tile_size)
    py -= (vp_start_row * tile_size)

    # Convert each tile from world space to viewport space and draw to screen
    for row in range(vp_start_row, vp_end_row):
        for col in range(vp_start_col, vp_end_col):
            i = row * width + col
            x = (col * tile_size) - (vp_start_col * tile_size)
            y = (row * tile_size) - (vp_start_row * tile_size)
            color = tile_types[map[i]]
            pygame.draw.rect(surface, color, pygame.Rect(x + x_offset, y + y_offset, tile_size, tile_size))
    pygame.draw.rect(surface, (0, 20, 255), pygame.Rect(px + x_offset, py + y_offset, tile_size, tile_size))
    return vp_start_row * width + vp_start_col