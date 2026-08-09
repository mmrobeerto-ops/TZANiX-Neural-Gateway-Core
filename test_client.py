import time
import random
import math
import requests

# Configuración de infraestructura local Fourier IFA
API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"  # Llave activa asignada a Neural_Node

def generate_noisy_ai_stream(length=50):
    """
    Simula una señal sinusoidal pura de baja frecuencia (inferencia de IA)
    mezclada con ruido aleatorio agudo de procesamiento.
    """
    t = time.time()
    sequence = []
    for i in range(length):
        clean_val = math.sin((t + i * 0.1) * 2.0) * 1.5
        noise = (random.random() - 0.5) * 2.5  # Ruido aleatorio simulado
        sequence.append(clean_val + noise)
    return sequence

def main():
    print("=" * 65)
    print("TZANiX DATA SOLUTIONS - MOTOR DE PURIFICACIÓN IA")
    print("Cliente Local de Carga de Trabajo de Inferencia | FastAPI Core")
    print(f"Endpoint: {API_URL}")
    print(f"Credencial (X-IFA-Key): {API_KEY}")
    print("Presiona Ctrl+C para detener el flujo de datos.")
    print("=" * 65)
    
    headers = {
        "Content-Type": "application/json",
        "X-IFA-Key": API_KEY
    }
    
    count = 0
    try:
        while True:
            # Generar datos sucios de inferencia
            noisy_data = generate_noisy_ai_stream(50)
            
            payload = {
                "data_stream_id": "NEURAL-NETWORK-FEED",
                "stream_type": "ai_inference",
                "sequences": noisy_data
            }
            
            start_time = time.time()
            try:
                response = requests.post(API_URL, json=payload, headers=headers, timeout=2.0)
                elapsed_ms = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    eff = data.get("compute_efficiency_gain", 0.0)
                    purified = data.get("purified_data", [])
                    print(f"[{time.strftime('%H:%M:%S')}] Enviado #{count + 1:04d} | "
                          f"Latencia: {elapsed_ms:.1f}ms | "
                          f"Eficiencia: {eff}% | "
                          f"Puntos Purificados: {len(purified)}")
                elif response.status_code == 401:
                    print(f"[{time.strftime('%H:%M:%S')}] ERROR 401: Llave inválida o revocada en SQLite.")
                elif response.status_code == 402:
                    print(f"[{time.strftime('%H:%M:%S')}] ERROR 402: Suspendido por falta de pago.")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ERROR {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[{time.strftime('%H:%M:%S')}] ERROR de conexión con FastAPI: {e}")
            
            count += 1
            time.sleep(0.1)  # Bucle continuo cada 100 milisegundos
            
    except KeyboardInterrupt:
        print("\n\nFlujo detenido por el usuario.")
        print(f"Total de ráfagas procesadas: {count}")
        print("=" * 65)

if __name__ == "__main__":
    main()
