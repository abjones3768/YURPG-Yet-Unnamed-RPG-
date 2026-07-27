import random

"""
TODO:
- Finish room templates and apply them after drawing rooms/corridors initially
- Implement random RUBBLE tile segments in each room that represent
  segments of tiles that are elevated above the ground for combat
- Create new tile types (chest, enemy, portal, etc)
- Function to generate enemies and items

IDEA:
- Randomly place keys in different chests around the map
- Collect all x keys to unlock the teleporter that takes you to the boss
"""

# room_templates
EMPTY = 0              #- empty room                                           - only sm rooms
CENTER_WALL_H = 1      #- wall along center in horizontal room                 - only sm and med horizontal rooms
CENTER_WALL_V = 2      #- wall along center in vertical room                   - only sm and med vertical rooms
FOUR_PILLARS = 3       #- four pillars, one in each corner of the room         - only sm and med square rooms                                     - only med and lg square rooms
# PORTAL = 4           #- portal room                                          - portal room is randomly-selected during dungeon generation
CISTERN = 5            #- large rectangular pool of water in center            - any med room
RUINS = 6              #- room is subdivided into subrooms connected by doors  - any med or lg room

class Room:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1
        self.left = None
        self.right = None
        self.h_neighbors = []
        self.v_neighbors = []
        self.template = None

    def shrink(self, min_size):
        if self.left == None:
            new_width = int(max(self.width * random.uniform(0.3, 0.9), min_size))
            new_height = int(max(self.height * random.uniform(0.3, 0.9), min_size))
            self.x1 = int(self.x1 + 0.5*(self.width - new_width))
            self.x2 = int(self.x2 - 0.5*(self.width - new_width))
            self.y1 = int(self.y1 + 0.5*(self.height - new_height))
            self.y2 = int(self.y2 - 0.5*(self.height - new_height))
            self.width = new_width
            self.height = new_height
        else:
            self.left.shrink(min_size)
            self.right.shrink(min_size)

    def getRooms(self, nodes):
        if self.left == None:
            nodes.append(self)
        else:
            self.left.getRooms(nodes)
            self.right.getRooms(nodes)

    def divideCell(self, min_size):
        if self.width < min_size or self.height < min_size:
            return False
        if self.left != None:
            if random.randint(1, 100) < 50:
                return self.left.divideCell(min_size)
            else:
                return self.right.divideCell(min_size)
        if self.width > self.height:
            midpoint = int(self.x1 + random.uniform(0.3, 0.6) * self.width)
            self.left = Room(self.x1, self.y1, midpoint, self.y2)
            self.right = Room(midpoint, self.y1, self.x2, self.y2)
            return True
        else:
            midpoint = int(self.y1 + random.uniform(0.3, 0.6) * self.height)
            self.left = Room(self.x1, self.y1, self.x2, midpoint)
            self.right = Room(self.x1, midpoint, self.x2, self.y2)
            return True

    # Randomly place segments of rubble tiles in each room that, when rendered in
    # isometric mode for combat, elevate those tiles to varying degrees
    def get_room_template(self, w, h):
        room_size = w*h
        ratio  = w / h
        options = []

        if room_size < 800:
            options.append(EMPTY)
        else:
            options.append(RUINS)
        if room_size >= 1600:
            #options.append(LIBRARY)
            #options.append(ARMORY)
            #options.append(CATACOMBS)
            if 800 < room_size <= 2400:
                options.append(CISTERN)
                options.append(FOUR_PILLARS)
        if ratio < 0.7:
            if room_size < 1600:
                options.append(CENTER_WALL_V)
        elif ratio > 1.3:
            if room_size < 1600:
                options.append(CENTER_WALL_H)
        return options[random.randint(0, len(options) - 1)]

    def empty_template(this_room, xpos, ypos):
        return 0

    def vertical_wall_template(this_room, xpos, ypos):
        vertical_mid = (this_room.x1 + this_room.x2) // 2
        y_offset = this_room.height // 6
        if xpos == vertical_mid and this_room.y1 + y_offset <= ypos < this_room.y2 - y_offset:
            return 1
        return 0

    def horizontal_wall_template(this_room, xpos, ypos):
        horizontal_mid = (this_room.y1 + this_room.y2) // 2
        x_offset = this_room.width // 6
        if ypos == horizontal_mid and this_room.x1 + x_offset <= xpos < this_room.x2 - x_offset:
            return 1
        return 0

    def pillars_template(this_room, xpos, ypos):
        pillar_size = min(this_room.width, this_room.height) // 6
        if ((this_room.x1 + pillar_size <= xpos < this_room.x1 + pillar_size*2 and this_room.y1 + pillar_size <= ypos < this_room.y1 + pillar_size*2) or
            (this_room.x2 - pillar_size > xpos >= this_room.x2 - pillar_size*2 and this_room.y1 + pillar_size <= ypos < this_room.y1 + pillar_size*2) or
            (this_room.x2 - pillar_size > xpos >= this_room.x2 - pillar_size*2 and this_room.y2 - pillar_size > ypos >= this_room.y2 - pillar_size*2) or
            (this_room.x1 + pillar_size <= xpos < this_room.x1 + pillar_size*2 and this_room.y2 - pillar_size > ypos >= this_room.y2 - pillar_size*2)):
            return 1
        return 0

    def cistern_template(this_room, xpos, ypos):
        cist_gap = min(this_room.width, this_room.height) // 4
        if (xpos >= this_room.x1 + cist_gap and xpos < this_room.x2 - cist_gap and 
           ypos >= this_room.y1 + cist_gap and ypos < this_room.y2 - cist_gap):
           return 3
        return 0

    def ruins_template(this_room, xpos, ypos):
        return 0

    def portal_template(this_room, xpos, ypos):
        return 0

    # Maps room types to their corresponding template functions
    template_map = {
        EMPTY: empty_template,                      # done
        CENTER_WALL_H : horizontal_wall_template,   # done
        CENTER_WALL_V : vertical_wall_template,     # done
        FOUR_PILLARS: pillars_template,             # done
        # PORTAL: portal_template,
        CISTERN: cistern_template,                  # done
        RUINS: ruins_template                       # done
    }

class Dungeon:
    def __init__(self, cell_size, start_x, start_y, map_width, map_height, total_rooms):
        self.root = Room(start_x, start_y, start_x + map_width, start_y + map_height)
        self.cell_size = cell_size
        self.map_width = map_width
        self.map_height = map_height
        self.total_rooms = total_rooms
        self.min_cell_size = cell_size
        self.rooms = []
        self.sub_dungeons = []
        self.tiles = [-1] * (map_width * map_height)
        self.player_tile = None
        self.parent = None

    def shrinkRooms(self):
        self.root.shrink(self.min_cell_size)

    def findNeighbors(self):
        self.root.getRooms(self.rooms)
        for room_A in self.rooms:
            for room_B in self.rooms:
                if room_A != room_B:
                    if room_A.x2 == room_B.x1:
                        if max(room_A.y1, room_B.y1) < min(room_A.y2, room_B.y2):
                            room_A.h_neighbors.append(room_B)
                    if room_A.y2 == room_B.y1:
                        if max(room_A.x1, room_B.x1) < min(room_A.x2, room_B.x2):
                            room_A.v_neighbors.append(room_B)

    def create_subdungeon_doors(self):
        for room in self.rooms:
            for neighbor in room.v_neighbors:
                min_x2 = min(room.x2, neighbor.x2)
                max_x1 = max(room.x1, neighbor.x1)
                cx = int(max_x1 + min_x2) // 2
                if self.parent.tiles[(neighbor.y1+1) * self.parent.map_width + cx] == 0 and self.parent.tiles[(room.y2-2) * self.parent.map_width + cx] == 0:
                    for x in range(cx-3, cx+2):
                        self.parent.tiles[neighbor.y1 * self.parent.map_width + x] = 0
                        self.parent.tiles[(room.y2-1) * self.parent.map_width + x] = 0
            for neighbor in room.h_neighbors:
                min_y2 = min(room.y2, neighbor.y2)
                max_y1 = max(room.y1, neighbor.y1)
                cy = int(max_y1 + min_y2) // 2
                if self.parent.tiles[cy * self.parent.map_width + neighbor.x1+1] == 0 and self.parent.tiles[cy * self.parent.map_width + room.x2-2] == 0:
                    for y in range(cy-2, cy+2):
                        self.parent.tiles[y * self.parent.map_width + neighbor.x1] = 0
                        self.parent.tiles[y * self.parent.map_width + room.x2-1] = 0

    def createHCorridor(self, x1, x2, cy):
        for y in range(cy-3, cy+2):
            for x in range(x1-2, x2+2):
                if y == cy-3 or y == cy+1:
                    if x == x1-2 or x == x2+1:
                        self.tiles[y * self.map_width+ x] = 0
                    else:
                        self.tiles[y * self.map_width + x] = 1
                elif x == x1-1 or x == x2:
                    self.tiles[y * self.map_width + x] = 2
                else:
                    self.tiles[y * self.map_width + x] = 0

    def createVCorridor(self, y1, y2, cx):
        for x in range(cx-3, cx+2):
            for y in range(y1-2, y2+2):
                if x == cx-3 or x == cx+1:
                    if y == y1-2 or y == y2+1:
                        self.tiles[y * self.map_width + x] = 0
                    else:
                        self.tiles[y * self.map_width + x] = 1
                elif y == y1-1 or y == y2:
                    self.tiles[y * self.map_width + x] = 2
                else:
                    self.tiles[y * self.map_width + x] = 0

    def generateDungeon(self):
        cur_room_count = 1
        while cur_room_count < self.total_rooms:
            if self.root.divideCell(self.min_cell_size):
                cur_room_count += 1
        self.findNeighbors()
        self.shrinkRooms()
        self.set_room_tiles(True)
        self.subdivide_subdungeons()
        self.set_corridor_tiles()
        self.placePlayer()
        return self.tiles

    def subdivide_room(self):
        subroom_count = 1
        while subroom_count < self.total_rooms:
            if self.root.divideCell(self.min_cell_size):
                subroom_count += 1
        self.findNeighbors()
        self.set_room_tiles(False)
        self.create_subdungeon_doors()

    def subdivide_subdungeons(self):
        for i in self.sub_dungeons:
            room = self.rooms[i]
            subroom_count = room.width * room.height // 320
            sub_dungeon = Dungeon(self.cell_size, room.x1, room.y1, room.width, room.height, subroom_count)
            sub_dungeon.parent = self
            sub_dungeon.subdivide_room()

    def placePlayer(self):
        start_room = self.rooms[random.randint(1, self.total_rooms-1)]
        self.player_tile = start_room.x1
        while self.tiles[self.player_tile] != 0:
            start_col = random.randint(start_room.x1 + 2, start_room.x2 - 2)
            start_row = random.randint(start_room.y1 + 2, start_room.y2 - 2)
            self.player_tile = start_row * self.map_width + start_col

    def set_room_tiles(self, is_world_map):
        dungeon = self
        for i, room in enumerate(self.rooms):
            room.template = room.get_room_template(room.width, room.height)
            if is_world_map:
                if room.template == RUINS:
                    self.sub_dungeons.append(i)
            else:
                dungeon = self.parent

            for y in range(room.y1, room.y2):
                for x in range(room.x1, room.x2):
                    if x == room.x1 or x == room.x2-1 or y == room.y1 or y == room.y2-1:
                        tile_type = 1
                    else:
                        if is_world_map:
                            tile_type = Room.template_map[room.template](room, x, y)
                        else:
                            tile_type = 0
                    dungeon.tiles[y * dungeon.map_width + x] = tile_type

    def set_corridor_tiles(self):
        for room in self.rooms:
            for neighbor in room.h_neighbors:
                min_y2 = min(room.y2, neighbor.y2)
                max_y1 = max(room.y1, neighbor.y1)
                if min_y2 - max_y1 > 6:
                    cy = int(max_y1 + min_y2) // 2
                    self.createHCorridor(room.x2, neighbor.x1, cy)
            for neighbor in room.v_neighbors:
                min_x2 = min(room.x2, neighbor.x2)
                max_x1 = max(room.x1, neighbor.x1)
                if min_x2 - max_x1 >= 6:
                    cx = int(max_x1 + min_x2) // 2
                    self.createVCorridor(room.y2, neighbor.y1, cx)