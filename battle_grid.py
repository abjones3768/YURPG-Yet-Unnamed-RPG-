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
        self.enemies = []
        self.obstacle_groups = [] # will be used to group wall / door tiles together for transparency