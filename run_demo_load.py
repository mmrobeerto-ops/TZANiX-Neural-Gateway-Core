import time
import requests
import numpy as np
import random

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"

def generate_demo_signal(step, length=50):
    # Crear un movimiento de onda sinusoidal limpia
    t = np.linspace(step * 0.1, step * 0.1 + 2 * np.pi, length)
    base = np.sin(t) * 10.0
    
    # Ruido gaussiano
    noise = np.random.normal(0, 1.8, length)
    
    # Picos industriales aleatorios (spikes) para mostrar la purificación
    spikes = np.zeros(length)
    if step % 8 == 0:
        spikes[random.randint(0, length - 1)] = 15.0
    elif step % 12 == 0:
        spikes[random.randint(0, length - 1)] = -15.0
        
    signal = base + noise + spikes
    return signal.tolist()

def main():
    print("=================================================================")
    print("TZANiX DEMO SIMULATOR - ALIMENTANDO INFERENCIA HOLOGRÁFICA")
    print("=================================================================")
    print("Preparando simulación para grabación de video (Duración: ~40s)...")
    time.sleep(2)
    
    headers = {"X-IFA-Key": API_KEY}
    
    for i in range(120):  # 120 iteraciones a 250ms = 30 segundos de animación
        signal = generate_demo_signal(i)
        payload = {
            "data_stream_id": "NEURAL-NETWORK-FEED",
            "stream_type": "ai_inference",
            "sequences": signal
        }
        
        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=2)
            if r.status_code == 200:
                data = r.json()
                print(f"[DEMO #{i+1:03d}] Ticks: 50 | Morton: {data.get('spatial_signature_4d')} | Attenuation: {data.get('compute_efficiency_gain'):.2f}%", flush=True)
            else:
                print(f"[ERROR] HTTP {r.status_code}", flush=True)
        except Exception as e:
            print(f"[ERROR] Conexión fallida: {e}", flush=True)
            
        time.sleep(0.25)  # Enviar cada 250ms para un refresco fluido
        
    print("\n[SIMULACIÓN COMPLETADA] Fin del flujo de video demo.")
    print("=================================================================")

if __name__ == "__main__":
    main()
