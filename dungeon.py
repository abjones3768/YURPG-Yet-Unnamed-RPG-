import random
import constants
from combatActors import Player, Goblin
from combatItems import *

# Dungeon room templates
CENTER_WALL_H = 0
CENTER_WALL_V = 1
FOUR_PILLARS = 2                                      
CISTERN = 3
RUINS = 4

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
        self.chests = {}
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
            if random.random() < 0.5:
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

    def get_room_template(self, w, h):
        room_size = w*h
        ratio  = w / h
        options = []

        if room_size >= 1600:
            options.append(RUINS)
        if ratio < 0.7:
            if room_size < 1600:
                options.append(CENTER_WALL_V)
        elif ratio > 1.3:
            if room_size < 1600:
                options.append(CENTER_WALL_H)
        else:
            if room_size < 1600:
                options.append(CISTERN)
            elif room_size < 3000:
                options.append(FOUR_PILLARS)
        return options[random.randint(0, len(options) - 1)]

    def vertical_wall_template(this_room, xpos, ypos):
        vertical_mid = (this_room.x1 + this_room.x2) // 2
        y_offset = this_room.height // 6
        if xpos == vertical_mid and this_room.y1 + y_offset <= ypos < this_room.y2 - y_offset:
            return constants.WALL
        return constants.FLOOR

    def horizontal_wall_template(this_room, xpos, ypos):
        horizontal_mid = (this_room.y1 + this_room.y2) // 2
        x_offset = this_room.width // 6
        if ypos == horizontal_mid and this_room.x1 + x_offset <= xpos < this_room.x2 - x_offset:
            return constants.WALL
        return constants.FLOOR

    def pillars_template(this_room, xpos, ypos):
        pillar_size = min(this_room.width, this_room.height) // 6
        if ((this_room.x1 + pillar_size <= xpos < this_room.x1 + pillar_size*2 and this_room.y1 + pillar_size <= ypos < this_room.y1 + pillar_size*2) or
            (this_room.x2 - pillar_size > xpos >= this_room.x2 - pillar_size*2 and this_room.y1 + pillar_size <= ypos < this_room.y1 + pillar_size*2) or
            (this_room.x2 - pillar_size > xpos >= this_room.x2 - pillar_size*2 and this_room.y2 - pillar_size > ypos >= this_room.y2 - pillar_size*2) or
            (this_room.x1 + pillar_size <= xpos < this_room.x1 + pillar_size*2 and this_room.y2 - pillar_size > ypos >= this_room.y2 - pillar_size*2)):
            return constants.WALL
        return constants.FLOOR

    def cistern_template(this_room, xpos, ypos):
        cist_gap = min(this_room.width, this_room.height) // 4
        if (xpos >= this_room.x1 + cist_gap and xpos < this_room.x2 - cist_gap and 
           ypos >= this_room.y1 + cist_gap and ypos < this_room.y2 - cist_gap):
           return constants.WATER
        return constants.FLOOR

    def ruins_template(this_room, xpos, ypos):
        return constants.FLOOR

    # Maps room types to their corresponding template functions
    template_map = {
        CENTER_WALL_H : horizontal_wall_template,   # done
        CENTER_WALL_V : vertical_wall_template,     # done
        FOUR_PILLARS: pillars_template,             # done
        CISTERN: cistern_template,                  # done
        RUINS: ruins_template                       # done
    }

class Dungeon:
    def __init__(self, cell_size, start_x, start_y, map_width, map_height, total_rooms, min_room_size):
        self.new_dungeon(cell_size, start_x, start_y, map_width, map_height, total_rooms, min_room_size)

    def new_dungeon(self, cell_size, start_x, start_y, map_width, map_height, total_rooms, min_room_size):
        self.root = Room(start_x, start_y, start_x + map_width, start_y + map_height)
        self.cell_size = cell_size
        self.map_width = map_width
        self.map_height = map_height
        self.total_rooms = total_rooms
        self.min_cell_size = min_room_size
        self.rooms = []
        self.enemies = {}
        self.sub_dungeons = []
        self.tiles = [constants.SHADOW] * (map_width * map_height)
        self.player_tile = None
        self.start_room = None
        self.parent = None
        self.in_room = False
        self.current_room = None
        weaponInit()
        armorInit()
        itemInit()

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
                if self.parent.tiles[(neighbor.y1+1) * self.parent.map_width + cx] == constants.FLOOR and self.parent.tiles[(room.y2-2) * self.parent.map_width + cx] == constants.FLOOR:
                    for x in range(cx-2, cx+2):
                        if x != room.x1 and x != room.x2-1:
                            self.parent.tiles[neighbor.y1 * self.parent.map_width + x] = constants.FLOOR
                            self.parent.tiles[(room.y2-1) * self.parent.map_width + x] = constants.FLOOR
            for neighbor in room.h_neighbors:
                min_y2 = min(room.y2, neighbor.y2)
                max_y1 = max(room.y1, neighbor.y1)
                cy = int(max_y1 + min_y2) // 2
                if self.parent.tiles[cy * self.parent.map_width + neighbor.x1+1] == constants.FLOOR and self.parent.tiles[cy * self.parent.map_width + room.x2-2] == constants.FLOOR:
                    for y in range(cy-2, cy+2):
                        if y != room.y1 and y != room.y2-1:
                            self.parent.tiles[y * self.parent.map_width + neighbor.x1] = constants.FLOOR
                            self.parent.tiles[y * self.parent.map_width + room.x2-1] = constants.FLOOR

    def createHCorridor(self, x1, x2, cy):
        for y in range(cy-3, cy+2):
            for x in range(x1-1, x2+1):
                index = y * self.map_width + x
                if y == cy-3 or y == cy+1:
                    self.tiles[index] = constants.WALL
                elif x == x1-1 or x == x2:
                    self.tiles[index] = constants.DOOR
                else:
                    self.tiles[index] = constants.FLOOR

    def createVCorridor(self, y1, y2, cx):
        for x in range(cx-3, cx+2):
            for y in range(y1-1, y2+1):
                index = y * self.map_width + x
                if x == cx-3 or x == cx+1:
                    self.tiles[index] = constants.WALL
                elif y == y1-1 or y == y2:
                    self.tiles[index] = constants.DOOR
                else:
                    self.tiles[index] = constants.FLOOR

    def open_door(self, index):
        left = index-1
        right = index+1
        up = index-self.map_width
        down = index+self.map_width
        self.tiles[index] = constants.FLOOR
        if self.tiles[left] == constants.DOOR:
            self.open_door(left)
        if self.tiles[right] == constants.DOOR:
            self.open_door(right)
        if self.tiles[up] == constants.DOOR:
            self.open_door(up)
        if self.tiles[down] == constants.DOOR:
            self.open_door(down)

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
        self.fill_rooms()
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
            sub_dungeon = Dungeon(self.cell_size, room.x1, room.y1, room.width, room.height, subroom_count, 8)
            sub_dungeon.parent = self
            sub_dungeon.subdivide_room()

    def placePlayer(self):
        self.start_room = self.rooms[random.randint(1, self.total_rooms-1)]
        self.player_tile = self.start_room.x1
        self.current_room = self.start_room
        self.in_room = True
        while self.tiles[self.player_tile] != constants.FLOOR:
            start_col = random.randint(self.start_room.x1 + 2, self.start_room.x2 - 2)
            start_row = random.randint(self.start_room.y1 + 2, self.start_room.y2 - 2)
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
                        tile_type = constants.WALL
                    else:
                        if is_world_map:
                            tile_type = Room.template_map[room.template](room, x, y)
                        else:
                            tile_type = constants.FLOOR
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

    def get_current_room(self, player):
        for room in self.rooms:
            player_x = player.x // constants.TILE_SIZE
            player_y = player.y // constants.TILE_SIZE
            if room.x1 <= player_x < room.x2 and room.y1 <= player_y < room.y2:
                return room

    # Spawn distribution of enemies in each room based on size.
    def fill_rooms(self):
        for room in self.rooms:
            # Calculate number of enemies in each room
            size = room.width * room.height
            room_level = 0
            enemy_count = 0
            chest_count = 0
            if size < 1600:
                room_level = 1
            elif size < 3200:
                room_level = 2
            elif size < 6400:
                room_level = 3
            else:
                room_level = 4
            enemy_chance = room_level/4
            chest_chance = room_level/8
            if random.random() <= enemy_chance:
                enemy_count = random.randint(1, 2) * room_level
                chest_count = random.randint(1, room_level)

            # Place any enemies in random floor tiles
            placed_enemies = 0
            while placed_enemies < enemy_count:
                place_tile = constants.SHADOW
                while self.tiles[place_tile] != constants.FLOOR:
                    place_col = random.randint(room.x1 + 2, room.x2 - 2)
                    place_row = random.randint(room.y1 + 2, room.y2 - 2)
                    place_tile = place_row * self.map_width + place_col
                enemy = Goblin(place_col*constants.TILE_SIZE, place_row*constants.TILE_SIZE, place_tile)
                self.equip_enemy(enemy)
                self.enemies[place_tile] = enemy
                self.tiles[place_tile] = constants.ENEMY
                placed_enemies += 1

            placed_chests = 0
            while placed_chests < chest_count:
                place_tile = constants.SHADOW
                while self.tiles[place_tile] != constants.FLOOR:
                    place_col = random.randint(room.x1 + 2, room.x2 - 2)
                    place_row = random.randint(room.y1 + 2, room.y2 - 2)
                    place_tile = place_row * self.map_width + place_col
                room.chests[place_tile] = self.fill_chest()
                self.tiles[place_tile] = constants.CHEST
                placed_chests += 1

    def equip_enemy(self, enemy):
        job = random.randint(0, 2)
        weap_chance = random.random()
        armor_chance = random.random()
        if weap_chance > 0.25:
            if job == 0:
                enemy.inventory.append(weaponDict["Iron Sword"])
            elif job == 1:
                enemy.inventory.append(weaponDict["Iron Dagger"])
            else:
                enemy.inventory.append(weaponDict["Wooden Staff"])
        elif weap_chance > 0.1:
            if job == 0:
                enemy.inventory.append(weaponDict["Steel Sword"])
            elif job == 1:
                enemy.inventory.append(weaponDict["Steel Dagger"])
            else:
                enemy.inventory.append(weaponDict["Ebony Staff"])
        else:
            if job == 0:
                enemy.inventory.append(weaponDict["Mythril Sword"])
            elif job == 1:
                enemy.inventory.append(weaponDict["Mythril Dagger"])
            else:
                enemy.inventory.append(weaponDict["Staff of Wisdom"])
        if armor_chance > 0.25:
            if job == 0:
                enemy.inventory.append(armorDict["Iron Chestplate"])
            elif job == 1:
                enemy.inventory.append(armorDict["Steel Chestplate"])
            else:
                enemy.inventory.append(armorDict["Mythril Chestplate"])
        elif armor_chance > 0.1:
            if job == 0:
                enemy.inventory.append(armorDict["Cloth Shirt"])
            elif job == 1:
                enemy.inventory.append(armorDict["Leather Cuirass"])
            else:
                enemy.inventory.append(armorDict["Studded Leather Cuirass"])
        else:
            if job == 0:
                enemy.inventory.append(armorDict["Apprentice Robe"])
            elif job == 1:
                enemy.inventory.append(armorDict["Journeyman Robe"])
            else:
                enemy.inventory.append(armorDict["Master Robe"])

    # Update to take player class into account and make chests have a
    # chance to contain gear for your class
    def fill_chest(self):
        if random.random() > 0.5:
            return itemDict["Potion"]
        else:
            return itemDict["Elixir"]