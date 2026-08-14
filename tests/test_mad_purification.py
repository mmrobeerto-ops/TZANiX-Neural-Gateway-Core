import requests
import json
import logging

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(message)s')

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "tzx_live_godmode_2026" # La llave que instalamos en el God Mode

def run_purification_test():
    logging.info("=== TZANiX NEURAL GATEWAY - PRUEBA DE PURIFICACIÓN MAD ===")
    
    # 1. El Vector Sucio (Veneno Inyectado)
    # Contiene datos normales (~10.x) y dos valores atípicos masivos.
    dirty_vector = [10.2, 10.5, 9999.0, 10.1, -8888.0, 10.4]
    
    payload = {
        "data_stream_id": "mad_validation_test",
        "stream_type": "sensor_telemetry",
        "sequences": dirty_vector,
        "scale_factor": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-IFA-Key": API_KEY
    }
    
    logging.info(f"\n[>] ENVIANDO VECTOR SUCIO A LA API:")
    logging.info(json.dumps(dirty_vector, indent=2))
    
    try:
        # Enviar petición al Motor de Rust
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logging.info("\n[<] RESPUESTA DEL MOTOR TZANiX (PURIFICADA):")
            
            clean_signals = data.get("purified_data", [])
            quarantine = data.get("quarantine_data", [])
            
            logging.info(f"\n  ✅ DATOS SEGUROS PARA LA IA (CLEAN ZONE):")
            logging.info(f"  {json.dumps(clean_signals)}")
            
            logging.info(f"\n  ☣️ VENENO DETECTADO Y BLOQUEADO (QUARANTINE ZONE):")
            logging.info(f"  {json.dumps(quarantine)}")
            
            logging.info("\n=== PRUEBA FINALIZADA CON ÉXITO ===")
        else:
            logging.error(f"Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        logging.error("Error: El servidor no está en línea. Asegúrate de ejecutar Uvicorn primero.")

if __name__ == "__main__":
    run_purification_test()
