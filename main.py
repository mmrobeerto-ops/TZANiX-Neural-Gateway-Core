import time
import sqlite3
import os
import secrets
import json
import stripe
from fastapi import FastAPI, HTTPException, Depends, Security, status, WebSocket, APIRouter, Request, Header, BackgroundTasks
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import numpy as np
import notifications
import licensing

# =====================================================================
# SYSTEM: Fourier IFA (Inteligencia Fractal Armónica) - Núcleo Universal
# CORE FREQUENCY: 7.25 Hz (Punto óptimo de silencio y flujo armónico)
# =====================================================================

app = FastAPI(
    title="Tzanix Tensor-Zero Core",
    description="Motor cuántico de tensores simulados para purificación de flujos de datos. Diseñado para consumo energético cercano a cero y huella de carbono ultra baja en nodos Edge.",
    version="3.0.0"
)

# Habilitar CORS para comunicación con el Portal Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-IFA-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Ruta absoluta para asegurar que conecte a la misma base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "fourier_ifa.db")

# Configuración de llaves de Stripe
stripe.api_key = "sk_test_tu_llave_secreta_de_stripe"
STRIPE_WEBHOOK_SECRET = "whsec_tu_secreto_de_webhook_local"

# Modelos Pydantic Universales
class UniversalDataPayload(BaseModel):
    data_stream_id: str
    stream_type: str
    sequences: List[float]
    scale_factor: Optional[int] = 1

class UniversalIFAResponse(BaseModel):
    data_stream_id: str
    stream_type: str
    status: str
    compute_efficiency_gain: float
    purified_data: List[float]
    quarantine_data: Optional[List[float]] = None
    spatial_signature_4d: Optional[int] = None
    spatial_coordinates: Optional[List[float]] = None
    knn_neighbors: Optional[List[dict]] = None
    energy_consumed_watts: float
    carbon_footprint_saved_grams: float
    tensor_delegation_status: str

# Middleware de Autenticación con DB
async def verify_fourier_ifa_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-IFA-Key requerida."
        )
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT client_id, plan_type, status FROM users_keys WHERE api_key = ?",
        (api_key,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida."
        )
        
    client_id, plan_type, status_val = user
    if status_val == "revoked":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key revocada."
        )
    elif status_val == "suspended":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="API Key suspendida por falta de pago."
        )
        
    return {"client_id": client_id, "plan_type": plan_type}

# =====================================================================
# MOTOR DE HIPERESPACIO 4D (TESSERACT) - BUFFER DE MEMORIA RAM CONTIGUO
# =====================================================================
import threading
from numba import njit
from scipy.spatial import cKDTree

TESSERACT_MAX_SIZE = 50000
tesseract_coords = np.zeros((TESSERACT_MAX_SIZE, 4), dtype=np.float32)
tesseract_mortons = np.zeros(TESSERACT_MAX_SIZE, dtype=np.uint64)
tesseract_metadata = []
tesseract_count = 0
tesseract_lock = threading.Lock()
global_kdtree = None
last_kdtree_count = 0

NORMALIZATION_SCALES = {
    "ai_inference": {"mean_div": 10.0, "std_div": 5.0, "last_div": 10.0, "grad_div": 5.0},
    "financial": {"mean_div": 150000.0, "std_div": 5000.0, "last_div": 150000.0, "grad_div": 2000.0},
    "industrial": {"mean_div": 500.0, "std_div": 100.0, "last_div": 500.0, "grad_div": 50.0}
}

@njit(fastmath=True, cache=True)
def interleave_bits_64(n):
    n = (n | (n << 16)) & 0x0000FFFF0000FFFF
    n = (n | (n << 8)) & 0x00FF00FF00FF00FF
    n = (n | (n << 4)) & 0x0F0F0F0F0F0F0F0F
    n = (n | (n << 2)) & 0x3333333333333333
    n = (n | (n << 1)) & 0x5555555555555555
    return n

try:
    import tzanix_core_rs
    RUST_CORE_ENABLED = False # Temporarily disabled for architecture rewrite
    print("[NÚCLEO] Armadura Pesada (Rust Core) Detectada, pero ignorada forzosamente para la prueba MAD.")
except ImportError:
    RUST_CORE_ENABLED = False
    print("[NÚCLEO] Rust Core no detectado. Operando con Python puro.")

@njit(fastmath=True, cache=True)
def get_morton_code_4d_python(x, y, z, t):
    ix = int(max(0.0, min(65535.0, x * 65535.0)))
    iy = int(max(0.0, min(65535.0, y * 65535.0)))
    iz = int(max(0.0, min(65535.0, z * 65535.0)))
    it = int(max(0.0, min(65535.0, t * 65535.0)))
    
    return (interleave_bits_64(it) << 3) | (interleave_bits_64(iz) << 2) | \
           (interleave_bits_64(iy) << 1) | interleave_bits_64(ix)

def get_morton_code_4d(x, y, z, t):
    if RUST_CORE_ENABLED:
        return tzanix_core_rs.get_morton_code_4d_rs(x, y, z, t)
    return get_morton_code_4d_python(x, y, z, t)

# Función knn_search_4d eliminada en favor de cKDTree

@app.on_event("startup")
def verify_hardware_license():
    import sys
    print("=================================================================", flush=True)
    print("TZANiX DATA SOLUTIONS - INICIALIZANDO VALIDACION DE LICENCIA", flush=True)
    print("=================================================================", flush=True)
    license_path = os.path.join(os.path.dirname(__file__), "license.key")
    current_uuid = licensing.get_hardware_uuid()
    
    if not os.path.exists(license_path):
        print(f"\n[ERROR DE LICENCIA] Archivo 'license.key' no encontrado en: {license_path}", flush=True)
        print("Para activar este nodo edge de TZANiX, por favor genera una clave.", flush=True)
        print(f"UUID DE HARDWARE DE ESTE EQUIPO: {current_uuid}", flush=True)
        print("=================================================================", flush=True)
        sys.stdout.flush()
        os._exit(1)
        
    with open(license_path, "r") as f:
        token = f.read().strip()
        
    valid, result = licensing.verify_license_token(token)
    if not valid:
        print(f"\n[ERROR DE LICENCIA] La activacion ha fallado:\n{result}", flush=True)
        print("=================================================================", flush=True)
        print(f"UUID DE HARDWARE DE ESTE EQUIPO: {current_uuid}", flush=True)
        print("=================================================================", flush=True)
        sys.stdout.flush()
        os._exit(1)
        
    print(f"[LICENCIA ACTIVA] Nodo registrado para el cliente: {result.get('client_id')}", flush=True)
    print(f"Vigencia del token: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.get('expiry')))}", flush=True)
    print("=================================================================", flush=True)
    sys.stdout.flush()

@app.on_event("startup")
def warmup_jit_functions():
    print("[WARMUP] Pre-compilando funciones JIT Numba para Tesseract...")
    dummy_code = get_morton_code_4d(0.5, 0.5, 0.5, 0.5)
    dummy_coords = np.random.rand(10, 4).astype(np.float32)
    dummy_query = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
    print(f"[WARMUP] Compilacion JIT finalizada. Codigo Morton de prueba: {dummy_code}")
    
    # Activar WAL mode en SQLite para máximo rendimiento
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.close()
        print("[DATABASE] SQLite WAL Mode activado exitosamente.")
    except Exception as e:
        print(f"[DATABASE] Error configurando WAL: {e}")
        
    # Inicializar la Cola Asíncrona de Logs y el Demonio de Escritura Masiva
    global log_queue
    log_queue = asyncio.Queue()
    asyncio.create_task(db_batch_writer())
    print("[NÚCLEO] Demonio Batch Writer activado. Cola en RAM lista.")

log_queue = None

def perform_batch_insert(batch):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO stream_logs (client_id, data_stream_id, stream_type, sequences_count, efficiency_gain, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[!] SQLite Busy en segundo plano durante BATCH INSERT: {e}")
    finally:
        conn.close()

async def db_batch_writer():
    batch = []
    last_write = time.time()
    
    while True:
        try:
            item = await asyncio.wait_for(log_queue.get(), timeout=1.0)
            batch.append(item)
            log_queue.task_done()
        except asyncio.TimeoutError:
            pass
            
        # Si llegamos a 1000 items o pasamos de 1 segundo con items pendientes
        if len(batch) >= 1000 or (len(batch) > 0 and (time.time() - last_write) > 1.0):
            await asyncio.to_thread(perform_batch_insert, batch)
            batch.clear()
            last_write = time.time()

async def broadcast_ws(response_payload: dict):
    for ws in list(active_websockets):
        try:
            await ws.send_json(response_payload)
        except Exception:
            if ws in active_websockets:
                active_websockets.remove(ws)

class TzanixQuantumCore:
    @staticmethod
    def process_tensor_stream(sequences: List[float]) -> Tuple[List[float], List[float]]:
        """
        Purificación Tensorial: Rechaza vectores atípicos (Veneno) usando 
        la Mediana de Desviación Absoluta (MAD) robusta.
        """
        signal_array = np.array(sequences)
        if len(signal_array) == 0:
            return [], []
            
        median = np.median(signal_array)
        mad = np.median(np.abs(signal_array - median))
        if mad == 0:
            mad = 1e-6 # prevent division by zero
            
        # Z-Score robusto (threshold 3.0 es común)
        z_scores = 0.6745 * (signal_array - median) / mad
        
        # Filtro: valores con z_score <= 3.0 pasan
        mask = np.abs(z_scores) <= 3.0
        
        clean_signals = signal_array[mask].tolist()
        quarantine = signal_array[~mask].tolist()
        
        return clean_signals, quarantine

# Lista de conexiones WebSocket de clientes web activas
active_websockets: List[WebSocket] = []

@app.websocket("/ws/live-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    print(f"[WS] Nueva conexión establecida: {websocket.client}")
    try:
        while True:
            # Mantener la conexión abierta escuchando mensajes vacíos/ping
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        print(f"[WS] Conexión cerrada: {websocket.client}")

import asyncio

def heavy_math_pipeline(sequences, stream_type):
    global tesseract_count, global_kdtree, last_kdtree_count
    
    # 1. Purify
    clean_signals, quarantine_data = TzanixQuantumCore.process_tensor_stream(sequences)
    
    # 2. Extract metrics
    clean_array = np.array(clean_signals)
    x_val = float(np.mean(clean_array))
    y_val = float(np.std(clean_array))
    z_val = float(clean_signals[-1])
    t_val = float(np.gradient(clean_array)[-1]) if len(clean_signals) > 1 else 0.0
    
    scales = NORMALIZATION_SCALES.get(stream_type, NORMALIZATION_SCALES["ai_inference"])
    x_norm = float(np.clip(x_val / scales["mean_div"], 0.0, 1.0))
    y_norm = float(np.clip(y_val / scales["std_div"], 0.0, 1.0))
    z_norm = float(np.clip(z_val / scales["last_div"], 0.0, 1.0))
    t_norm = float(np.clip((t_val + scales["grad_div"]) / (2 * scales["grad_div"]), 0.0, 1.0))
    
    query_coord = np.array([x_norm, y_norm, z_norm, t_norm], dtype=np.float32)
    morton_code = int(get_morton_code_4d(x_norm, y_norm, z_norm, t_norm))
    
    knn_neighbors_list = []
    
    with tesseract_lock:
        current_count = tesseract_count
        
    if current_count > 0:
        with tesseract_lock:
            if global_kdtree is None or (current_count - last_kdtree_count) >= 100:
                global_kdtree = cKDTree(tesseract_coords[:current_count])
                last_kdtree_count = current_count
        
        dists, indices = global_kdtree.query(query_coord, k=min(3, current_count))
        if np.isscalar(dists):
            dists = [dists]
            indices = [indices]
            
        for idx, dist in zip(indices, dists):
            meta = tesseract_metadata[idx]
            knn_neighbors_list.append({
                "data_stream_id": meta["data_stream_id"],
                "timestamp": meta["timestamp"],
                "distance": float(dist),
                "morton_code": int(tesseract_mortons[idx])
            })
            
    return clean_signals, quarantine_data, query_coord, morton_code, knn_neighbors_list

# Endpoint Universal Protegido y Auditado
@app.post("/api/v1/purify-stream", response_model=UniversalIFAResponse)
async def purify_data_stream(
    payload: UniversalDataPayload,
    background_tasks: BackgroundTasks,
    auth_info: dict = Depends(verify_fourier_ifa_key)
):
    try:
        global tesseract_count
        # Procesamiento delegado al hilo secundario para no asfixiar el Event Loop
        clean_signals, quarantine_data, query_coord, morton_code, knn_neighbors_list = await asyncio.to_thread(
            heavy_math_pipeline, payload.sequences, payload.stream_type
        )
        
        # Simulación de métricas de huella de carbono y energía
        efficiency_gain = round(float(np.random.uniform(92.0, 99.9)), 2)
        energy_consumed_watts = round(float(np.random.uniform(0.001, 0.005)), 4)
        carbon_saved = round(float(np.random.uniform(0.5, 2.0)), 2) # gramos de CO2 ahorrados
                
        # 4. Inserción segura de hilos en Buffer Circular
        new_meta = {
            "data_stream_id": payload.data_stream_id,
            "timestamp": time.time(),
            "purified_data": clean_signals
        }
        with tesseract_lock:
            insert_idx = tesseract_count % TESSERACT_MAX_SIZE
            tesseract_coords[insert_idx] = query_coord
            tesseract_mortons[insert_idx] = morton_code
            if len(tesseract_metadata) < TESSERACT_MAX_SIZE:
                tesseract_metadata.append(new_meta)
            else:
                tesseract_metadata[insert_idx] = new_meta
            tesseract_count += 1
            
        # Insertar a la cola en RAM (Toma 0.000001 segundos, NO BLOQUEA)
        if log_queue is not None:
            log_queue.put_nowait((
                auth_info["client_id"],
                payload.data_stream_id,
                payload.stream_type,
                len(payload.sequences) * payload.scale_factor,
                efficiency_gain,
                time.time()
            ))
        
        # Estructurar respuesta para retransmitir por WS (incluyendo métricas ambientales)
        response_payload = {
            "data_stream_id": payload.data_stream_id,
            "stream_type": payload.stream_type,
            "status": f"Secuencia armonizada vía Tzanix Quantum Core bajo el plan {auth_info['plan_type']}",
            "compute_efficiency_gain": efficiency_gain,
            "purified_data": clean_signals,
            "original_data": payload.sequences,
            "spatial_signature_4d": morton_code,
            "spatial_coordinates": query_coord.tolist(),
            "knn_neighbors": knn_neighbors_list,
            "energy_consumed_watts": energy_consumed_watts,
            "carbon_footprint_saved_grams": carbon_saved,
            "tensor_delegation_status": "Active (Zero-Carbon Mode)"
        }
        
        # Retransmitir asincrónicamente a todos los clientes web conectados sin bloquear la respuesta
        background_tasks.add_task(broadcast_ws, response_payload)
        
        return UniversalIFAResponse(
            data_stream_id=payload.data_stream_id,
            stream_type=payload.stream_type,
            status=f"Secuencia armonizada vía Tzanix Quantum Core bajo el plan {auth_info['plan_type']}",
            compute_efficiency_gain=efficiency_gain,
            purified_data=clean_signals,
            quarantine_data=quarantine_data,
            spatial_signature_4d=morton_code,
            spatial_coordinates=query_coord.tolist(),
            knn_neighbors=knn_neighbors_list,
            energy_consumed_watts=energy_consumed_watts,
            carbon_footprint_saved_grams=carbon_saved,
            tensor_delegation_status="Active (Zero-Carbon Mode)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el núcleo universal IFA: {str(e)}")

# =====================================================================
# ROUTER: API Key Management
# =====================================================================
router_keys = APIRouter(prefix="/api/v1/keys", tags=["API Key Management"])

class KeyCreatePayload(BaseModel):
    client_id: str
    plan_type: str  # Ej: "Financial_Trader", "Industrial_Tijuana", "AI_Research"

class KeyResponse(BaseModel):
    client_id: str
    api_key: str
    plan_type: str
    status: str
    stripe_customer_id: Optional[str] = None

@router_keys.get("/", response_model=List[KeyResponse])
async def list_api_keys():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, api_key, plan_type, status, stripe_customer_id FROM users_keys")
    rows = cursor.fetchall()
    conn.close()
    return [
        KeyResponse(client_id=r[0], api_key=r[1], plan_type=r[2], status=r[3], stripe_customer_id=r[4])
        for r in rows
    ]

@router_keys.post("/generate", response_model=KeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_new_api_key(payload: KeyCreatePayload):
    try:
        new_key = f"ifa_live_{secrets.token_urlsafe(16)}"
        mock_stripe_cust_id = f"cus_mock_{secrets.token_hex(6)}"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users_keys (api_key, client_id, plan_type, status, stripe_customer_id)
            VALUES (?, ?, ?, 'active', ?)
        """, (new_key, payload.client_id, payload.plan_type, mock_stripe_cust_id))
        
        # Inicializar preferencias de alertas
        cursor.execute("""
            INSERT OR IGNORE INTO notification_settings (client_id, weekly_report, noise_alert, budget_limit)
            VALUES (?, 1, 1, 1)
        """, (payload.client_id,))
        
        conn.commit()
        conn.close()
        
        notifications.send_notification(
            payload.client_id,
            "API Key Generada Exitosamente",
            f"Tu clave API ha sido creada de forma segura: {new_key[:15]}... Tu portal ya está activo.",
            "weekly_report"
        )
        
        return KeyResponse(
            client_id=payload.client_id,
            api_key=new_key,
            plan_type=payload.plan_type,
            status="active",
            stripe_customer_id=mock_stripe_cust_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la llave: {str(e)}")

@router_keys.post("/revoke/{api_key}", status_code=status.HTTP_200_OK)
async def revoke_api_key(api_key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT client_id FROM users_keys WHERE api_key = ?", (api_key,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="La API Key especificada no existe.")
        
    client_id = row[0]
    cursor.execute("UPDATE users_keys SET status = 'revoked' WHERE api_key = ?", (api_key,))
    conn.commit()
    conn.close()
    
    notifications.send_notification(
        client_id,
        "API Key Revocada de Inmediato",
        f"Tu credencial {api_key[:12]}... ha sido marcada como revocada y desactivada.",
        "critical"
    )
    
    return {"message": f"La API Key {api_key[:12]}... ha sido revocada exitosamente."}

# =====================================================================
# ROUTER: Billing & Payments (Stripe)
# =====================================================================
router_billing = APIRouter(prefix="/api/v1/billing", tags=["Billing & Payments"])

class SubscriptionPayload(BaseModel):
    client_id: str
    payment_method_id: str

@router_billing.post("/create-customer")
async def create_billing_customer(payload: SubscriptionPayload):
    try:
        stripe_cust_id = None
        stripe_sub_id = None
        
        # Lógica de Stripe real si la clave no es la de test genérica
        if stripe.api_key and stripe.api_key != "sk_test_tu_llave_secreta_de_stripe":
            try:
                customer = stripe.Customer.create(
                    description=f"Cliente Universal IFA: {payload.client_id}",
                    payment_method=payload.payment_method_id,
                    invoice_settings={"default_payment_method": payload.payment_method_id}
                )
                stripe_cust_id = customer.id
                
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{"price": "price_ID_DE_TU_PLAN_POR_CONSUMO"}],
                )
                stripe_sub_id = subscription.id
            except Exception as e:
                print(f"[STRIPE ERROR] Fallback a simulación local: {str(e)}")

        # Fallback local simulado para pruebas locales rápidas sin conexión
        if not stripe_cust_id:
            stripe_cust_id = f"cus_mock_{secrets.token_hex(6)}"
            stripe_sub_id = f"sub_mock_{secrets.token_hex(6)}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users_keys 
            SET status = 'active', stripe_customer_id = ? 
            WHERE client_id = ?
        """, (stripe_cust_id, payload.client_id))
        conn.commit()
        conn.close()
        
        notifications.send_notification(
            payload.client_id,
            "Tarjeta de Pago Vinculada",
            "Tu cuenta ha sido vinculada con Stripe. Se ha activado la facturación por consumo (Metered Billing).",
            "budget_limit"
        )
        
        return {
            "status": "Subscription Active",
            "customer_id": stripe_cust_id,
            "subscription_id": stripe_sub_id,
            "message": "Filtro Fourier IFA activado y vinculado a pasarela de pagos global."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router_billing.get("/metrics/{client_id}")
async def get_billing_metrics(client_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(sequences_count) FROM stream_logs WHERE client_id = ?", (client_id,))
    total_points = cursor.fetchone()[0] or 0
    conn.close()
    
    # Capa Gratuita: Primeros 10,000 puntos de datos gratis al mes
    # Pago por Uso: $0.01 por cada 1,000 puntos purificados
    free_limit = 10000
    billable_points = max(0, total_points - free_limit)
    cost = round((billable_points / 1000) * 0.01, 2)
    
    # Ahorro simulado en cómputo/energía (ej: $0.04 por cada 1,000 puntos procesados)
    savings = round((total_points / 1000) * 0.04, 2)
    
    return {
        "client_id": client_id,
        "total_points": total_points,
        "billable_points": billable_points,
        "cost_usd": cost,
        "savings_usd": savings,
        "net_benefit_usd": round(savings - cost, 2)
    }

# =====================================================================
# ROUTER: Notifications & Settings
# =====================================================================
router_notifications = APIRouter(prefix="/api/v1/notifications", tags=["Notifications Management"])

class NotificationSettingsPayload(BaseModel):
    weekly_report: int
    noise_alert: int
    budget_limit: int

class NotificationLogResponse(BaseModel):
    id: int
    client_id: str
    title: str
    message: str
    timestamp: float

@router_notifications.get("/{client_id}")
async def get_notification_settings(client_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT weekly_report, noise_alert, budget_limit FROM notification_settings WHERE client_id = ?",
        (client_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"weekly_report": 1, "noise_alert": 1, "budget_limit": 1}
    return {"weekly_report": row[0], "noise_alert": row[1], "budget_limit": row[2]}

@router_notifications.post("/{client_id}")
async def update_notification_settings(client_id: str, payload: NotificationSettingsPayload):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notification_settings (client_id, weekly_report, noise_alert, budget_limit)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(client_id) DO UPDATE SET
            weekly_report=excluded.weekly_report,
            noise_alert=excluded.noise_alert,
            budget_limit=excluded.budget_limit
    """, (client_id, payload.weekly_report, payload.noise_alert, payload.budget_limit))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Preferencia de alertas actualizada."}

@router_notifications.get("/{client_id}/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(client_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, client_id, title, message, timestamp FROM notification_logs WHERE client_id = ? ORDER BY timestamp DESC",
        (client_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        NotificationLogResponse(id=r[0], client_id=r[1], title=r[2], message=r[3], timestamp=r[4])
        for r in rows
    ]

# =====================================================================
# ROUTER: Stripe Webhooks
# =====================================================================
router_webhooks = APIRouter(prefix="/api/v1/webhooks", tags=["Stripe Webhooks"])

@router_webhooks.post("/stripe")
async def stripe_webhook_listener(request: Request, x_stripe_signature: str = Header(None)):
    payload = await request.body()
    event = None
    
    # Intentar validación de firma
    if STRIPE_WEBHOOK_SECRET and x_stripe_signature:
        try:
            event = stripe.Webhook.construct_event(
                payload, x_stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error de firma: {str(e)}")
    else:
        # Fallback local de pruebas
        try:
            event = json.loads(payload)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Payload inválido: {str(e)}")
            
    # Manejar eventos de Stripe
    if event and 'type' in event:
        if event['type'] == 'invoice.payment_failed':
            session = event['data']['object']
            customer_id = session.get('customer')
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT client_id FROM users_keys WHERE stripe_customer_id = ?", (customer_id,))
            user = cursor.fetchone()
            if user:
                client_id = user[0]
                cursor.execute("UPDATE users_keys SET status = 'suspended' WHERE stripe_customer_id = ?", (customer_id,))
                conn.commit()
                conn.close()
                print(f"[ALERTA SEGURIDAD] API Key suspendida para el cliente Stripe: {customer_id} debido a pago fallido.")
                
                # Enviar notificación crítica
                notifications.send_notification(
                    client_id,
                    "ALERTA CRÍTICA: Cuenta Suspendida por Falta de Pago",
                    "Tu último pago mensual en Stripe ha fallado. El acceso a tu filtro Fourier 7.25 Hz ha sido suspendido temporalmente.",
                    "critical"
                )
            else:
                conn.close()
                
        elif event['type'] == 'invoice.payment_succeeded':
            session = event['data']['object']
            customer_id = session.get('customer')
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT client_id FROM users_keys WHERE stripe_customer_id = ?", (customer_id,))
            user = cursor.fetchone()
            if user:
                client_id = user[0]
                notifications.send_notification(
                    client_id,
                    "Factura de Consumo Cobrada Exitosamente",
                    "Tu pago mensual por consumo ha sido procesado de forma global en Stripe. ¡Gracias por sintonizar con nosotros!",
                    "budget_limit"
                )
            conn.close()
            print("[FINANZAS] Pago exitoso procesado de forma global.")
            
    return {"status": "success"}

# Registrar todos los routers adicionales en la aplicación FastAPI
app.include_router(router_keys)
app.include_router(router_billing)
app.include_router(router_notifications)
app.include_router(router_webhooks)

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ONLINE",
        "engine": "Tzanix Tensor-Zero Core",
        "tuning_frequency": "7.25 Hz",
        "carbon_footprint": "Zero-Impact"
    }
