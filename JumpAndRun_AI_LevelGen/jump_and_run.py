from os import write

import pygame
import time
import config
import Player
import Obstacle
import data_logger

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Jump and Run AI Level Gen")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game objects
        self.player = Player.Player()
        self.obstacle = Obstacle.Obstacle(speed = 5)
        self.start_time = time.time()
        self.speed_increase_interval = 5 # increase every 5 seconds
        self.sped_increase_summand = 0.5 # increase by 0.5
        self.logger = data_logger.DataLogger()

    def check_collision(self):
        """checks whether player collides with an obstacle"""
        if self.player.x < self.obstacle.x + self.obstacle.width and self.player.x + self.player.width > self.obstacle.x:
            if self.player.y + self.player.height > self.obstacle.y:
                return True
        return False

    def detect_collision(self):
        """handles collision between player and obstacle as well as a player passing an object successfully"""
        if self.check_collision():
            self.log_end_of_game()
            elapsed_time = self.logger.time_survived
            print("Game Over! Time survived: " + str(elapsed_time))
            self.running = False
        else:
            self.check_passed_obstacle()

    def check_passed_obstacle(self):
        """checks whether player has passed an obstacle"""
        if self.obstacle.x + self.obstacle.width < self.player.x and self.obstacle.counted == False:
            self.obstacle.counted = True
            self.logger.obstacles_cleared += 1
            for obstacle in self.logger.kinds_of_obstacles_cleared:
                if obstacle["name"] == self.obstacle.type["name"]:
                    obstacle["count"] += 1

    def log_jump(self, jump_height):
        if jump_height != 0:
            name = ""
            match jump_height:
                case 1:
                    name = "single_jump"
                case 2:
                    name = "double_jump"
            for movement in self.logger.kinds_of_movement:
                if movement["name"] == name:
                    movement["count"] += 1

    def log_end_of_game(self):
        """logs end stats of game"""
        self.logger.speed_at_end = self.obstacle.speed
        self.logger.speed_factor = self.sped_increase_summand
        self.logger.death_cause = self.obstacle.type["name"]
        self.logger.time_survived = self.calculate_time_survived()
        self.logger.save_game_data()

    def calculate_time_survived(self):
        return round(time.time() - self.start_time, 2)

    def handle_events(self):
        """handles events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()

    def draw(self):
        """drawing environment, Player, Obstacles and time survived"""
        self.player.draw(self.screen)
        self.obstacle.draw(self.screen)
        pygame.draw.rect(self.screen, config.GROUND_COLOR, (0, config.HEIGHT - 20, config.WIDTH, 20))  # ground

        # show time survived
        elapsed_time = self.calculate_time_survived()
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Time: {elapsed_time}", True, config.BLACK)
        self.screen.blit(text, (10, 10))

    def run(self):
        """runs the game"""
        while self.running:
            self.clock.tick(config.FPS)
            self.screen.fill(config.WHITE)

            self.handle_events()

            # game logic
            self.log_jump(self.player.apply_gravity())

            if self.obstacle.move(): # in case the obstacle moves out of the window
                self.obstacle = Obstacle.Obstacle(speed=self.obstacle.speed)

            # increase the speed
            if time.time() - self.start_time > self.speed_increase_interval:
                self.obstacle.speed += 0.5
                self.speed_increase_interval += 5

            self.detect_collision()
            self.draw()

            pygame.display.update()

        pygame.quit()