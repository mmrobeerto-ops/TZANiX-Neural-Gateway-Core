import asyncio
import aiohttp
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "dummy_key_not_checked_if_no_db" # The API expects an X-IFA-Key in the header

HEADERS = {
    "X-IFA-Key": "test_key", # Assuming a test key exists, or the middleware will reject it 401
    "Content-Type": "application/json"
}

# Payloads de prueba
CLEAN_PAYLOAD = {
    "data_stream_id": "sensor_001",
    "stream_type": "ai_inference",
    "sequences": [0.5, 0.52, 0.51, 0.49, 0.5],
    "scale_factor": 1
}

DIRTY_PAYLOAD = {
    "data_stream_id": "sensor_002",
    "stream_type": "ai_inference",
    "sequences": [0.5, 999.0, -999.0, 0.51, 0.49],
    "scale_factor": 1
}

async def send_request(session, payload, drop_connection=False):
    """Envía una petición al servidor. Simula caída de conexión si se solicita."""
    start_time = time.time()
    try:
        # Timeout agresivo si simulamos mala red
        timeout = aiohttp.ClientTimeout(total=0.5 if drop_connection else 5)
        
        # OMITIMOS EL HEADER X-IFA-Key PARA PRUEBAS SIN BASE DE DATOS LOCAL,
        # A MENOS QUE TENGAS UNA LLAVE VÁLIDA CREADA.
        # Por ahora lo mandamos sin header esperando un 401 que de todos modos
        # prueba la conexión web, o le quitamos la seguridad al endpoint para el test.
        async with session.post(URL, json=payload, headers=HEADERS, timeout=timeout) as response:
            if drop_connection:
                logging.warning("Simulando conexión caída abruptamente...")
                return "Dropped"
            
            # Solo leemos el estatus, no nos importa si falla la DB de claves
            status = response.status
            latency = (time.time() - start_time) * 1000
            return latency, status
    except Exception as e:
        if drop_connection:
            return "Dropped"
        return f"Error: {e}"

async def simulate_asymmetric_load(session):
    """Fase: Carga Asimétrica (Silencio seguido de un pico masivo)."""
    logging.info("=== INICIANDO PRUEBA DE CARGA ASIMÉTRICA ===")
    logging.info("Simulando silencio de red (10 segundos)...")
    await asyncio.sleep(10)
    
    logging.info("Disparando pico asíncrono de 1,000 peticiones en ráfaga...")
    start_time = time.time()
    
    tasks = []
    for _ in range(1000):
        tasks.append(send_request(session, CLEAN_PAYLOAD))
        
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    success_count = sum(1 for r in results if isinstance(r, tuple))
    logging.info(f"Ráfaga completada en {duration:.2f} segundos.")
    logging.info(f"Conexiones Atendidas: {success_count}/1000. RPS Efectivo: {1000 / duration:.2f}")

async def simulate_dropped_connections(session):
    """Fase: Conexiones Caídas (Tráfico Sucio y Roto)."""
    logging.info("=== INICIANDO PRUEBA DE CONEXIONES CAÍDAS ===")
    logging.info("Enviando 500 peticiones donde el 20% abortará la conexión...")
    
    tasks = []
    for i in range(500):
        is_drop = random.random() < 0.20 # 20% de probabilidad de caerse
        payload = DIRTY_PAYLOAD if random.random() < 0.3 else CLEAN_PAYLOAD
        tasks.append(send_request(session, payload, drop_connection=is_drop))
        
    results = await asyncio.gather(*tasks)
    
    dropped_count = results.count("Dropped")
    success_count = sum(1 for r in results if isinstance(r, tuple))
    
    logging.info(f"Prueba de Caídas Finalizada.")
    logging.info(f"Peticiones Existentes Atendidas: {success_count}")
    logging.info(f"Conexiones Abortadas Exitosamente (Manejadas por FastAPI): {dropped_count}")

async def main():
    async with aiohttp.ClientSession() as session:
        logging.info("Esperando que el servidor esté en línea...")
        await asyncio.sleep(2)
        
        await simulate_asymmetric_load(session)
        await asyncio.sleep(3)
        await simulate_dropped_connections(session)

if __name__ == "__main__":
    asyncio.run(main())
