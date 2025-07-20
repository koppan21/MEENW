import os
import pandas as pd

RESULTS_FOLDER = "results"
FUSION_DATA = os.path.join(RESULTS_FOLDER, "power_log_corrected.csv")

def calculate_energy_consumption(file_path=FUSION_DATA, power_column='power_shelly'):
    """
    Calculates the total energy consumed per session from power data
    and the time difference between samples.

    Args:
        file_path (str): The path to the CSV file containing the data.
        power_column (str): The name of the column containing the power data
                            ('power_shelly' or 'power_hwmon').

    Returns:
        pd.DataFrame: A DataFrame with the total energy consumed (in Joules and Wh)
                      per session, or None if there's an error.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"File '{file_path}' loaded successfully.")
        print(f"Original columns: {df.columns.tolist()}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None

    required_columns = [power_column, 'session', 'timestamp']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in the DataFrame. Cannot calculate energy.")
            return None

    df[power_column] = pd.to_numeric(df[power_column], errors='coerce')

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        print(f"Error: Could not convert 'timestamp' column to datetime format: {e}")
        print("Ensure the 'timestamp' column is in a recognized format (e.g., ISO 8601, '%Y-%m-%d %H:%M:%S').")
        return None

    df.sort_values(by=['session', 'timestamp'], inplace=True)

    original_rows = len(df)
    df.dropna(subset=[power_column, 'session', 'timestamp'], inplace=True)
    rows_after_dropna = len(df)
    if original_rows != rows_after_dropna:
        print(f"Warning: {original_rows - rows_after_dropna} rows with critical NaN values were removed.")
    if rows_after_dropna == 0:
        print("Error: No valid data remaining after NaN cleaning. Cannot calculate energy.")
        return None

    df_filtered = df[df['session'] != 'Background'].copy()
    if df_filtered.empty:
        print("No valid sessions remaining for calculation after filtering 'Background'.")
        return None

    energy_results = []
    unique_sessions = df_filtered['session'].unique()
    print(f"\nCalculating energy for {len(unique_sessions)} sessions...")

    for session_name in unique_sessions:
        session_df = df_filtered[df_filtered['session'] == session_name].copy()
        session_df['time_delta'] = session_df['timestamp'].diff().dt.total_seconds()
        session_df['time_delta'] = session_df['time_delta'].bfill()
        session_df['time_delta'] = session_df['time_delta'].fillna(0)

        session_df['energy_joules'] = session_df[power_column] * session_df['time_delta']

        total_energy_joules = session_df['energy_joules'].sum()

        total_energy_wh = total_energy_joules / 3600
        total_energy_kwh = total_energy_wh / 1000

        energy_results.append({
            'Session': session_name,
            'Total Energy (Joules)': total_energy_joules,
            'Total Energy (Wh)': total_energy_wh,
            'Total Energy (kWh)': total_energy_kwh
        })

    if not energy_results:
        print("Could not calculate energy for any session.")
        return None

    energy_df = pd.DataFrame(energy_results)
    return energy_df


if __name__ == "__main__":
    energy_df_shelly = calculate_energy_consumption(FUSION_DATA, 'power_shelly')

    if energy_df_shelly is not None:
        print("\n--- Energy Consumption Summary per Session (using power_shelly) ---")
        print(energy_df_shelly.to_string(index=False))

        energy_output_csv = os.path.join(RESULTS_FOLDER, 'energy_consumption_shelly.csv')
        energy_df_shelly.to_csv(energy_output_csv, index=False)
        print(f"\nEnergy results saved to: {energy_output_csv}")