import os.path
import pandas as pd
import matplotlib.pyplot as plt

DATA_FOLDER = "results"
FUSION_DATA = "power_log_fusion.csv"

def plot_separated_power_comparison(file_path=FUSION_DATA):
    """
    Generates separate comparative plots for 'power_shelly' and 'power_hwmon' for all sessions,
    excluding the 'Background' session, and plotting the total available samples for each.

    One plot is generated for 'power_shelly' and one for 'power_hwmon',
    where all non-Background sessions are overlaid for each power metric,
    showing all their data points.
    The 'session' column is treated as a string name.

    Args:
        file_path (str): The path to the CSV file (defaults to "power_log_fusion.csv").
    """
    try:
        df = pd.read_csv(file_path)
        print(f"File '{file_path}' loaded successfully.")
        print(f"Original columns: {df.columns.tolist()}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    required_columns = ['power_shelly', 'power_hwmon', 'session']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in the DataFrame. Ensure the CSV contains it or that renaming is correct.")
            return

    df['power_shelly'] = pd.to_numeric(df['power_shelly'], errors='coerce')
    df['power_hwmon'] = pd.to_numeric(df['power_hwmon'], errors='coerce')

    original_rows = len(df)
    df.dropna(subset=['power_shelly', 'power_hwmon', 'session'], inplace=True)
    rows_after_dropna = len(df)
    print(f"Original rows: {original_rows}, Rows after NaN cleaning: {rows_after_dropna}")
    if rows_after_dropna == 0:
        print("Error: No valid data remaining after NaN cleaning. Cannot generate plots.")
        return

    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values(by=['session', 'timestamp'], inplace=True)
            print("Sorting by session and timestamp.")
        except Exception:
            print("Warning: Could not convert 'timestamp' to datetime. Sorting by session and order of appearance.")
            df.sort_values(by=['session'], inplace=True)
    else:
        df.sort_values(by=['session'], inplace=True)
        print("Warning: 'timestamp' column not found. Sorting only by session and order of appearance.")

    df_filtered = df[df['session'] != 'Background'].copy()
    if df_filtered.empty:
        print("No non-Background sessions found after filtering. Cannot generate plots.")
        return

    unique_sessions = df_filtered['session'].unique() # Use the filtered DataFrame for unique sessions
    if len(unique_sessions) == 0:
        print("Error: No unique sessions (excluding 'Background') found in the data. Cannot generate plots.")
        return
    unique_sessions_sorted = sorted(unique_sessions.tolist())
    print(f"Unique sessions found (excluding 'Background', sorted): {unique_sessions_sorted}")

    # --- Plotting for Power Shelly (All Samples) ---
    print("\n--- Generating plot for Power Shelly (All Samples) ---")
    plt.figure(figsize=(20, 10))

    plt.title('Power Shelly evolution over time per Session', fontsize=16)
    plt.xlabel('Sample Number', fontsize=12)
    plt.ylabel('Shelly Power (W)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.7)

    plotted_any_line_shelly = False

    for session_name in unique_sessions_sorted:
        session_subset = df_filtered[df_filtered['session'] == session_name].reset_index(drop=True)

        if not session_subset.empty:
            plotted_any_line_shelly = True
            print(f"Plotting Shelly for Session '{session_name}', all samples ({len(session_subset)}).")
            plt.plot(session_subset.index, session_subset['power_shelly'],
                     label=f'{session_name}', alpha=0.7)
        else:
            print(f"Warning: No Shelly data for Session '{session_name}'. Skipping plot.")

    if plotted_any_line_shelly:
        plt.legend(title='Session', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8, ncol=1)
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        filename = os.path.join(DATA_FOLDER, "graph_shelly_all_samples.png")
        plt.savefig(filename, bbox_inches='tight')
        plt.show()
    else:
        print(f"No Shelly lines were plotted. No legend or plot will be shown.")
        plt.close()

    # --- Plotting for Power Hwmon (All Samples) ---
    print("\n--- Generating plot for Power Hwmon (All Samples) ---")
    plt.figure(figsize=(20, 10))

    plt.title('Power Hwmon evolution over time per Session', fontsize=16)
    plt.xlabel('Sample Number', fontsize=12)
    plt.ylabel('Hwmon Power (W)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.7)

    plotted_any_line_hwmon = False

    for session_name in unique_sessions_sorted:
        session_subset = df_filtered[df_filtered['session'] == session_name].reset_index(drop=True)

        if not session_subset.empty:
            plotted_any_line_hwmon = True
            print(f"Plotting Hwmon for Session '{session_name}', all samples ({len(session_subset)}).")
            plt.plot(session_subset.index, session_subset['power_hwmon'],
                     label=f'{session_name}', alpha=0.7)
        else:
            print(f"Warning: No Hwmon data for Session '{session_name}'. Skipping plot.")

    if plotted_any_line_hwmon:
        plt.legend(title='Session', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8, ncol=1)
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        filename = os.path.join(DATA_FOLDER, "graph_hwmon_all_samples.png")
        plt.savefig(filename, bbox_inches='tight')
        plt.show()
    else:
        print(f"No Hwmon lines were plotted. No legend or plot will be shown.")
        plt.close()


if __name__ == "__main__":
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"Folder '{DATA_FOLDER}' created.")

    plot_separated_power_comparison(FUSION_DATA)