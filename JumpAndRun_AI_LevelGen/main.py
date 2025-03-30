import pygame
import random
import time

pygame.init()

# window size
WIDTH, HEIGHT = 800, 400
FPS = 30

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (100, 50, 0)

#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#pygame.display.set_caption("Jump & Run - Prototype")

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = 100
        self.y = HEIGHT - self.height - 20
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

        # collision with ground
        if self.y >= HEIGHT - self.height - 20:
            self.y = HEIGHT - self.height - 20
            self.velocity_y = 0
            self.is_jumping = 0

    def draw(self, screen):
        """draws player"""
        pygame.draw.rect(screen, BLACK, [self.x, self.y, self.width, self.height])


class Obstacle:
    def __init__(self, speed):
        self.width = 30
        self.type = random.choice([
            {"height": 30},  # small obstacle
            {"height": 60},  # big obstacle
        ])
        self.height = self.type["height"]
        self.x = WIDTH
        self.y = HEIGHT - self.height - 20
        self.speed = speed

    def move(self):
        """moves obstacle to the left"""
        self.x -= self.speed
        if self.x < -self.width:
            return True
        return False

    def draw(self, screen):
        """draws obstacle"""
        pygame.draw.rect(screen, BLACK, [self.x, self.y, self.width, self.height])


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Jump and Run AI Level Gen")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game objects
        self.player = Player()
        self.obstacle = Obstacle(speed = 5)
        self.start_time = time.time()
        self.speed_increase_interval = 5 # increase every 5 seconds

    def check_collision(self):
        """checks whether player collides with an obstacle"""
        if self.player.x < self.obstacle.x + self.obstacle.width and self.player.x + self.player.width > self.obstacle.x:
            if self.player.y + self.player.height > self.obstacle.y:
                return True
        return False

    def run(self):
        """runs the game"""
        while self.running:
            self.clock.tick(FPS)
            self.screen.fill(WHITE)

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()

            # game logic
            self.player.apply_gravity()
            if self.obstacle.move(): # in case the obstacle moves out of the window
                self.obstacle = Obstacle(speed=self.obstacle.speed)

            # increase the speed
            if time.time() - self.start_time > self.speed_increase_interval:
                self.obstacle.speed += 0.5
                self.speed_increase_interval += 5

            # collision detection
            if self.check_collision():
                elapsed_time = round(time.time() - self.start_time, 2)
                print("Game Over! Time survived: " + str(elapsed_time))
                self.running = False

            # draw
            self.player.draw(self.screen)
            self.obstacle.draw(self.screen)
            pygame.draw.rect(self.screen, GROUND_COLOR, (0, HEIGHT - 20, WIDTH, 20))  # ground

            # show time survived
            elapsed_time = round(time.time() - self.start_time, 2)
            font = pygame.font.SysFont(None, 36)
            text = font.render(f"Time: {elapsed_time}", True, BLACK)
            self.screen.blit(text, (10, 10))

            pygame.display.update()

        pygame.quit()


# start game
if __name__ == "__main__":
    game = Game()
    game.run()
