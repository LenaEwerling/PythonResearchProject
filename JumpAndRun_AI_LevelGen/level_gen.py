def adjust_difficulty(df):
    """Analyses data and changes level dynamicly"""

    average_time = df["Time_Survived"].mean()
    avg_speed = df["Speed_At_End"].mean()

    # Logik for changes
    if avg_time < 20:  #players often die to soon -> make it easier
        speed_factor = 0.9
        more_powerups = True
    elif avg_time > 40:  #players often die late -> make it mor difficult
        speed_factor = 1.1
        morve_powerups = False
    else:  #no aadaptations needed
        speed_factor = 1.0
        more_powerups = False