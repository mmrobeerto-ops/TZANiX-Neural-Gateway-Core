import os
import sys
import platform
import subprocess
import hashlib
import hmac
import base64
import json
import time

# Llave maestra del fabricante para la firma criptográfica de licencias
SECRET_KEY = b"TZANIX_SECRET_SECURITY_KEY_2026_MASTER"

def get_hardware_uuid():
    """
    Recupera de forma segura el identificador único físico (UUID) de la placa base
    o del procesador según el sistema operativo del host.
    """
    system = platform.system().lower()
    uuid = "UNKNOWN_HARDWARE_UUID"
    try:
        if "windows" in system:
            # Ejecutar WMIC para extraer el UUID físico de la BIOS/Motherboard
            out = subprocess.check_output("wmic csproduct get uuid", shell=True)
            lines = [line.strip() for line in out.decode(errors="ignore").splitlines() if line.strip()]
            if len(lines) > 1:
                uuid = lines[1]
        elif "linux" in system:
            # Buscar el UUID físico del producto o el ID de la máquina virtual/física
            for path in ["/sys/class/dmi/id/product_uuid", "/etc/machine-id", "/var/lib/dbus/machine-id"]:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        uuid = f.read().strip()
                        break
        elif "darwin" in system:
            # Obtener UUID de hardware en macOS
            out = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice", shell=True)
            for line in out.decode(errors="ignore").splitlines():
                if "IOPlatformUUID" in line:
                    uuid = line.split("=")[1].replace('"', "").strip()
                    break
    except Exception:
        pass
    
    # Sanitizar quitando guiones, espacios y convirtiendo a mayúsculas
    return uuid.replace("-", "").replace(" ", "").upper().strip()

def generate_license_token(uuid, client_id, expiry_days=30):
    """
    Helper para generar un token de activación firmado con HMAC-SHA256.
    """
    expiry_time = int(time.time()) + (expiry_days * 86400)
    payload = {
        "uuid": uuid,
        "client_id": client_id,
        "expiry": expiry_time
    }
    payload_json = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_json.encode()).decode()
    
    # Calcular la firma digital de los datos
    signature = hmac.new(SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
    
    # Retornar el token compuesto: payload_base64.firma
    return f"{payload_b64}.{signature}"

def verify_license_token(token_str):
    """
    Verifica si una firma de licencia es válida, si coincide con el hardware actual
    y si sigue dentro del periodo de vigencia.
    """
    try:
        parts = token_str.strip().split(".")
        if len(parts) != 2:
            return False, "Formato de licencia inválido."
        
        payload_b64, signature = parts
        
        # Validar integridad y autenticidad del token
        expected_sig = hmac.new(SECRET_KEY, payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return False, "Firma inválida (El archivo de licencia ha sido modificado)."
        
        # Decodificar el payload JSON
        payload_json = base64.b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)
        
        # Validar vinculación a hardware
        current_uuid = get_hardware_uuid()
        if payload["uuid"] != current_uuid:
            return False, f"ID de hardware incorrecto.\n  Registrado: {payload['uuid']}\n  Equipo Actual: {current_uuid}"
        
        # Validar fecha de expiración
        if time.time() > payload["expiry"]:
            return False, "La licencia ha expirado."
        
        return True, payload
    except Exception as e:
        return False, f"Falla en verificación: {str(e)}"
