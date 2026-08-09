import requests
import sqlite3
import json
import os

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = os.path.join(os.path.dirname(__file__), "fourier_ifa.db")

def check_client_status(client_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, stripe_customer_id FROM users_keys WHERE client_id = ?", (client_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def test_webhook_suspension():
    print("=" * 70)
    print("INICIANDO PRUEBA DE WEBHOOK DE STRIPE (BLOQUEO AUTOMÁTICO)")
    print("=" * 70)

    # 1. Comprobar estado inicial del cliente de Bitcoin (Debe ser active)
    client_id = "Financial_Trader"
    initial_status, customer_id = check_client_status(client_id)
    print(f"Estado inicial de {client_id}: {initial_status} (Stripe ID: {customer_id})")
    
    if initial_status != "active":
        print("[AVISO] El cliente no estaba activo. Forzando a activo para la prueba...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users_keys SET status = 'active' WHERE client_id = ?", (client_id,))
        conn.commit()
        conn.close()
        initial_status, _ = check_client_status(client_id)
        print(f"Nuevo estado forzado: {initial_status}")

    # 2. Enviar evento mock de invoice.payment_failed a la API
    webhook_url = f"{BASE_URL}/api/v1/webhooks/stripe"
    mock_event = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "customer": customer_id
            }
        }
    }
    
    print(f"Enviando evento 'invoice.payment_failed' ficticio a: {webhook_url}...")
    try:
        response = requests.post(webhook_url, json=mock_event)
        if response.status_code == 200:
            print("Webhook procesado exitosamente por la API (HTTP 200).")
        else:
            print(f"[ERROR] Código devuelto por el Webhook: {response.status_code} - {response.text}")
            return
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar al servidor FastAPI. Asegúrate de iniciarlo en el puerto 8000.")
        return

    # 3. Comprobar nuevo estado en base de datos (Debe ser suspended)
    new_status, _ = check_client_status(client_id)
    print(f"Estado final de {client_id}: {new_status}")
    
    if new_status == "suspended":
        print("\n[ÉXITO] El bloqueo automático funcionó correctamente. La API Key ha sido suspendida.")
    else:
        print(f"\n[FALLO] La API Key no fue suspendida. Estado actual: {new_status}")

    # 4. Probar que las peticiones de purificación de señales sean rebotadas con error 402 Payment Required
    purify_url = f"{BASE_URL}/api/v1/purify-stream"
    payload = {
        "data_stream_id": "BTC-USD-TICK",
        "stream_type": "financial",
        "sequences": [65000.0, 65100.0, 64900.0]
    }
    headers = {
        "X-IFA-Key": "ifa_live_btc_trader_99x"
    }
    
    print("\nVerificando denegación de servicio en /purify-stream...")
    response_purify = requests.post(purify_url, json=payload, headers=headers)
    print(f"Código HTTP recibido (Esperado 402): {response_purify.status_code}")
    print(f"Respuesta de la API: {response_purify.json()}")
    
    if response_purify.status_code == 402:
        print("[ÉXITO] El endpoint bloqueó la petición con HTTP 402 Payment Required.")
    else:
        print(f"[FALLO] La petición no fue bloqueada. Código HTTP devuelto: {response_purify.status_code}")

    print("\n" + "=" * 70)
    print("FIN DE LA PRUEBA DE WEBHOOK")
    print("=" * 70)

if __name__ == "__main__":
    test_webhook_suspension()
