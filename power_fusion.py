import csv
from datetime import datetime, timedelta

# Define input and output file names
HWMON_DATA = "power_log_hwmon.csv"
SHELLY_DATA = "power_log_shelly.csv"
FUSION_DATA = "power_log_fusion.csv"


def parse_ts(ts):
    """
    Parses a timestamp string in 'YYYYMMDDTHH:MM:SS' format into a datetime object.
    """
    return datetime.strptime(ts, "%Y%m%dT%H:%M:%S")


# --- Process Hwmon Data ---
# Initialize a list to store processed system (hwmon) data
system_data = []

try:
    with open(HWMON_DATA, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Parse timestamp, convert power to float, and extract session
                timestamp = parse_ts(row["timestamp"])
                power = float(row["power"])
                session = row["session"]
                # Append processed data to the list
                system_data.append({"timestamp": timestamp, "power": power, "session": session})
            except (ValueError, KeyError) as e:
                # Skip rows with parsing errors and print a warning
                print(f"Skipping row in {HWMON_DATA} due to parsing error: {e} - Row: {row}")
                continue
except FileNotFoundError:
    print(f"Error: {HWMON_DATA} not found. Please ensure the file exists.")
    exit()  # Exit the script if a critical input file is missing
except Exception as e:
    print(f"An unexpected error occurred while reading {HWMON_DATA}: {e}")
    exit()

# --- Process Shelly Data ---
# Initialize a list to store processed Shelly data
shelly_data = []
try:
    with open(SHELLY_DATA, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Parse timestamp and convert power to float
                timestamp = parse_ts(row["timestamp"])
                power = float(row["power"])
                # Append processed data to the list
                shelly_data.append({"timestamp": timestamp, "power": power})
            except (ValueError, KeyError) as e:
                # Skip rows with parsing errors and print a warning
                print(f"Skipping row in {SHELLY_DATA} due to parsing error: {e} - Row: {row}")
                continue
except FileNotFoundError:
    print(f"Error: {SHELLY_DATA} not found. Please ensure the file exists.")
    exit()  # Exit the script if a critical input file is missing
except Exception as e:
    print(f"An unexpected error occurred while reading {SHELLY_DATA}: {e}")
    exit()

# --- Fuse Data ---
# Initialize a list to store the fused data
fused_data = []

# Iterate through each Shelly data point
for shelly in shelly_data:
    matched = None
    # Look for a matching system data point based on timestamp proximity
    for sys in system_data:
        delta = abs(shelly["timestamp"] - sys["timestamp"])
        if delta <= timedelta(seconds=1):  # If timestamps are within 1 second, consider them a match
            matched = sys
            break  # Found a match, move to the next Shelly data point
    
    # If a match is found, add the combined data to the fused_data list
    if matched:
        fused_data.append({
            "timestamp": shelly["timestamp"].strftime("%Y%m%dT%H:%M:%S"),  # Format timestamp back to string
            "power_shelly": shelly["power"],
            "power_hwmon": matched["power"],
            "session": matched["session"]
        })
    # If no match is found, do nothing (skip this Shelly data point)
    else:
        pass

# --- Write Fused Data to CSV ---
try:
    with open(FUSION_DATA, 'w', newline='') as f:
        # Define the column headers for the output CSV
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "power_shelly", "power_hwmon", "session"
        ])
        writer.writeheader()  # Write the header row
        writer.writerows(fused_data)  # Write all the fused data rows
    
    print(f"Data successfully fused and saved to {FUSION_DATA}")
    print(f"Total fused entries: {len(fused_data)}")

except IOError as e:
    print(f"Error writing to file {FUSION_DATA}: {e}")
except Exception as e:
    print(f"An unexpected error occurred while writing the fused data: {e}")