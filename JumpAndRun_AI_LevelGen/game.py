from data_logger import save_game_data
import random

# Expamle values from game
run_id = random.randint(1000, 9999)
time_survived = 32.5 #seconds
speed_at_end = 12.3
obstacles_cleared = 15
death_cause = "High_obstacle"
powerups_used = 2

# save data
save_game_data(run_id, time_survived, speed_at_end, obstacles_cleared, death_cause, powerups_used)