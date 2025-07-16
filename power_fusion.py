import csv
from datetime import datetime, timedelta

HWMON_DATA = "power_log_hwmon.csv"
SHELLY_DATA = "power_log_shelly.csv"
FUSION_DATA = "power_log_fusion.csv"

# Parse timestamp
def parse_ts(ts):
    return datetime.strptime(ts, "%Y%m%dT%H:%M:%S")

# hwmon
system_data = []

with open(HWMON_DATA, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            timestamp = parse_ts(row["timestamp"])
            power = float(row["power"])
            session = row["session"]
            system_data.append({"timestamp": timestamp, "power": power, "session": session})
        except:
            continue

# Shelly
shelly_data = []
with open(SHELLY_DATA, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            timestamp = parse_ts(row["timestamp"])
            power = float(row["power"])
            shelly_data.append({"timestamp": timestamp, "power": power})
        except:
            continue

# Fusion
fused_data = []

for shelly in shelly_data:
    matched = None
    for sys in system_data:
        delta = abs(shelly["timestamp"] - sys["timestamp"])
        if delta <= timedelta(seconds=1):
            matched = sys
            break
    if matched:
        fused_data.append({
            "timestamp": shelly["timestamp"].strftime("%Y%m%dT%H:%M:%S"),
            "power_shelly": shelly["power"],
            "power_hwmon": matched["power"],
            "session": matched["session"]
        })
    else:
        pass


with open(FUSION_DATA, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "timestamp", "power_shelly", "power_hwmon", "session"
    ])
    writer.writeheader()
    writer.writerows(fused_data)
