import random
import pygame
import config

class Obstacle:
    def __init__(self, speed):
        self.width = 30
        self.type = random.choice([
            {"name": "low_block", "height": 30},  # small obstacle
            {"name": "high_block", "height": 60},  # big obstacle
        ])
        self.height = self.type["height"]
        self.x = config.WIDTH
        self.y = config.HEIGHT - self.height - 20
        self.speed = speed
        self.counted = False

    def move(self):
        """moves obstacle to the left"""
        self.x -= self.speed
        if self.x < -self.width:
            return True
        return False

    def draw(self, screen):
        """draws obstacle"""
        pygame.draw.rect(screen, config.BLACK, [self.x, self.y, self.width, self.height])