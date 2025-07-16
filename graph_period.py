import os.path
import pandas as pd
import matplotlib.pyplot as plt

DATA_FOLDER = "results"
FUSION_DATA = "power_log_fusion.csv"

def plot_separated_power_comparison(file_path=FUSION_DATA):
    """
    Genera gráficas comparativas separadas para 'power_shelly' y 'power_hwmon' para todas las sesiones.

    Se generan tres gráficas para 'power_shelly' y tres para 'power_hwmon',
    una para cada intervalo de muestras (60, 240, 600),
    donde todas las sesiones se superponen para cada métrica de potencia.
    La columna 'session' se trata como un nombre (cadena de texto).

    Args:
        file_path (str): La ruta al archivo CSV (por defecto "power_log_fusion.csv").
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Archivo '{file_path}' cargado exitosamente.")
        print(f"Columnas originales: {df.columns.tolist()}")

    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no se encontró.")
        return
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    required_columns = ['power_shelly', 'power_hwmon', 'session']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: La columna requerida '{col}' no se encuentra en el DataFrame. Asegúrate de que el CSV la contenga o de que el renombrado sea correcto.")
            return

    df['power_shelly'] = pd.to_numeric(df['power_shelly'], errors='coerce')
    df['power_hwmon'] = pd.to_numeric(df['power_hwmon'], errors='coerce')

    original_rows = len(df)
    df.dropna(subset=['power_shelly', 'power_hwmon', 'session'], inplace=True)
    rows_after_dropna = len(df)
    print(f"Filas originales: {original_rows}, Filas después de limpiar NaN: {rows_after_dropna}")
    if rows_after_dropna == 0:
        print("Error: No quedan datos válidos después de la limpieza de NaN. No se pueden generar gráficas.")
        return

    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.sort_values(by=['session', 'timestamp'], inplace=True)
            print("Ordenando por sesión y timestamp.")
        except Exception:
            print("Advertencia: No se pudo convertir 'timestamp' a datetime. Ordenando por sesión y orden de aparición.")
            df.sort_values(by=['session'], inplace=True)
    else:
        df.sort_values(by=['session'], inplace=True)
        print("Advertencia: No se encontró la columna 'timestamp'. Ordenando solo por sesión y orden de aparición.")

    unique_sessions = df['session'].unique()
    if len(unique_sessions) == 0:
        print("Error: No se encontraron sesiones únicas en los datos. No se pueden generar gráficas.")
        return
    unique_sessions_sorted = sorted(unique_sessions.tolist())
    print(f"Sesiones únicas encontradas (ordenadas): {unique_sessions_sorted}")

    sample_intervals = [60, 120, 240]

    # shelly
    print("\n--- Generando gráficas para Power Shelly ---")
    for interval in sample_intervals:
        plt.figure(figsize=(20, 10))

        plt.title(f'Power Shelly por Sesión (Intervalo: {interval} muestras)', fontsize=16)
        plt.xlabel('Número de Muestra', fontsize=12)
        plt.ylabel('Potencia Shelly (W)', fontsize=12)
        plt.grid(True, linestyle=':', alpha=0.7)

        plotted_any_line = False

        for session_name in unique_sessions_sorted:
            session_df_filtered = df[df['session'] == session_name]
            session_subset = session_df_filtered.head(interval).reset_index(drop=True)

            if not session_subset.empty:
                plotted_any_line = True
                print(f"Graficando Shelly para Sesión '{session_name}', Intervalo {interval}: {len(session_subset)} muestras.")
                plt.plot(session_subset.index, session_subset['power_shelly'],
                         label=f'Sesión {session_name}', alpha=0.7)
            else:
                print(f"Advertencia: No hay suficientes datos para Shelly en Sesión '{session_name}' para el Intervalo {interval}. Saltando graficación.")

        if plotted_any_line:
            plt.legend(title='Sesión', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8, ncol=1)
            plt.tight_layout(rect=[0, 0, 0.85, 1])
            filename = os.path.join(DATA_FOLDER, f"graph_shelly_ranking_period_{interval}.png")
            plt.savefig(filename, bbox_inches='tight')
            plt.show()
        else:
            print(f"No se graficaron líneas de Shelly para el Intervalo {interval}. No se mostrará la leyenda ni la gráfica.")
            plt.close()

    # hwmon
    print("\n--- Generando gráficas para Power Hwmon ---")
    for interval in sample_intervals:
        plt.figure(figsize=(20, 10))

        plt.title(f'Power Hwmon por Sesión (Intervalo: {interval} muestras)', fontsize=16)
        plt.xlabel('Número de Muestra', fontsize=12)
        plt.ylabel('Potencia Hwmon (W)', fontsize=12)
        plt.grid(True, linestyle=':', alpha=0.7)

        plotted_any_line = False

        for session_name in unique_sessions_sorted:
            session_df_filtered = df[df['session'] == session_name]
            session_subset = session_df_filtered.head(interval).reset_index(drop=True)

            if not session_subset.empty:
                plotted_any_line = True
                print(f"Graficando Hwmon para Sesión '{session_name}', Intervalo {interval}: {len(session_subset)} muestras.")
                plt.plot(session_subset.index, session_subset['power_hwmon'],
                         label=f'Sesión {session_name}', alpha=0.7)
            else:
                print(f"Advertencia: No hay suficientes datos para Hwmon en Sesión '{session_name}' para el Intervalo {interval}. Saltando graficación.")

        if plotted_any_line:
            plt.legend(title='Sesión', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8, ncol=1)
            plt.tight_layout(rect=[0, 0, 0.85, 1])
            filename = os.path.join(DATA_FOLDER, f"graph_hwmon_ranking_period_{interval}.png")
            plt.savefig(filename, bbox_inches='tight')
            plt.show()
        else:
            print(f"No se graficaron líneas de Hwmon para el Intervalo {interval}. No se mostrará la leyenda ni la gráfica.")
            plt.close()


if __name__ == "__main__":
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"Carpeta '{DATA_FOLDER}' creada.")

    plot_separated_power_comparison(FUSION_DATA)