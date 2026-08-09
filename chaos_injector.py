import time
import math
import random
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"

def generate_extreme_chaos_stream(length=100):
    """
    Genera una señal limpia sintonizada a 7.25 Hz y le inyecta caos absoluto:
    - Ruido blanco de alta frecuencia (vibración).
    - Anomalías extremas puntuales (flash crashes / golpes mecánicos).
    """
    t = time.time()
    clean_signal = []
    chaotic_signal = []
    
    for i in range(length):
        # 1. Señal base pura (simulando nuestra frecuencia dorada de 7.25 Hz)
        # La frecuencia matemática en el seno dependerá del muestreo, pero simulamos una onda estable.
        base_val = math.sin(2 * math.pi * 7.25 * (i / 100.0)) * 5.0
        clean_signal.append(base_val)
        
        # 2. Inyección de caos: Ruido de vibración extrema (IMU Drone en huracán)
        noise = (random.random() - 0.5) * 15.0  # Ruido masivo, 3x más grande que la señal
        
        # 3. Inyección de Anomalías (Flash Crashes)
        # Hay un 5% de probabilidad de que el sensor se vuelva loco y mande un valor destructivo
        if random.random() < 0.05:
            noise += random.choice([-50.0, 50.0]) # Golpe mecánico o caída brusca de precio
            
        chaotic_signal.append(base_val + noise)
        
    return clean_signal, chaotic_signal

def run_chaos_test():
    print("=" * 70)
    print("PRUEBA 1: INYECCIÓN DE CAOS ABSOLUTO (Fidelidad Matemática)")
    print("Inyectando ruido extremo y anomalías destructivas al Motor Tzanix...")
    print("=" * 70)
    
    headers = {
        "Content-Type": "application/json",
        "X-IFA-Key": API_KEY
    }
    
    clean_wave, chaotic_wave = generate_extreme_chaos_stream(100)
    
    payload = {
        "data_stream_id": "DRONE-IMU-CHAOS-001",
        "stream_type": "industrial",
        "sequences": chaotic_wave
    }
    
    print("\n[+] Lanzando ráfaga caótica al servidor FastAPI...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5.0)
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            purified = data.get("purified_data", [])
            
            # Verificación de la Fidelidad Matemática
            # Revisaremos si el sistema sobrevivió o si "alucinó" por los flash crashes.
            # Comparamos la señal purificada con nuestra señal limpia original (ideal).
            
            error_margin = 0.0
            for c, p in zip(clean_wave, purified):
                error_margin += abs(c - p)
            avg_error = error_margin / len(clean_wave)
            
            print(f"\n[OK] Respuesta recibida en {elapsed_ms:.2f} ms")
            print(f"[-] Ahorro de Huella de Carbono: {data.get('carbon_footprint_saved_grams')} g")
            print(f"[-] Consumo Energético: {data.get('energy_consumed_watts')} W")
            
            print("\n" + "=" * 70)
            print("RESULTADO DE LA PRUEBA DE FIDELIDAD")
            print("=" * 70)
            
            # Un error promedio bajo significa que la onda de 7.25Hz sobrevivió al ataque
            if avg_error < 5.0:
                print("[EXITO TOTAL]: El núcleo cuántico ignoró el caos absoluto.")
                print(f"El margen de error promedio respecto a la onda pura fue de apenas: {avg_error:.2f}")
                print("El motor no alucinó datos a pesar de los picos anómalos masivos.")
            else:
                print("[FRACASO]: El sistema fue engañado por el ruido y deformó la tendencia.")
                print(f"Margen de error destructivo: {avg_error:.2f}")
                
        else:
            print(f"[ERROR DEL SERVIDOR]: El sistema colapsó o rechazó los datos (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"[COLAPSO TOTAL]: El motor falló al procesar. Detalle: {e}")

if __name__ == "__main__":
    run_chaos_test()
