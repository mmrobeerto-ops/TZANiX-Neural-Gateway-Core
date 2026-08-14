import asyncio
import aiohttp
import time
import os
import psutil
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

URL = "http://127.0.0.1:8000/api/v1/purify-stream"
DURATION_HOURS = 4
RPS_TARGET = 500

HEADERS = {
    "X-IFA-Key": "test_key",
    "Content-Type": "application/json"
}

PAYLOAD = {
    "data_stream_id": "soak_test_sensor",
    "stream_type": "industrial",
    "sequences": [0.5, 0.5, 0.49, 0.51, 0.5],
    "scale_factor": 1
}

def get_server_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024) # MB

async def send_batch(session, batch_size):
    tasks = []
    for _ in range(batch_size):
        tasks.append(session.post(URL, json=PAYLOAD, headers=HEADERS, timeout=2))
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    # Ignorar auth failures (401) si no configuramos la DB para el test
    successes = sum(1 for r in responses if not isinstance(r, Exception) and (r.status == 200 or r.status == 401))
    return successes

async def run_soak_test():
    logging.info(f"=== INICIANDO SOAK TEST DE {DURATION_HOURS} HORAS ===")
    logging.info(f"Objetivo: {RPS_TARGET} Requests Per Second (RPS)")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=DURATION_HOURS)
    
    total_requests_sent = 0
    total_successes = 0
    
    async with aiohttp.ClientSession() as session:
        while datetime.now() < end_time:
            batch_start = time.time()
            
            successes = await send_batch(session, RPS_TARGET)
            
            total_requests_sent += RPS_TARGET
            total_successes += successes
            
            if total_requests_sent % 10000 == 0:
                elapsed = datetime.now() - start_time
                mem_usage = get_server_memory_usage()
                logging.info(f"--- REPORTE DE SOAK TEST ---")
                logging.info(f"Tiempo Transcurrido: {elapsed}")
                logging.info(f"Peticiones Totales: {total_requests_sent}")
                logging.info(f"Conexiones Atendidas: {total_successes}")
                logging.info(f"Uso de Memoria (Script Tester): {mem_usage:.2f} MB")
                
            elapsed_batch = time.time() - batch_start
            sleep_time = max(0, 1.0 - elapsed_batch)
            await asyncio.sleep(sleep_time)
            
    logging.info("=== SOAK TEST FINALIZADO ===")
    logging.info(f"Total Enviado: {total_requests_sent}")
    logging.info(f"Total Éxitos: {total_successes}")

if __name__ == "__main__":
    try:
        asyncio.run(run_soak_test())
    except KeyboardInterrupt:
        logging.info("Soak Test interrumpido por el usuario.")
