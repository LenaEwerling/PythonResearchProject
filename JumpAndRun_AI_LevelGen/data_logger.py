import pandas as pd
import os

DATA_FILE = "data/game_data.csv"

def save_game_data(run_id, time_survived, speed_at_end, obstacles_cleared, death_cause, powerups_used)
    """Saves Gamedata in a csv file"""

    # Data as dictionary
    data = {
        "Run_ID": [run_id],
        "Time_Survived": [time_survived],
        "Speed_At_End": [speed_at_end],
        "Obstacles_Cleared": [obstacles_cleared],
        "Death_Cause": [death_cause],
        "Powerups_Used": [powerups_used]
    }

    df = pd.DataFrame(data)

    # if file exists, add, else create new
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(DATA_FILE, index=False)

    print(f"Saved run {run_id} to {DATA_FILE}")