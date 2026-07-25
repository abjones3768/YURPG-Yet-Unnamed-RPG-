import random

"""
TODO:
- Define a set of rules for generating room interiors and create an interiorGen function
  that creates interior walls/obstacles for each room in the dungeon
- Create new tile types (chest, key, etc)
- Function to generate enemies and items

IDEA:
- Randomly place 10 keys in different areas of the map
- Collect all 10 keys to unlock the teleporter that takes you to the boss?
"""

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

class Dungeon:
    def __init__(self, cell_size, map_width, map_height):
        self.root = None
        self.cell_size = cell_size
        self.map_width = map_width
        self.map_height = map_height
        self.total_rooms = 80
        self.min_cell_size = cell_size
        self.rooms = None
        self.player_tile = None
        self.tiles = self.generateDungeon()

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

    def createHCorridor(self, x1, x2, cy):
        for y in range(cy-3, cy+2):
            for x in range(x1-1, x2+1):
                if y == cy-3 or y == cy+1:
                    self.tiles[y * self.map_width + x] = 1
                elif x == x1-1 or x == x2:
                    self.tiles[y * self.map_width + x] = 2
                else:
                    self.tiles[y * self.map_width + x] = 0


    def createVCorridor(self, y1, y2, cx):
        for x in range(cx-3, cx+2):
            for y in range(y1-1, y2+1):
                if x == cx-3 or x == cx+1:
                    self.tiles[y * self.map_width + x] = 1
                elif y == y1-1 or y == y2:
                    self.tiles[y * self.map_width + x] = 2
                else:
                    self.tiles[y * self.map_width + x] = 0

    def generateDungeon(self):
        cur_room_count = 1
        self.refreshDungeon()
        while cur_room_count < self.total_rooms:
            if self.root.divideCell(self.min_cell_size):
                cur_room_count += 1
        self.findNeighbors()
        self.shrinkRooms()
        self.updateTiles()
        self.placePlayer()
        return self.tiles

    def placePlayer(self):
        start_room = self.rooms[random.randint(1, self.total_rooms-1)]
        start_col = random.randint(start_room.x1 + 2, start_room.x2 - 2)
        start_row = random.randint(start_room.y1 + 2, start_room.y2 - 2)
        self.player_tile = start_row * self.map_width + start_col

    def updateTiles(self):
        for room in self.rooms:
            for y in range(room.y1, room.y2):
                for x in range(room.x1, room.x2):
                    if x == room.x1 or x == room.x2-1 or y == room.y1 or y == room.y2-1:
                        tile_type = 1
                    else:
                        tile_type = 0
                    self.tiles[y * self.map_width + x] = tile_type
        for room in self.rooms:
            for neighbor in room.h_neighbors:
                min_y2 = min(room.y2, neighbor.y2)
                max_y1 = max(room.y1, neighbor.y1)
                if min_y2 - max_y1 > 5:
                    cy = int(max_y1 + min_y2) // 2
                    self.createHCorridor(room.x2, neighbor.x1, cy)
            for neighbor in room.v_neighbors:
                min_x2 = min(room.x2, neighbor.x2)
                max_x1 = max(room.x1, neighbor.x1)
                if min_x2 - max_x1 >= 5:
                    cx = int(max_x1 + min_x2) // 2
                    self.createVCorridor(room.y2, neighbor.y1, cx)

    def refreshDungeon(self):
        self.root = Room(1, 1, self.map_width-1, self.map_height-1)
        self.rooms = []
        self.tiles = [-1] * (self.map_width * self.map_height)