import pandas as pd
import matplotlib.pyplot as plt
import re

file_path = "simulacion_imu.csv"
df = pd.read_csv(file_path, skiprows=1, encoding='utf-16')
df.columns = ['timestamp_us', 'raw_signal', 'filtered_signal']

# Drop empty rows
df = df.dropna()

# Extract float from string if it contains "Latencia", else just float it.
def extract_float(val):
    s = str(val).strip()
    if not s:
        return None
    # match the first number (could be negative or have decimal)
    match = re.match(r"([+-]?\d+(?:\.\d+)?)", s)
    return float(match.group(1)) if match else None

df['filtered_signal'] = df['filtered_signal'].apply(extract_float)
df['raw_signal'] = df['raw_signal'].apply(extract_float)
df['timestamp_us'] = df['timestamp_us'].apply(extract_float)

df = df.dropna()

df['time_ms'] = df['timestamp_us'] / 1000.0

plt.figure(figsize=(12, 6))
plt.plot(df['time_ms'], df['raw_signal'], color='#ff4d4d', alpha=0.6, linewidth=1.2, label='Señal Bruta IMU (Motores 9,000 RPM + Ruido)')
plt.plot(df['time_ms'], df['filtered_signal'], color='#00e676', linewidth=2.5, label='Señal Filtrada PureInertial (TZANiX Engine)')

plt.title('TZANiX Singularity: Cancelación de Vibración Mecánica en Dron', fontsize=14, fontweight='bold')
plt.xlabel('Tiempo (milisegundos)', fontsize=12)
plt.ylabel('Aceleración Z (m/s²)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right', fontsize=11)
plt.tight_layout()

plt.savefig("grafica_simulacion_imu.png", dpi=300)
print("✅ Gráfica generada exitosamente: grafica_simulacion_imu.png")
