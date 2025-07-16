import os
import pandas as pd

RESULTS_FOLDER = "results"
FUSION_DATA = "power_log_fusion.csv"

def calculate_energy_consumption(file_path=FUSION_DATA, power_column='power_shelly'):
    """
    Calcula la energía total consumida por cada sesión a partir de datos de potencia
    y la diferencia de tiempo entre muestras.

    Args:
        file_path (str): La ruta al archivo CSV que contiene los datos.
        power_column (str): El nombre de la columna que contiene los datos de potencia
                            ('power_shelly' o 'power_hwmon').

    Returns:
        pd.DataFrame: Un DataFrame con la energía total consumida (en Joules y Wh)
                      por cada sesión, o None si hay un error.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Archivo '{file_path}' cargado exitosamente.")
        print(f"Columnas originales: {df.columns.tolist()}")

    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no se encontró.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None

    required_columns = [power_column, 'session', 'timestamp']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: La columna requerida '{col}' no se encuentra en el DataFrame. No se puede calcular la energía.")
            return None

    df[power_column] = pd.to_numeric(df[power_column], errors='coerce')

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        print(f"Error: No se pudo convertir la columna 'timestamp' a formato datetime: {e}")
        print("Asegúrate de que la columna 'timestamp' esté en un formato reconocible (ej. ISO 8601, '%Y-%m-%d %H:%M:%S').")
        return None

    df.sort_values(by=['session', 'timestamp'], inplace=True)

    original_rows = len(df)
    df.dropna(subset=[power_column, 'session', 'timestamp'], inplace=True)
    rows_after_dropna = len(df)
    if original_rows != rows_after_dropna:
        print(f"Advertencia: Se eliminaron {original_rows - rows_after_dropna} filas con valores NaN críticos.")
    if rows_after_dropna == 0:
        print("Error: No quedan datos válidos después de la limpieza de NaN. No se puede calcular la energía.")
        return None

    df_filtered = df[df['session'] != 'Background'].copy()
    if df_filtered.empty:
        print("No quedan sesiones válidas para el cálculo después de filtrar 'Background'.")
        return None

    energy_results = []
    unique_sessions = df_filtered['session'].unique()
    print(f"\nCalculando energía para {len(unique_sessions)} sesiones...")

    for session_name in unique_sessions:
        session_df = df_filtered[df_filtered['session'] == session_name].copy()
        session_df['time_delta'] = session_df['timestamp'].diff().dt.total_seconds()
        session_df['time_delta'] = session_df['time_delta'].bfill()
        session_df['time_delta'] = session_df['time_delta'].fillna(0)

        session_df['energy_joules'] = session_df[power_column] * session_df['time_delta']

        total_energy_joules = session_df['energy_joules'].sum()

        total_energy_wh = total_energy_joules / 3600
        total_energy_kwh = total_energy_wh / 1000

        print(f"Sesión '{session_name}': {total_energy_joules:.2f} J, {total_energy_wh:.4f} Wh, {total_energy_kwh:.6f} kWh")

        energy_results.append({
            'Session': session_name,
            'Total Energy (Joules)': total_energy_joules,
            'Total Energy (Wh)': total_energy_wh,
            'Total Energy (kWh)': total_energy_kwh
        })

    if not energy_results:
        print("No se pudo calcular la energía para ninguna sesión.")
        return None

    energy_df = pd.DataFrame(energy_results)
    return energy_df


if __name__ == "__main__":
    energy_df_shelly = calculate_energy_consumption(FUSION_DATA, 'power_shelly')

    if energy_df_shelly is not None:
        print("\n--- Resumen de Energía Consumida por Sesión (usando power_shelly) ---")
        print(energy_df_shelly.to_string(index=False))

        energy_output_csv = os.path.join(RESULTS_FOLDER, 'energy_consumption_shelly.csv')
        energy_df_shelly.to_csv(energy_output_csv, index=False)
        print(f"\nResultados de energía guardados en: {energy_output_csv}")
        