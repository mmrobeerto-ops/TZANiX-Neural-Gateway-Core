import asyncio
import json
import websockets
import requests

# Configuración de infraestructura local Fourier IFA
API_URL = "http://127.0.0.1:8000/api/v1/purify-stream"
API_KEY = "ifa_live_btc_trader_99x"  # Llave registrada en SQLite
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@ticker"

price_buffer = []
BUFFER_SIZE = 50  # Tamaño de la secuencia para la Transformada de Fourier

async def stream_bitcoin_to_ifa():
    global price_buffer
    print(f" Connecting to Live Bitcoin Stream via Binance WebSockets...")
    
    async with websockets.connect(BINANCE_WS_URL) as ws:
        while True:
            try:
                # 1. Escuchar precio de BTC en tiempo real
                data = await ws.recv()
                msg = json.loads(data)
                current_price = float(msg['c']) # 'c' es el precio de cierre actual
                
                price_buffer.append(current_price)
                
                # Mantener el buffer optimizado para el análisis secuencial
                if len(price_buffer) > BUFFER_SIZE:
                    price_buffer.pop(0)
                
                # 2. Cuando el buffer esté lleno, enviar al motor de 7.25 Hz
                if len(price_buffer) == BUFFER_SIZE:
                    payload = {
                        "data_stream_id": "BTC-USD-LIVE",
                        "stream_type": "financial",
                        "sequences": price_buffer
                    }
                    
                    headers = {
                        "X-IFA-Key": API_KEY,
                        "Content-Type": "application/json"
                    }
                    
                    # Enviar al backend local en FastAPI
                    response = requests.post(API_URL, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"[IFA CORE] BTC Price: {current_price} | Gain: {result['compute_efficiency_gain']}% | Stream Sintonizado")
                    else:
                        print(f"[ERROR API] Status {response.status_code}: {response.text}")
                        
                await asyncio.sleep(1) # Procesar segundo a segundo
                
            except Exception as e:
                print(f"[CRITICAL ERROR]: {e}")
                await asyncio.sleep(5) # Reconectar en caso de caída de red

if __name__ == "__main__":
    # Necesita: pip install websockets
    asyncio.run(stream_bitcoin_to_ifa())
