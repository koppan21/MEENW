# Measuring Energy Efficiency in Web Browsing

This repository contains a suite of Python scripts designed to measure, fuse, correct, analyze, and visualize power consumption data from different sources (Shelly device and `hwmon` system sensor) during various Browse sessions.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Scripts Overview](#scripts-overview)
- [Configuration](#configuration)
- [Results](#results)

## Features

* **Dual Power Source Logging**: Capture power consumption from a Shelly device and a system's `hwmon` sensor simultaneously.
* **Automated Browse Sessions**: `power_logger_hwmon.py` automates opening specified websites in Firefox to measure power during web Browse.
* **Data Fusion**: Merge power logs from different sources based on timestamps for unified analysis.
* **Background Power Correction**: Correct raw power data by subtracting a calculated background power mean to isolate active consumption.
* **Energy Calculation**: Compute total energy consumed (Joules, Wh, kWh) for each session.
* **Percentage Analysis**: Calculate the percentage of `hwmon` power relative to Shelly power.
* **Data Visualization**: Generate various plots, including:
    * Bar charts of total energy consumption per session.
    * Time-series plots comparing Shelly and `hwmon` power over specific intervals for different sessions.

## Project Structure

```
.
├── results/
│   ├── energy_consumption_shelly.csv
│   ├── mean.csv
│   ├── percentage.csv
│   ├── power_log_corrected.csv
│   └── graph_shelly_all_samples.png
    ├── graph_hwmon_all_samples.png
│   └── total_energy_wh_bar_chart.png
├── power_log_hwmon.csv
├── power_log_shelly.csv
├── power_log_fusion.csv
├── obtain_energy.py
├── obtain_percent.py
├── power_correction.py
├── power_fusion.py
├── power_logger_hwmon.py
├── power_logger_shelly.py
├── graph_energy.py
├── graph_period.py
├── main.py
├── requirements.txt
└── webs.json
```

## Getting Started

### Prerequisites

* Linux PC
* Python 3.x
* Firefox web browser
* `xdotool` (for controlling Firefox tabs in `power_logger_hwmon.py` - typically available on Linux)
* A Shelly device with power monitoring capabilities (e.g., Shelly Plug S) configured on your local network.
* An `hwmon` sensor configured and accessible on your system (e.g., `fam15h_power` for AMD CPUs).

### Installation

1.  Clone this repository:
    ```bash
    git clone [https://github.com/your_username/your_repository_name.git](https://github.com/your_username/your_repository_name.git)
    cd your_repository_name
    ```
2.  Install the required Python libraries using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the entire power consumption measurement and analysis pipeline, simply execute the `main.py` script. This script will orchestrate the execution of all other scripts in the necessary order:

```bash
python3 main.py
```

**Note:** Ensure that your Shelly device's IP address is correctly configured in `power_logger_shelly.py` and that the *POWER_SENSOR_NAME* in `power_logger_hwmon.py` matches your system's hwmon sensor. The `power_logger_hwmon.py` script will open Firefox tabs based on the `webs.json` file. You will need to keep the terminal running for the duration of the logging process.

## Scripts Overview

* **main.py:** Orchestrates the execution of all other scripts in the correct order.
* **power_logger_shelly.py:** Logs real-time power consumption from a Shelly device.
* **power_logger_hwmon.py:** Logs system power consumption via hwmon during automated Browse sessions.
* **power_fusion.py:** Merges power_log_shelly.csv and power_log_hwmon.csv into power_log_fusion.csv.
* **power_correction.py:** Corrects power data in power_log_fusion.csv by subtracting background power means, saving to power_log_corrected.csv.
* **obtain_energy.py:** Calculates and reports total energy consumed per session from power_log_fusion.csv.
* **obtain_percent.py:** Calculates the percentage of hwmon power relative to Shelly power per session.
* **graph_energy.py:** Generates a bar chart showing total energy consumed per session.
* **graph_period.py:** Creates comparative time-series plots of Shelly and hwmon power over time.
* **webs.json:** Defines the list of websites used by power_logger_hwmon.py for automated Browse.

## Configuration

* **power_logger_shelly.py:**
  * *IP_SHELLY:* Replace with your Shelly device's IP address.
  * *INTERVAL:* Sampling interval in seconds.
* **power_logger_hwmon.py:**
  * *POWER_SENSOR_NAME:* Your specific hwmon power sensor name (e.g., "fam15h_power").
  * *INTERVAL:* Sampling interval in seconds.
  * *DURATION:* Duration of each session in seconds.
  * *PAUSE:* Pause between sessions in seconds.
* **webs.json:** Modify this file to include different websites for power_logger_hwmon.py to visit.

## Results
The results/ directory will contain the following files after running all scripts:
* *power_log_fusion.csv:* Fused power data from Shelly and Hwmon with session information.
* *power_log_corrected.csv:* Fused power data corrected by subtracting background power.
* *mean.csv:* Mean background power values for Shelly and Hwmon.
* *energy_consumption_shelly.csv:* Total energy consumed per session (in Joules, Wh, kWh) based on Shelly data.
* *percentage.csv:* Average percentage of Hwmon power relative to Shelly power per session.
* *graph_shelly_all_samples.png:* Plot of Shelly power showing all samples for non-background sessions.
* *graph_hwmon_all_samples.png:* Plot of Hwmon power showing all samples for non-background sessions.
* *total_energy_wh_bar_chart.png:* Bar chart summarizing total energy (Wh) per session.