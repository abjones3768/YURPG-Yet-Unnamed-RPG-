OCTANTS = 8
import tile_types

# Class that implements Björn Bergström's recursive shadowcasting FOV algorithm
class Shadowcaster:
    def __init__(self, width, height):
        # Stores each tile's visibility status
        self.tile_visibility = [0] * (width * height)
        
        # Multiplication matrix used to compute x,y offsets in each octant
        # around the player
        self.mult = [
            [1,  0,  0, -1, -1,  0,  0,  1],
            [0,  1, -1,  0,  0, -1,  1,  0],
            [0,  1,  1,  0,  0, -1, -1,  0],
            [1,  0,  0,  1, -1,  0,  0, -1]
        ]

    # Check if a tile is blocked (either a wall or door tile)
    def blocked(self, dungeon, x, y):
        i = y * dungeon.map_width + x
        return dungeon.tiles[i] == tile_types.WALL or dungeon.tiles[i] == tile_types.DOOR

    # Recursive function that casts shadows behind blocked tiles by segmenting tiles
    # surrounding the player into octants and iterating each octant's tiles.
    # When blocked tiles are encountered, the function uses the slopes between
    # the player's position and each tile's corners to tell which tiles to illuminate.
    # All tiles that lie behind blocked tiles, out of the player's field of view
    # remain shaded.
    def cast_light(self, cx, cy, row, start, end, radius, dungeon, xx, xy, yx, yy):
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
                            self.tile_visibility[Y * dungeon.map_width + X] = 1
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
                                                radius, dungeon, xx, xy, yx, yy)
                                new_start = r_slope

                # Row is scanned; do next row unless last square was blocked:
                if blocked:
                    break
    
    # Run the recursive cast light function on each octant of tiles around the player
    def fov(self, x, y, radius, dungeon):
        "Calculate lit squares from the given location and radius"
        for oct in range(OCTANTS):
            self.cast_light(x, y, 1, 1.0, 0.0, radius, dungeon,
                            self.mult[0][oct], self.mult[1][oct],
                            self.mult[2][oct], self.mult[3][oct])