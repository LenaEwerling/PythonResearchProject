import pandas as pd
#import mathplotlib as plt
import os
import json

DATA_FILE = "data/game_data.csv"
PARAMETER_FILE = "parameter.json"

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

    def adjust_difficulty(self):
        print("adjust_difficulty")
        if not self.data_file.empty:
            increases = self.data_file['Time_Survived'] / self.data_file['Change_Interval']
            #increases = [int(row['Time_Survived']) / float(row['Change_Interval']) for row in self.data_file]
            if not increases.empty:
                print(f"increases: {increases}")
                avg_increases = increases.mean()
                remainder = avg_increases % 1
                if avg_increases <= 3:
                    self.params['speed_factor'] -= 0.02
                    self.params['spawn_factor'] += 0.02
                elif avg_increases >= 9:
                    self.params['speed_factor'] += 0.02
                    self.params['spawn_factor'] -= 0.02
                print(f"adjusted parameters: {self.params}")

    def analyze(self):
        self.load_data()
        self.load_parameters()
        self.adjust_difficulty()
        self.save_parameters()
 



# # calculate average time survived
# average_time = df["Time_Survived"].mean()
# print(f"Avarage time survived: {average_time:.2f} seconds")

# # plot histogram of time survived
# plt.hist(df["Time_Survived"], bins=10, color='blue', alpha=0.7)
# plt.xlabel("Time survived (seconds)")
# plt.ylabel("Run count")
# plt.title("Distribution of survival time")
# plt.show()