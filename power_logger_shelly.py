# power_logger_shelly.py

import requests
import time
import csv

IP_SHELLY = "***.***.*.**" # Replace with yours

OUTPUT_FILE = "power_log_shelly.csv"
INTERVAL = 1

with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "power"])

print("Starting power meter: shelly")

def get_power():
    url = f"http://{IP_SHELLY}/rpc/Switch.GetStatus?id=0"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "timestamp": time.strftime("%Y%m%dT%H:%M:%S"),
                "power": data.get("apower", 0.0)
            }
        else:
            print(f"Error while getting status: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Connection error while getting status: {e}")
        return None

with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "power"])

print("Start test")
try:
    while True:
        data = get_power()
        if data:
            with open(OUTPUT_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    data["timestamp"],
                    data["power"]
                ])
            print(f'Shelly: {data["power"]} W')

        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print(f"Stopping capture")

print(f"\nCapture completed")
