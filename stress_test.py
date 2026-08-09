import time
import requests
import numpy as np
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"  # Clave válida configurada en la BD

def generate_stressed_signal(length=50):
    # Base: Señal senoidal pura
    t = np.linspace(0, 2 * np.pi, length)
    base = np.sin(t)
    
    # Ruido extremo: Ruido Gaussiano de alta amplitud
    noise = np.random.normal(0, 1.5, length)
    
    # Anomalía masiva: Spikes aleatorios destructivos (picos de 10x)
    spikes = np.zeros(length)
    for _ in range(3):
        idx = random.randint(0, length - 1)
        spikes[idx] = random.choice([-8.0, 8.0])
        
    stressed_signal = base + noise + spikes
    return stressed_signal.tolist()

def send_request(request_id):
    payload = {
        "data_stream_id": "STRESS-TEST-FEED",
        "stream_type": "industrial",
        "sequences": generate_stressed_signal()
    }
    headers = {"X-IFA-Key": API_KEY}
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        latency = (time.time() - start_time) * 1000  # En milisegundos
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "latency_ms": latency,
                "gain": data.get("compute_efficiency_gain", 0),
                "morton": data.get("spatial_signature_4d"),
                "knn_count": len(data.get("knn_neighbors", []))
            }
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_stress_test(num_requests=100, max_workers=5):
    print("=================================================================")
    print("TZANiX STRESS TEST - EJECUTANDO SIMULACIÓN DE ALTA CARGA")
    print("=================================================================")
    print(f"Iniciando {num_requests} peticiones concurrentes con {max_workers} hilos...")
    
    latencies = []
    gains = []
    success_count = 0
    failure_count = 0
    errors = []
    
    start_test = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_request, i) for i in range(num_requests)]
        
        for future in as_completed(futures):
            res = future.result()
            if res["success"]:
                success_count += 1
                latencies.append(res["latency_ms"])
                gains.append(res["gain"])
            else:
                failure_count += 1
                errors.append(res.get("error"))
                
    total_duration = time.time() - start_test
    
    # Cálculos estadísticos
    mean_latency = np.mean(latencies) if latencies else 0
    p95_latency = np.percentile(latencies, 95) if latencies else 0
    p99_latency = np.percentile(latencies, 99) if latencies else 0
    mean_gain = np.mean(gains) if gains else 0
    
    print("\n=================================================================")
    print("RESULTADOS DE LA PRUEBA DE ESTRÉS")
    print("=================================================================")
    print(f"Peticiones Exitosas: {success_count} / {num_requests} ({success_count/num_requests*100:.1f}%)")
    print(f"Peticiones Fallidas: {failure_count}")
    if errors:
        print(f"Errores Únicos: {set(errors)}")
    print(f"Duración Total del Test: {total_duration:.2f} segundos")
    print(f"Tasa de Procesamiento: {success_count / total_duration:.1f} req/seg")
    print(f"Latencia Promedio: {mean_latency:.2f} ms")
    print(f"Latencia Percentil 95 (p95): {p95_latency:.2f} ms")
    print(f"Latencia Percentil 99 (p99): {p99_latency:.2f} ms")
    print(f"Atenuación Promedio de Ruido: {mean_gain:.2f}%")
    print("=================================================================")
    
    # Escribir informe crudo temporal para análisis
    with open("stress_results.txt", "w") as f:
        f.write(f"success_count={success_count}\n")
        f.write(f"failure_count={failure_count}\n")
        f.write(f"total_duration={total_duration:.4f}\n")
        f.write(f"mean_latency={mean_latency:.4f}\n")
        f.write(f"p95_latency={p95_latency:.4f}\n")
        f.write(f"p99_latency={p99_latency:.4f}\n")
        f.write(f"mean_gain={mean_gain:.4f}\n")

if __name__ == "__main__":
    run_stress_test(150, 8)
