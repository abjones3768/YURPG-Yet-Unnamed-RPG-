import pygame

class BattleGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = pygame.Surface((width, height))
        self.foreground = pygame.Surface((width, height), pygame.SRCALPHA)
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.actors = []
        self.obstacle_groups = [] # will be used to group wall / door tiles together for transparency

    def group_obstacles(self, tilemap, width, index, tile_type):
        if not any(sprite in group for group in self.obstacle_groups):
            self.obstacle_groups[-1].append(sprite)
            if tilemap[index-1] == tile_type:
                group_obstacles(tilemap, index-1, tile_type)
            elif tilemap[index+1] == tile_type:
                group_obstacles(tilemap, index+1, tile_type)
            elif tilemap[index-width] == tile_type:
                group_obstacles(tilemap, index-width, tile_type)
            elif tilemap[index+width] == tile_type:
                group_obstacles(tilemap, index+width, tile_type)