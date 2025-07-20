import os
import sys
import pandas as pd

data_folder = "results"
power_input = 'power_log_fusion.csv'
power_output = os.path.join(data_folder, 'power_log_corrected.csv')
mean_output = os.path.join(data_folder, 'mean.csv') # Changed 'media_output' to 'mean_output' for consistency

try:
    df = pd.read_csv(power_input)
except FileNotFoundError:
    print("ERROR: File not found. Please check the path.")
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)

# Convert power columns to numeric, coercing errors
df["power_shelly"] = pd.to_numeric(df["power_shelly"], errors='coerce')
df["power_hwmon"] = pd.to_numeric(df["power_hwmon"], errors='coerce')

# Calculate the mean of 'power_shelly' and 'power_hwmon' for "Background" sessions
background = df[df["session"] == "Background"]
shelly_bg_mean = background["power_shelly"].mean()
system_bg_mean = background["power_hwmon"].mean() # Changed 'sistema_bg_mean' to 'system_bg_mean'

# Create a new DataFrame with background-corrected power values
corrected_data = pd.DataFrame({
    "timestamp": df["timestamp"],
    "power_shelly_c": df["power_shelly"] - shelly_bg_mean,
    "power_hwmon_c": df["power_hwmon"] - system_bg_mean,
    "session": df["session"]
})

# Save the corrected power data to a CSV file
corrected_data.to_csv(power_output, index=False)

# Create a DataFrame to store the calculated background means
mean_data = pd.DataFrame({
    "shelly_mean": [shelly_bg_mean],
    "hwmon_mean": [system_bg_mean]
})

# Save the background mean values to a CSV file
mean_data.to_csv(mean_output, index=False)