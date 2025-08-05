import pandas as pd
import numpy as np
import os
import json
import random

DATA_FILE = "data/game_data.csv"
PARAMETER_FILE = "analysis/parameter.json"

class Analyzer:
    def __init__(self):
        pass

    def load_parameters(self):
        with open(PARAMETER_FILE, 'r') as f:
            self.params = json.load(f)

    def save_parameters(self):
        with open(PARAMETER_FILE, 'w') as f:
            json.dump(self.params, f, indent=2)

    def load_data(self):
        if os.path.isfile(DATA_FILE):
            self.data_file = pd.read_csv(DATA_FILE)

    def analyze(self):
        self.load_data()
        self.load_parameters()
        self.adjust_difficulty()
        print(f"adjusted parameters: {self.params}")
        self.save_parameters()

    def adjust_difficulty(self):
        if not self.data_file.empty:
            last_five = self.data_file[['Time_Survived', 'Change_Interval']].tail(5)
            time_survived = last_five['Time_Survived'].tail(2)
            avg_time_survived = time_survived.mean()
            increases = last_five['Time_Survived'] / last_five['Change_Interval']
            fract_part = increases - np.floor(increases)
            self.adjust_initial_dificulty(avg_time_survived)
            self.adjust_factors(fract_part)
        
    def adjust_initial_dificulty(self, avg_time_survived):
        if avg_time_survived == 0.0:
            print("avg_time_survived is invalid")
            return
        probability = random.random()
        print(probability)
        print(self.params['obstacle_factor'])
        if avg_time_survived <= 30:                      #to difficult
            print("to difficult")
            if (self.params['speed'] >= 1.02):
                self.params['speed'] -= 0.02
            self.params['spawn_interval'] += 0.02
            if (probability <= 0.3 and self.params['obstacle_factor'] >= 0.2):
                print("decrease obstacle difficulty")
                self.params['obstacle_factor'] -= 0.05
        elif avg_time_survived >= 90:                    #to easy
            print("to easy")
            self.params['speed'] += 0.02
            if (self.params['spawn_interval'] <= 0.22):
                self.params['spawn_interval'] -= 0.02
            if (probability <= 0.3 and self.params['obstacle_factor'] <= 0.8):
                print("increase obstacle difficulty")
                self.params['obstacle_factor'] += 0.05
            

    def adjust_factors(self, fract_parts):
        if fract_parts.empty:
            print("fract_parts invalid")
            return
        count_smaller = (fract_parts <= 0.2).sum()
        count_bigger = (fract_parts >= 0.8).sum()
        if (count_smaller  >= 3):                   #change is to abrupt
            print("to abrupt")
            self.params['speed_factor'] -= 0.02
            self.params['spawn_factor'] += 0.02
        elif (count_bigger >= 3):                   #change is to lush
            print("to lush")
            self.params['speed_factor'] += 0.02
            self.params['spawn_factor'] -= 0.02