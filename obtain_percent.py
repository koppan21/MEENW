import os
import pandas as pd

csv_data = "power_log_fusion.csv"
percentage_output = os.path.join("results", 'percentage.csv')

# Load the CSV data into a pandas DataFrame
df = pd.read_csv(csv_data)

def calculate_percentage(row):
    # Calculate the percentage of 'power_hwmon' relative to 'power_shelly'
    # Returns 0 if 'power_shelly' is zero to avoid division by zero errors
    if row['power_shelly'] != 0:
        return (row['power_hwmon'] / row['power_shelly']) * 100
    else:
        return 0

# Apply the calculate_percentage function to each row to create a new column
df['percentage_hwmon_of_shelly'] = df.apply(calculate_percentage, axis=1)

# Group the DataFrame by 'session' and calculate the mean percentage for each session
session_percentage = df.groupby('session')['percentage_hwmon_of_shelly'].mean().reset_index()
# Save the results to a new CSV file
session_percentage.to_csv(percentage_output, index=False)