import constants

# Class that implements recursive shadowcasting FOV algorithm and stores tile visibility data
class Shadowcaster:
    def __init__(self, width, height):
        # Stores each tile's visibility status
        self.tile_visibility = [0] * (width * height)
        
        # Multiplication matrix used to compute x,y offsets in each octant
        # around the player
        self.mult_matrix = (
            (1,  0,  0, -1, -1,  0,  0,  1),
            (0,  1, -1,  0,  0, -1,  1,  0),
            (0,  1,  1,  0,  0, -1, -1,  0),
            (1,  0,  0,  1, -1,  0,  0, -1)
        )

    # Check if a tile is blocked (either a wall or door tile)
    def blocked(self, dungeon, x, y):
        i = y * dungeon.map_width + x
        return dungeon.tiles[i] == constants.WALL or dungeon.tiles[i] == constants.DOOR

    # Recursive function that casts shadows behind blocked tiles by segmenting tiles
    # surrounding the player into octants and casting rays from the player to the
    # tiles in each octant to identify obstacles
    def cast_light(self, cx, cy, row, start, end, radius, dungeon, player, state, grid, xx, xy, yx, yy, aggro_enemies):
            if start < end:
                return
            radius_squared = radius*radius
            for j in range(row, radius+1):
                dx, dy = -j-1, -j
                blocked = False
                while dx <= 0:
                    dx += 1
                    # Translate the dx, dy coordinates into dungeon coordinates
                    X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy

                    # Get the slopes of the left and right
                    # corners of the current tile
                    l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)

                    if start < r_slope:
                        continue
                    elif end > l_slope:
                        break
                    else:

                        # Cast light on the current tile:
                        if dx*dx + dy*dy < radius_squared:
                            index = Y * dungeon.map_width + X
                            if self.tile_visibility[index] == 0:
                                self.tile_visibility[index] = 1
                                if dungeon.tiles[index] == constants.ENEMY:
                                    enemy = dungeon.enemies[index]
                                    aggro_enemies.append(enemy)
                                    enemy.path_to_player = enemy.move(player.cur_tile, dungeon, state, grid)
                                    enemy.move_step = 0
                        # If in blocked row, keep passing tiles until an unblocked tile is found.
                        # Then set the new starting slope as the slope to the right corner of the
                        # blank tile.
                        if blocked:
                            if self.blocked(dungeon, X, Y):
                                new_start = r_slope
                                continue
                            else:
                                blocked = False
                                start = new_start
                        # If not in a blocked row, check to see if the current tile is blocked.
                        # If it is, then make recursive call for the next row behind it.
                        else:
                            if self.blocked(dungeon, X, Y) and j < radius:
                                blocked = True
                                self.cast_light(cx, cy, j+1, start, l_slope,
                                                radius, dungeon, player, state, grid,
                                                xx, xy, yx, yy, aggro_enemies)
                                new_start = r_slope

                # Row is scanned; do next row unless last square was blocked:
                if blocked:
                    break
    
    # Run the recursive cast light function on each octant of tiles around the player
    def fov(self, x, y, radius, dungeon, player, state, grid, aggro_enemies):
        # Calculate lit squares from the given location and radius
        self.tile_visibility[dungeon.player_tile] = 1
        for oct in range(constants.OCTANTS):
            self.cast_light(x, y, 1, 1.0, 0.0, radius, dungeon, player, state, grid,
                            self.mult_matrix[0][oct], self.mult_matrix[1][oct],
                            self.mult_matrix[2][oct], self.mult_matrix[3][oct], aggro_enemies)