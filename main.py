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

# main.py

import subprocess
import time
import sys
import os

# List of webs to analyze
WEBS_JSON_FILE = "webs.json" # Modify with yours

# Necessary scripts
# Logger scripts
SHELLY_SCRIPT = "power_logger_shelly.py"
HWMON_SCRIPT = "power_logger_hwmon.py"

# Data processing scripts
FUSION_SCRIPT = "power_fusion.py"
CORRECTION_SCRIPT = "power_correction.py"
ENERGY_SCRIPT = "obtain_energy.py"
PERCENT_SCRIPT = "obtain_percent.py"

# Generate graphs scripts
ENERGY_GRAPH = "graph_energy.py"
PERIOD_GRAPHS = "graph_period.py"


RESULTS_FOLDER = "results"
POST_HWMON_DELAY = 10


def run_shelly_logger():
    """Starts the Shelly power logger in a non-blocking way."""
    print(f"Starting {SHELLY_SCRIPT}...")
    return subprocess.Popen(["python3", SHELLY_SCRIPT])

def run_hwmon_logger():
    """Runs the hwmon power logger and waits for it to complete."""
    print(f"Starting {HWMON_SCRIPT}...")
    result = subprocess.run(["python3", HWMON_SCRIPT, WEBS_JSON_FILE])
    if result.returncode != 0:
        print(f"Error: {HWMON_SCRIPT} exited with code {result.returncode}")
    print(f"{HWMON_SCRIPT} finished.")

def terminate_process(process):
    """Terminates a subprocess."""
    if process and process.poll() is None:
        print(f"Terminating process {process.pid}...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"Process {process.pid} did not terminate gracefully, killing...")
            process.kill()
    else:
        print(f"Process {process.pid} already finished or not started.")
        
def run_final_scripts():
    """Runs all the post-processing scripts sequentially."""
    if not os.path.exists(RESULTS_FOLDER):
        print(f"Creating directory: {RESULTS_FOLDER}")
        os.makedirs(RESULTS_FOLDER)
    else:
        print(f"Directory '{RESULTS_FOLDER}' already exists.")
        
    scripts_to_run = [
        FUSION_SCRIPT,
        CORRECTION_SCRIPT,
        ENERGY_SCRIPT,
        PERCENT_SCRIPT,
        ENERGY_GRAPH,
        PERIOD_GRAPHS
    ]

    print("\nStarting post-processing scripts...")
    for script in scripts_to_run:
        print(f"Running {script}...")
        result = subprocess.run(["python3", script])
        if result.returncode != 0:
            print(f"Error: {script} exited with code {result.returncode}")
        else:
            print(f"{script} finished successfully.")
        time.sleep(5)
    print("All post-processing scripts completed.")



if __name__ == "__main__":
    shelly_process = None
    try:
        # 1. Start Shelly logger and wait
        shelly_process = run_shelly_logger()
        time.sleep(5)

        # 2. Run Hwmon logger and wait for it to finish
        run_hwmon_logger()

        # 3. Wait
        time.sleep(POST_HWMON_DELAY)

    except FileNotFoundError:
        print("Error: Ensure 'python3' and the logger scripts are in your PATH or specified correctly.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 4. Stop Shelly logger
        terminate_process(shelly_process)
        print("All power logging completed.")
        # 5. Run the final scripts
        run_final_scripts()