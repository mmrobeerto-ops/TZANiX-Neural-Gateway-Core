import time
import asyncio
import aiohttp
import math
import sys

API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_ai_research_05w"

TOTAL_REQUESTS = 10000
CONCURRENT_CONNECTIONS = 1000

print("=" * 70)
print("PRUEBA 3 FINAL: ASFIXIA INDUSTRIAL (AIOHTTP)")
print(f"Disparando {TOTAL_REQUESTS} peticiones masivas al servidor FastAPI...")
print("=" * 70)

payload_data = [math.sin(2 * math.pi * 7.25 * (i / 100.0)) * 5.0 for i in range(50)]
payload = {
    "data_stream_id": "STRESS-TEST-NODE",
    "stream_type": "industrial",
    "sequences": payload_data
}
headers = {
    "Content-Type": "application/json",
    "X-IFA-Key": API_KEY
}

success_count = 0
failed_count = 0
latencies = []

async def fire_request(session):
    global success_count, failed_count
    start_time = time.time()
    try:
        async with session.post(API_URL, json=payload, headers=headers, timeout=60.0) as response:
            if response.status == 200:
                success_count += 1
                latencies.append((time.time() - start_time) * 1000)
            else:
                failed_count += 1
    except Exception:
        failed_count += 1

    total_done = success_count + failed_count
    if total_done % 1000 == 0:
        print(f"    -> Progreso: {total_done}/{TOTAL_REQUESTS} peticiones disparadas...")

async def run_stress_test():
    start_time_global = time.time()
    
    # TCPConnector optimizado para no limitar conexiones
    connector = aiohttp.TCPConnector(limit=CONCURRENT_CONNECTIONS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(fire_request(session)) for _ in range(TOTAL_REQUESTS)]
        await asyncio.gather(*tasks)

    total_time_global = time.time() - start_time_global
    requests_per_second = TOTAL_REQUESTS / total_time_global
    
    print("\n" + "=" * 70)
    print("RESULTADO DE LA PRUEBA DE RENDIMIENTO")
    print("=" * 70)
    
    print(f"Tiempo Total del Ataque:  {total_time_global:.2f} segundos")
    print(f"Rendimiento Real (RPS):   {requests_per_second:.2f} peticiones por segundo")
    print(f"Conexiones Exitosas:      {success_count}")
    print(f"Conexiones Fallidas:      {failed_count}")
    
    if success_count > 0:
        avg_latency = sum(latencies) / success_count
        print(f"Latencia Promedio:        {avg_latency:.2f} ms")
        print(f"Latencia Máxima (Pico):   {max(latencies):.2f} ms")
        
    print("\nDIAGNÓSTICO DEL NÚCLEO:")
    if failed_count == 0 and requests_per_second > 500:
        print("[EXITO TOTAL]: El servidor es un búnker. 0% de fallas bajo estrés industrial masivo.")
    elif failed_count > 0:
        print("[FRACASO PARCIAL]: El embudo purificador se asfixió. El servidor rechazó conexiones o superó el timeout.")
    else:
        print("[ALERTA AMARILLA]: No hubo fallos, pero el servidor está muy lento para escenarios de 10k RPS.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
