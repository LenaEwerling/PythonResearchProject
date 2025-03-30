import pygame
import random
import time

pygame.init()

# window size
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump & Run - Prototype")

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_COLOR = (100, 50, 0)

# player parameters
player_size = 50
player_x = 100
player_y = HEIGHT - player_size - 20
player_velocity_y = 0
gravity = 0.8
jump_strength = -12
is_jumping = False

# obstacle parameters
obstacle_width = 30
#obstacle_height = 50
obstacle_x = WIDTH
#obstacle_y = HEIGHT - obstacle_height - 20
obstacle_speed = 5
obstacle_types = [
    {"height": 30, "requires_double_jump": False}, # small obstacle
    {"height": 60, "requires_double_jump": True}, # big obstacle
]

# game variables
running = True
start_time = time.time()
clock = pygame.time.Clock()
speed_increase_interval = 5 # increase every 5 seconds

# generate first obstacle
current_obstacle = random.choice(obstacle_types)
obstacle_y = HEIGHT - current_obstacle["height"] - 20

while running:
    clock.tick(30)                          # 30 FPS
    screen.fill(WHITE)                      # background color\

    # check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not is_jumping: # single jump
                    player_velocity_y = jump_strength
                    is_jumping = True
                elif current_obstacle["requires_double_jump"]:
                    player_velocity_y = jump_strength

    # apply gravity
    player_velocity_y += gravity
    player_y += player_velocity_y

    # collision with ground
    if player_y >= HEIGHT - player_size - 20:
        player_y = HEIGHT - player_size - 20
        is_jumping = False

    # move obstacles
    obstacle_x -= obstacle_speed
    if obstacle_x < -obstacle_width:
        obstacle_x = WIDTH
        current_obstacle = random.choice(obstacle_types)
        obstacle_y = HEIGHT - current_obstacle["height"] - 20

    # detect collision
    if player_x < obstacle_x + obstacle_width and player_x + player_size > obstacle_x:
        if player_y + player_size > obstacle_y:
            elapsed_time = round(time.time() - start_time, 2)
            print("Game Over! Time survived: " + str(elapsed_time))
            running = False

    # print
    pygame.draw.rect(screen, BLACK, [player_x, player_y, player_size, player_size])  # player
    pygame.draw.rect(screen, BLACK, [obstacle_x, obstacle_y, obstacle_width, current_obstacle["height"]])  # obstacle
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - 20, WIDTH, 20))  # ground

    # show time survived
    elapsed_time = round(time.time() - start_time, 2)
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Time: {elapsed_time}", True, BLACK)
    screen.blit(text, (10, 10))

    pygame.display.update()

pygame.quit()

