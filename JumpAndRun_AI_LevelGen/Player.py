import pygame
import config

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = config.HEIGHT - self.height - 20
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_strength = -12
        self.is_jumping = 0

    def jump(self):
        """player is jumping"""
        if self.is_jumping < 2:
            self.velocity_y = self.jump_strength
            self.is_jumping += 1

    def apply_gravity(self):
        """applies gravity"""
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        jump_height = 0

        # collision with ground
        if self.y >= config.HEIGHT - self.height - 20:
            self.y = config.HEIGHT - self.height - 20
            self.velocity_y = 0
            jump_height = self.is_jumping
            self.is_jumping = 0

        return jump_height

    def draw(self, screen):
        """draws player"""
        pygame.draw.rect(screen, config.BLACK, [self.x, self.y, self.width, self.height])