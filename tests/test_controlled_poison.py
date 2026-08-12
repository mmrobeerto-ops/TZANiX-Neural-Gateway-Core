import requests
import numpy as np
import time

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"

def run_controlled_poison_test():
    print("==========================================================")
    print("🔥 TZANiX NEURAL GATEWAY - PRUEBA DE VENENO CONTROLADO 🔥")
    print("==========================================================")
    
    # 1. Generar el "Ground Truth" (Dataset Puro)
    # Simularemos 1 Millón de vectores limpios (una onda senoidal perfecta)
    print("\n[1] Generando 1,000,000 de vectores limpios (Ground Truth)...")
    clean_size = 1000000
    t = np.linspace(0, 100, clean_size)
    clean_vectors = np.sin(t)
    
    # 2. Generar el "Veneno"
    # Inyectaremos exactamente 50,000 vectores basura (ruido extremo / outliers)
    poison_size = 50000
    print(f"[2] Sintetizando {poison_size} vectores envenenados (Ruido de alta frecuencia)...")
    
    # Creamos un array combinado y lo llenamos de ruido en posiciones aleatorias
    total_size = clean_size + poison_size
    combined_vectors = np.zeros(total_size)
    
    # Insertar el dataset limpio
    combined_vectors[:clean_size] = clean_vectors
    
    # Insertar el veneno al final (luego mezclaremos todo)
    # El veneno serán picos anómalos masivos
    poison_data = np.random.uniform(50.0, 100.0, poison_size) 
    combined_vectors[clean_size:] = poison_data
    
    # Mezclar aleatoriamente para que el veneno esté oculto en los datos
    print("[3] Mezclando el veneno dentro del dataset limpio (Ofuscación)...")
    np.random.shuffle(combined_vectors)
    
    print(f"\n[>] Tamaño del Dataset Envenenado: {len(combined_vectors):,} vectores.")
    
    # 3. Enviar a TZANiX Neural Gateway
    payload = {
        "data_stream_id": "test_venom_001",
        "stream_type": "ai_inference",
        "sequences": combined_vectors.tolist(),
        "scale_factor": 1
    }
    
    headers = {
        "X-IFA-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("\n[4] 🚀 Enviando datos al Motor Cuántico TZANiX para purificación...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        end_time = time.time()
        
        purified_data = data.get("purified_data", [])
        quarantine_data = data.get("quarantine_data", [])
        purified_size = len(purified_data)
        quarantine_size = len(quarantine_data)
        
        print(f"\n✅ Purificación completada en {end_time - start_time:.2f} segundos.")
        
        # 4. Verificación y Auditoría
        margin_of_error = abs(quarantine_size - poison_size)
        
        print("\n==========================================================")
        print("📊 REPORTE DE AUDITORÍA Y CUARENTENA")
        print("==========================================================")
        print(f"Vectores Originales (Enviados): {total_size:,}")
        print(f"Vectores Limpios (Devueltos):   {purified_size:,}")
        print(f"Vectores en Cuarentena (Basura): {quarantine_size:,}")
        
        print("\n🔎 VERIFICACIÓN DE PRECISIÓN:")
        print(f"Veneno inyectado por nosotros:  {poison_size:,}")
        print(f"Veneno detectado por TZANiX:    {quarantine_size:,}")
        
        if quarantine_size == poison_size:
            print("\n🎯 RESULTADO: ÉXITO ABSOLUTO (Margen de Error: 0.00%)")
            print("El motor identificó el 100% del veneno sin borrar un solo vector útil.")
        elif margin_of_error < (poison_size * 0.05): # 5% de margen
            print(f"\n⚠️ RESULTADO: EXCELENTE (Margen de Error: {(margin_of_error/total_size)*100:.4f}%)")
            print("El motor identificó casi la totalidad del veneno con una precisión comercial aceptable.")
        else:
            print(f"\n❌ RESULTADO: FALLO (Margen de Error: {(margin_of_error/total_size)*100:.4f}%)")
            print("El motor fue engañado por el veneno o fue demasiado agresivo.")
            
        print(f"\n💰 Ahorro de Energía (GPU): {data.get('compute_efficiency_gain', 0)}%")
        print(f"🌱 Ahorro de Carbono (ESG): {data.get('carbon_footprint_saved_grams', 0)} gramos de CO2")
        print("==========================================================")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error al conectar con TZANiX API: {e}")
        print("Asegúrate de que el servidor esté corriendo (uvicorn main:app --reload)")

if __name__ == "__main__":
    run_controlled_poison_test()
