import pandas as pd
import os
from datetime import datetime
import json

DATA_FILE = "data/game_data.csv"
PARAMETER_FILE = "analysis/parameter.json"

class DataLogger:
    """Class for logging game data and statistics."""
    def __init__(self):
        """Initialize the data logger with default values."""
        self.time_survived = 0
        self.speed_at_end = 0
        self.change_interval = 0
        self.speed_factor = 0
        self.spawn_interval = 0
        self.spawn_factor = 0
        self.obstacles_cleared = 0
        self.kinds_of_obstacles_cleared = [
            {"name": "low_block", "count": 0},
            {"name": "high_block", "count": 0},
        ]
        self.kinds_of_movement = [
            {"name": "single_jump", "count": 0},
            {"name": "double_jump", "count": 0},
        ]
        self.death_cause = ""

    def load_parameters(self):
        """Load game parameters from JSON file."""
        with open(PARAMETER_FILE, 'r') as f:
            self.params = json.load(f)

    def save_game_data(self):
        """Save game data to CSV file."""
        difficultyLevel, difficulty_score = self.calculate_difficulty_score()
        print("after calculate_difficulty_score")
        # Data as dictionary
        data = {
            "DateTime": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Time_Survived": [self.time_survived],
            "Speed_At_End": [self.speed_at_end],
            "Change_Interval": [self.change_interval],
            "Speed_Factor": [self.speed_factor],
            "Spawn_Interval": [self.spawn_interval],
            "Spawn_Factor": [self.spawn_factor],
            "Obstacles_Cleared": [self.obstacles_cleared],
            "Kinds_Of_Obstacles_Cleared": [self.kinds_of_obstacles_cleared],
            "Kinds_Of_Movement": [self.kinds_of_movement],
            "Death_Cause": [self.death_cause],
            "Difficulty_Level": [difficultyLevel],
            "Difficulty_Score": [difficulty_score],
            #"Powerups_Used": [powerups_used]
        }

        df = pd.DataFrame(data)

        # If file exists, append, else create new
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(DATA_FILE, header=True, index=False)

        print(f"Saved run to {DATA_FILE}")

    def calculate_difficulty_score(self):
        """Calculate difficulty level and score based on parameters."""
        print("calculate_difficulty")
        self.load_parameters()
        print("loaded parameters")
        # Soft limits and reference values
        max_speed = -10.0      # Soft limit for speed
        min_speed = -2.0        # Soft limit for speed
        min_spawn_rate = 0.2          # Corresponds to spawn_interval = 5.0
        max_spawn_rate = 2.0          # Corresponds to spawn_interval = 0.5
        max_obstacle_factor = 1.0   
        min_obstacle_factor = 0.0
        max_speed_factor = 5.0        # Assumption: Maximum speed_factor (adjustable)
        min_speed_factor = 0.5       # Assumption: Minimum speed_factor (adjustable)
        max_spawn_factor = 0.5        # Assumption: Maximum spawn_factor (adjustable)
        min_spawn_factor = 5.0       # Assumption: Minimum spawn_factor (adjustable)

        # Normalization of parameters
        speed_norm = max(0, (self.params['speed'] - min_speed) / (max_speed - min_speed))  # Scaled relative to -5 and -10
        print(f"speed_norm: {speed_norm}")
        spawn_rate = 1 / self.params['spawn_interval']
        spawn_rate_norm = max(0, (spawn_rate - min_spawn_rate) / (max_spawn_rate - min_spawn_rate))  # Scaled relative to 0.2 and 2.0
        spawn_rate_norm = min(1, spawn_rate_norm)  # Cap at [0, 1]
        print(f"spawn_rate_norm: {spawn_rate_norm}")
        obstacle_factor_norm = max(0, (self.params['obstacle_factor'] - min_obstacle_factor) / (max_obstacle_factor - min_obstacle_factor))  # Scaled to [0, 1]
        print(f"obstacle_factor_norm: {obstacle_factor_norm}")
        speed_factor_norm = (self.params['speed_factor'] - min_speed_factor) / (max_speed_factor - min_speed_factor)  # Scaled to [0, 1]
        print(f"speed_factor_norm: {speed_factor_norm}")
        spawn_factor_norm = (self.params['spawn_factor'] - min_spawn_factor) / (max_spawn_factor - min_spawn_factor)  # Scaled to [0, 1]
        print(f"spawn_factor_norm: {spawn_factor_norm}")

        # Weighted difficulty score
        weights = {
            'speed': 0.3,
            'spawn_rate': 0.3,
            'obstacle_factor': 0.2,
            'speed_factor': 0.1,
            'spawn_factor': 0.1
        }
        difficulty_score = (
            weights['speed'] * speed_norm +
            weights['spawn_rate'] * spawn_rate_norm +
            weights['obstacle_factor'] * obstacle_factor_norm +
            weights['speed_factor'] * speed_factor_norm +
            weights['spawn_factor'] * spawn_factor_norm
        )
        difficulty_score = max(0, difficulty_score)  # Prevent negative scores

        # Determine difficulty level
        if difficulty_score <= 0.2:
            return "Beginner", difficulty_score
        elif difficulty_score <= 0.4:
            return "Novice", difficulty_score
        elif difficulty_score <= 0.6:
            return "Intermediate", difficulty_score
        elif difficulty_score <= 0.8:
            return "Advanced", difficulty_score
        else:
            return "Master", difficulty_score