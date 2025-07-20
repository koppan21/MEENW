# power_logger_shelly.py

import requests
import time
import csv

# Replace with the actual IP address of your Shelly device
IP_SHELLY = "***.***.*.**"

OUTPUT_FILE = "power_log_shelly.csv" # Define the output CSV file name
INTERVAL = 1 # Define the interval between power readings in seconds

print("Starting power meter: Shelly")

def get_power():
    """
    Fetches power consumption data from the Shelly device.

    Returns:
        dict: A dictionary containing 'timestamp' and 'power' if successful,
              otherwise None.
    """
    # Construct the URL for the Shelly RPC API to get switch status (assuming ID 0)
    url = f"http://{IP_SHELLY}/rpc/Switch.GetStatus?id=0"
    try:
        # Send a GET request to the Shelly device with a 5-second timeout
        response = requests.get(url, timeout=5)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            # Return a dictionary with the current timestamp and the active power ('apower')
            return {
                "timestamp": time.strftime("%Y%m%dT%H:%M:%S"),
                "power": data.get("apower", 0.0) # Use .get() with a default to avoid KeyError
            }
        else:
            # Print an error if the status code is not 200
            print(f"Error while getting status: {response.status_code}")
            return None
    except requests.RequestException as e:
        # Catch any request-related errors (e.g., connection issues, timeouts)
        print(f"Connection error while getting status: {e}")
        return None

# Initialize the CSV file with headers
# 'mode="w"' ensures the file is created or overwritten, 'newline=""' handles line endings correctly
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "power"])

print("Starting power data capture...")
try:
    # Loop indefinitely to continuously capture power data
    while True:
        data = get_power() # Get power data from Shelly
        if data:
            # If data is successfully retrieved, append it to the CSV file
            with open(OUTPUT_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    data["timestamp"],
                    data["power"]
                ])
            print(f'Shelly: {data["power"]} W')

        time.sleep(INTERVAL) # Wait for the defined interval before the next reading
except KeyboardInterrupt:
    # Handle graceful exit when the user presses Ctrl+C
    print(f"\nStopping capture.")

print(f"Capture completed.")