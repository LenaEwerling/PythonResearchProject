import pandas as pd
import os
from datetime import datetime
import time

DATA_FILE = "data/game_data.csv"

class DataLogger:
    def __init__(self):
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

    def save_game_data(self):
        """Saves Gamedata in a csv file"""

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
            #"Powerups_Used": [powerups_used]
        }

        df = pd.DataFrame(data)

        # if file exists, add, else create new
        if os.path.exists(DATA_FILE):
            df.to_csv(DATA_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(DATA_FILE, header=True, index=False)

        print(f"Saved run to {DATA_FILE}")