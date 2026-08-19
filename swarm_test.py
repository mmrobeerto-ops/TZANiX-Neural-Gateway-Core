import asyncio
import httpx
import time
import random
import json

# Configuración de la Prueba de Enjambre
API_URL = "http://127.0.0.1:8002/process"
NUM_DRONES = 10           # Cantidad de drones concurrentes
PETICIONES_POR_DRON = 10  # Telemetrías que enviará cada dron
TOTAL_REQUESTS = NUM_DRONES * PETICIONES_POR_DRON

async def dron_virtual(dron_id: int, client: httpx.AsyncClient, stats: dict):
    """
    Simula un dron enviando telemetría caótica.
    """
    for i in range(PETICIONES_POR_DRON):
        # Generar datos ruidosos sintéticos (Vibración de alta frecuencia + Picos)
        ruido = random.uniform(-10.0, 10.0)
        pico = random.choice([0, 0, 0, 50.0]) # Esporádicos picos de viento/golpe
        payload = {
            "datos": {
                "dron_id": dron_id,
                "seq": i,
                "raw_accel": 9.81 + ruido + pico,
                "gyro_z": random.uniform(-500.0, 500.0)
            }
        }
        
        start_time = time.perf_counter()
        try:
            response = await client.post(API_URL, json=payload, timeout=10.0)
            elapsed = time.perf_counter() - start_time
            
            if response.status_code == 200:
                stats['success'] += 1
                stats['latencies'].append(elapsed)
            else:
                stats['failed'] += 1
        except Exception as e:
            stats['errors'] += 1

async def main():
    print("======================================================")
    print(" INICIANDO PRUEBA DE ESTRES DE ENJAMBRE (SWARM TEST) ")
    print("======================================================")
    print(f" Drones Virtuales Concurrentes : {NUM_DRONES}")
    print(f" Peticiones por Dron           : {PETICIONES_POR_DRON}")
    print(f" Total de Paquetes Inerciales  : {TOTAL_REQUESTS}")
    print("------------------------------------------------------")
    
    stats = {
        'success': 0,
        'failed': 0,
        'errors': 0,
        'latencies': []
    }
    
    start_time = time.perf_counter()
    
    # Crear un pool de conexiones HTTP de alto rendimiento
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=NUM_DRONES)) as client:
        # Lanzar todos los drones simultáneamente
        tasks = [dron_virtual(dron_id, client, stats) for dron_id in range(NUM_DRONES)]
        await asyncio.gather(*tasks)
        
    total_time = time.perf_counter() - start_time
    
    print("\n======================================================")
    print(" RESULTADOS DEL ENJAMBRE ")
    print("======================================================")
    print(f" Tiempo Total de Simulación : {total_time:.4f} segundos")
    print(f" Peticiones Exitosas (200)  : {stats['success']} / {TOTAL_REQUESTS}")
    print(f" Peticiones Fallidas (500)  : {stats['failed']}")
    print(f" Errores de Red / Timeouts  : {stats['errors']}")
    
    if stats['latencies']:
        avg_latency = sum(stats['latencies']) / len(stats['latencies'])
        max_latency = max(stats['latencies'])
        print(f" Latencia Promedio (HTTP)   : {avg_latency*1000:.2f} ms por petición")
        print(f" Latencia Máxima (Jitter)   : {max_latency*1000:.2f} ms")
    
    throughput = stats['success'] / total_time
    print(f" Throughput del Servidor    : {throughput:.2f} Req/segundo")
    print("======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
