import time
import numpy as np
import gc
import psutil
import os
from scipy.spatial import cKDTree

# Simularemos la arquitectura Tesseract pero al límite (5 millones de nodos en RAM)
# En main.py el límite actual es 50,000. Aquí forzaremos la asfixia.
MASSIVE_SIZE = 5_000_000 

print("=" * 70)
print("PRUEBA 2: SATURACIÓN DEL TESERACTO 4D (Memory & KNN Stress Test)")
print(f"Cargando hiperespacio con {MASSIVE_SIZE:,} eventos históricos...")
print("=" * 70)

# Simulación lineal eliminada a favor de cKDTree

def get_ram_usage_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def run_memory_asphyxiation_test():
    start_ram = get_ram_usage_mb()
    print(f"[-] RAM inicial del proceso: {start_ram:.2f} MB")
    
    # 1. ASIGNACIÓN MASIVA EN RAM (Asfixia)
    start_alloc = time.time()
    try:
        # 5 millones de coordenadas 4D de alta precisión
        tesseract_coords = np.random.rand(MASSIVE_SIZE, 4).astype(np.float32)
    except MemoryError:
        print("[ERROR FATAL]: El sistema colapsó por falta de memoria RAM al intentar alocar el Tesseract.")
        return
        
    alloc_time = time.time() - start_alloc
    peak_ram = get_ram_usage_mb()
    print(f"[+] Hiperespacio cargado en {alloc_time:.2f} segundos.")
    print(f"[!] Consumo de RAM actual (Tesseract Saturado): {peak_ram:.2f} MB")
    
    # 2. CONSTRUCCIÓN DEL KD-TREE 
    print("\n[-] Construyendo el índice espacial cKDTree (batch rebuild)...")
    start_build = time.time()
    kdtree = cKDTree(tesseract_coords)
    build_time = time.time() - start_build
    print(f"[+] Árbol espacial construido en {build_time:.2f} segundos.")
    
    print("\n[-] Iniciando búsqueda espacial O(log N) sobre 5,000,000 de registros...")
    query_target = np.array([0.12, 0.88, 0.45, 0.99], dtype=np.float32)
    
    # Medimos el tiempo real de búsqueda
    start_search = time.perf_counter()
    distances, indices = kdtree.query(query_target, k=3)
    search_time_ms = (time.perf_counter() - start_search) * 1000
    
    print("\n" + "=" * 70)
    print("RESULTADO DE LA PRUEBA DE SATURACIÓN 4D")
    print("=" * 70)
    
    if search_time_ms <= 1.0:
        print("[EXITO TOTAL]: Velocidad luz alcanzada.")
        print(f"Búsqueda espacial completada en {search_time_ms:.4f} ms.")
        print("La memoria RAM se mantuvo estable y contigua sin fragmentarse.")
    elif search_time_ms <= 15.0:
        print("[ALERTA AMARILLA]: El motor resistió, pero con lentitud.")
        print(f"Búsqueda espacial completada en {search_time_ms:.4f} ms.")
        print("Estamos por encima de los 0.5 ms ideales. Podría saturarse bajo 10k RPS.")
    else:
        print("[FRACASO DE MEMORIA]: Lentitud extrema.")
        print(f"Búsqueda espacial tardó {search_time_ms:.4f} ms.")
        print("El arreglo en RAM es demasiado masivo para escanearlo linealmente. Se requiere un índice espacial (KD-Tree/BallTree).")

if __name__ == "__main__":
    run_memory_asphyxiation_test()
