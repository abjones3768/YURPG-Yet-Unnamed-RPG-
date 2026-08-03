import pygame
import random
import math

"""
Demo for spinning vortex animation that would be cool to represent a portal.
Find keys in the dungeon to activate the portal to take you to the level's boss
or next dungeon or something?
"""

class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.angle = math.radians(random.randint(0, 360))
        self.radius = random.uniform(1, 4)
        self.speed = random.uniform(2, 5)
        self.dist = random.uniform(self.h/4, self.h/2)

    def draw(self, w, h, screen):
        self.angle += 0.06
        self.speed -= 0.03
        self.x = self.w//2 + math.cos(self.angle) * self.dist * self.speed
        self.y = self.h//2 + math.sin(self.angle) * self.dist * self.speed
        color = (100, 0, 255)
        if self.speed <= 0.1:
            self.speed = random.uniform(1, 3)
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)

class Vortex:
    def __init__(self, w, h, count, surf):
        self.width = w
        self.height = h
        self.count = count
        self.particles = [Particle(w, h) for _ in range(count)]

    def play_vortex(self, w, h, surf):
        for p in self.particles:
            p.draw(w, h, surf)