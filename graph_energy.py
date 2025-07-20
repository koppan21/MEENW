import os
import pandas as pd
import matplotlib.pyplot as plt

csv_data = os.path.join("results", "energy_consumption_shelly.csv")

try:
    df = pd.read_csv(csv_data)

    # Sort the DataFrame by 'Total Energy (Wh)' in descending order
    df_sorted = df.sort_values(by='Total Energy (Wh)', ascending=False)

    plt.figure(figsize=(12, 8))
    plt.bar(df_sorted['Session'], df_sorted['Total Energy (Wh)'], color='skyblue')
    plt.xlabel('Session')
    plt.ylabel('Total Energy (Wh)')
    plt.title('Total Energy per Session (Wh)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    filename = os.path.join("results", 'total_energy_wh_bar_chart.png')
    plt.savefig(filename, format='png')

    print("The graph 'total_energy_wh_bar_chart.png' has been generated.")

except FileNotFoundError:
    print(f"Error: The file '{csv_data}' was not found. Please ensure the file exists in the specified path.")
except Exception as e:
    print(f"An error occurred: {e}")