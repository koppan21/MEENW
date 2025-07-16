import os
import pandas as pd

csv_data = "power_log_fusion.csv"
percentage_output = os.path.join("results", 'percentage.csv')

df = pd.read_csv(csv_data)

def calculate_percentage(row):
    if row['power_shelly'] != 0:
        return (row['power_hwmon'] / row['power_shelly']) * 100
    else:
        return 0

df['percentage_hwmon_of_shelly'] = df.apply(calculate_percentage, axis=1)

session_percentage = df.groupby('session')['percentage_hwmon_of_shelly'].mean().reset_index()
session_percentage.to_csv(percentage_output, index=False)
