# Copyright (C) 2025 Sandra Nicole Solórzano Carcelén sandranicole2001@hotmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# power_logger_hwmon.py

import sys
import time
import json
import csv
import subprocess
import glob

# Define the name of your power sensor as found in /sys/class/hwmon/hwmon*/name
POWER_SENSOR_NAME = "fam15h_power" 

# Define output file and timing parameters
OUTPUT_FILE = "power_log_hwmon.csv"
INTERVAL = 1  # Time interval between power readings in seconds
DURATION = 60 # Duration for each session's power capture in seconds
PAUSE = 10    # Pause between sessions in seconds

# Command-line argument check
if len(sys.argv) > 2:
    print("Usage: python3 power_logger_hwmon.py <webs.json>")
    sys.exit(1) # Exit with an error code

# Get the path to the webs.json file from command-line arguments
webs_json = sys.argv[1]

def get_power_field():
    """
    Finds the sysfs path for the power input of the specified HWMON sensor.
    """
    # Search for hwmon devices and their names
    hwmon_paths = glob.glob("/sys/class/hwmon/hwmon*/name")
    for path in hwmon_paths:
        with open(path, "r") as f:
            if POWER_SENSOR_NAME in f.read().strip():
                return path.replace("name", "power1_input")
    return None # Return None if the sensor is not found

# Get the specific power field path for the sensor
POWER_FIELD = get_power_field()

# Exit if the power sensor file is not found
if POWER_FIELD is None:
    print(f'Error: The power consumption file does not exist on the system.')
    exit(1) # Exit with an error code

print("Starting power meter: hwmon")

# Load URLs from the provided JSON file
try:
    with open(webs_json) as file:
        URLS = json.load(file)
except FileNotFoundError:
    print(f"Error: The file '{webs_json}' was not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{webs_json}'. Please check the file format.")
    sys.exit(1)

# Initialize the CSV output file with headers
with open(OUTPUT_FILE, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "power", "session"])

def save_power(session):
    """
    Captures power readings for a specified duration and saves them to the output CSV.
    """
    start_time = time.time()
    try:
        while time.time() - start_time < DURATION:
            with open(POWER_FIELD, 'r') as file:
                # Read power, convert to integer, and then to Watts (from microWatts)
                power = int(file.read().strip()) / 1_000_000 

            # Get current timestamp in the specified format
            timestamp = time.strftime("%Y%m%dT%H:%M:%S")

            # Append the data to the CSV file
            with open(OUTPUT_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, power, session])

            print(f'Hwmon: {power:.2f} W') # Print current power reading
            time.sleep(INTERVAL) # Wait for the next reading
    except KeyboardInterrupt:
        print('\nStopping capture...') # Handle manual interruption
    except FileNotFoundError:
        print(f"Error: Power sensor file '{POWER_FIELD}' not found during capture. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during power capture: {e}")
        sys.exit(1)

# --- Start Power Logging Sessions ---

# Background session
print("\nBackground session starting...")
save_power("Background")
time.sleep(PAUSE) # Pause after session

# BlankTab session (open a blank Firefox tab)
print("\nBlankTab session starting...")
# Open Firefox with a new window and blank tab, redirecting stdout/stderr to DEVNULL
subprocess.Popen(["firefox", "--new-window", "about:blank"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(DURATION) # Let Firefox load and stabilize

# Iterate through defined URLs and capture power
for name, url in URLS.items():
    print(f'\nSession: {name} ({url})\n')
    # Open URL in a new Firefox tab
    subprocess.run(["firefox", "--new-tab", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    save_power(name) # Capture power for this session
    # Close the current tab using xdotool
    subprocess.run(["xdotool", "key", "Ctrl+w"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(PAUSE) # Pause after session

# Kill all Firefox processes after all sessions are complete
subprocess.run(["pkill", "-f", "firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"\nCapture completed. Data saved to {OUTPUT_FILE}")