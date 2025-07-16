import os
import sys
import pandas as pd

data_folder = "results"
power_input = 'power_log_fusion.csv'
power_output = os.path.join(data_folder, 'power_log_corrected.csv')
media_output = os.path.join(data_folder, 'mean.csv')

try:
    df = pd.read_csv(power_input)
except FileNotFoundError:
    print("ERROR: File not found. Please check the path.")
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)

df["power_shelly"] = pd.to_numeric(df["power_shelly"], errors='coerce')
df["power_hwmon"] = pd.to_numeric(df["power_hwmon"], errors='coerce')

# Mean
background = df[df["session"] == "Background"]
shelly_bg_mean = background["power_shelly"].mean()
sistema_bg_mean = background["power_hwmon"].mean()

corrected_data = pd.DataFrame({
    "timestamp": df["timestamp"],
    "power_shelly_c": df["power_shelly"] - shelly_bg_mean,
    "power_hwmon_c": df["power_hwmon"] - sistema_bg_mean,
    "session": df["session"]
})

corrected_data.to_csv(power_output, index=False)

mean_data = pd.DataFrame({
    "shelly_mean": [shelly_bg_mean],
    "hwmon_mean": [sistema_bg_mean]
})

mean_data.to_csv(media_output, index=False)
