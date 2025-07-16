import os
import pandas as pd
import matplotlib.pyplot as plt

csv_data = os.path.join("results", "energy_consumption_shelly.csv")

df = pd.read_csv(csv_data)

df_sorted = df.sort_values(by='Total Energy (Wh)', ascending=False)

plt.figure(figsize=(12, 8))
plt.bar(df_sorted['Session'], df_sorted['Total Energy (Wh)'], color='skyblue')
plt.xlabel('Sesión')
plt.ylabel('Energía Total (Wh)')
plt.title('Energía Total por Sesión (Wh)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
filename = os.path.join("results", 'total_energy_wh_bar_chart.png')
plt.savefig(filename, format='png')

print("Se ha generado la gráfica 'total_energy_wh_bar_chart.png'.")