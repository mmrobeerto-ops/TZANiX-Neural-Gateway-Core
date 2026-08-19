from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager
from shield import TzanixShield
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

# Instancia global del Shield
shield = None

import os
import sys
import jwt
from cryptography.hazmat.primitives import serialization

def verify_license():
    api_key = os.getenv("TZANIX_API_KEY")
    if not api_key:
        logging.error("FATAL: TZANIX_API_KEY environment variable is missing.")
        sys.exit(1)
        
    try:
        # Extraer el JWT quitando el prefijo (ej: tzx_sg_)
        token = "_".join(api_key.split("_")[2:]) if api_key.startswith("tzx_") else api_key
        
        with open("public.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
            
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        logging.info(f"Licencia Válida [3 Meses]. Cliente: {payload.get('email')}")
    except jwt.ExpiredSignatureError:
        logging.error("FATAL: TZANIX License Expired. Trial period is over.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"FATAL: Invalid TZANIX License Signature. Intrusion detected. {e}")
        sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Verificar criptográficamente la licencia offline
    verify_license()
    
    # 2. Inicializar el Shield al arrancar el servidor
    global shield
    shield = TzanixShield("Neural Gateway.db")
    logging.info("TzanixShield inicializado en FastAPI.")
    yield
    # Apagar el demonio de forma limpia al detener el servidor
    if shield:
        await shield.shutdown()
        logging.info("TzanixShield detenido.")

app = FastAPI(title="Tzanix Neural Gateway Core API", lifespan=lifespan)

class QuantumRequest(BaseModel):
    # Aquí puedes definir los parámetros que acepta tu motor cuántico.
    # Por ahora aceptamos cualquier diccionario/JSON libre.
    datos: dict

@app.get("/")
def read_root():
    return {"message": "Tzanix Quantum Core Engine is running."}

@app.post("/process")
async def process_quantum_data(req: QuantumRequest):
    """
    Endpoint principal. Recibe datos, los pasa por TzanixShield 
    (que ejecuta Rust de fondo y encola logs en RAM a SQLite), 
    y devuelve la onda purificada.
    """
    if not shield:
        return {"status": "error", "message": "Shield no está inicializado"}
        
    resultado = await shield.process(req.datos)
    return resultado
