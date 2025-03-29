import pandas as pd
import matplotlib as plt

DATA_FILE = "data/game_data.csv"

#read data
df = pd.read_csv(DATA_FILE)

# calculate average time survived
average_time = df["Time_Survived"].mean()
print(f"Avarage time survived: {average_time:.2f} seconds")

# plot histogram of time survived
plt.hist(df["Time_Survived"], bins=10, color='blue', alpha=0.7)
plt.xlabel("Time survived (seconds)")
plt.ylabel("Run count")
plt.title("Distribution of survival time")
plt.show()