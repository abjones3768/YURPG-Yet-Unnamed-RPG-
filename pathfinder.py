import constants

"""
Use A* algorithm to calculate shortest path between start and dest tiles.
Outputs a dictionary called 'node-map' that contains all tiles that were traversed.
Each value in the dict has a parent that allows the path to be traversed.
"""

def findPath(actor, tilemap, dest, state, grid):
    start = actor.cur_tile          # player tile
    width = tilemap.map_width       # dungeon width in tiles
    open_set = {start}              # stores tiles that have not yet been checked
    closed_set = set()              # stores tiles that have already been checked
    map_size = len(tilemap.tiles)   # total number of tiles in the dungeon
    
    # Maps tiles to lists containing gx, hx, fx, and parent for A* calculations
    # Each tile in the dict's parent is used to traverse the path
    # from start to dest
    node_map = {}
    node_map[start] = [0, 0, 0, None]
    
    # While there are still tiles to check, set the current tile being checked to
    # the one in the open set with the lowest f-score
    while open_set:
        cur = min(open_set, key=lambda tile: node_map[tile][2])
        open_set.remove(cur)
        closed_set.add(cur)
        
        # When destination tile is reached, return the dict for traversal
        if cur == dest:
            return node_map
        
        neighbors = [
            cur - 1,       # left
            cur + 1,       # right
            cur - width,   # up
            cur + width    # down
        ]

        # Check each valid neighbor of the current tile and add each one that hasn't
        # been checked, or needs to have its g-score updated, to both the open set and
        # the node map
        # If in combat, check each n to see if it is in battle_grid bounds before parsing
        for n in neighbors:
            is_valid = True
            cur_tile = tilemap.tiles[n]
            if cur_tile == constants.FLOOR or cur_tile == constants.DOOR:
                if state == constants.COMBAT_STATE and not (grid.x1 <= n%width <= grid.x2 and grid.y1 <= n//width <= grid.y2):
                    is_valid = False
                if 0 <= n < map_size and n not in closed_set and is_valid:
                    g = node_map[cur][0] + 1
                    if n not in open_set or g < node_map[n][0]:
                        open_set.add(n)
                        h = abs(n%width - dest%width) + abs(n//width - dest//width)
                        node_map[n] = [g, h, g+h, cur]