# power_logger_hwmon.py

import sys
import time
import json
import csv
import subprocess
import glob

POWER_SENSOR_NAME = "fam15h_power" # Replace with yours

OUTPUT_FILE = "power_log_hwmon.csv"
INTERVAL = 1
DURATION = 60
PAUSE = 10

if len(sys.argv) > 2:
    print("Uso: python3 power_logger_hwmon.py <webs.json>")
    sys.exit()

webs_json = sys.argv[1]

def get_power_field():
    hwmon_paths = glob.glob("/sys/class/hwmon/hwmon*/name")
    for path in hwmon_paths:
        with open(path, "r") as f:
            if POWER_SENSOR_NAME in f.read().strip():
                return path.replace("name", "power1_input")
    return None

POWER_FIELD = get_power_field()

if POWER_FIELD is None:
    print(f'Error: El archivo de consumo de potencia no existe en el sistema.')
    exit(1)

print("Starting power meter: hwmon")

with open(webs_json) as file:
    URLS = json.load(file)

with open(OUTPUT_FILE, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "power", "session"])

def save_power(session):
    start_time = time.time()
    try:
        while time.time() - start_time < DURATION:
            with open(POWER_FIELD, 'r') as file:
                power = int(file.read().strip()) / 1_000_000

            timestamp = time.strftime("%Y%m%dT%H:%M:%S")

            with open(OUTPUT_FILE, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, power, session])

            print(f'Hwmon: {power:.2f} W')
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print('\nStopping capture...')

print("\n Background")
save_power("Background")
time.sleep(PAUSE)

print("\n BlankTab")
subprocess.Popen(["firefox", "--new-window", "about:blank"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(DURATION)
save_power("BlankTab")
time.sleep(PAUSE)

for name, url in URLS.items():
    print(f'\nSession: {name}\n')
    subprocess.run(["firefox", "--new-tab", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    save_power(name)
    subprocess.run(["xdotool", "key", "Ctrl+w"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(PAUSE)

subprocess.run(["pkill", "-f", "firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"\nCapture completed")
