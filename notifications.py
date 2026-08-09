import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "fourier_ifa.db")

def send_notification(client_id: str, title: str, message: str, notification_type: str = "critical") -> bool:
    """
    Simula el envío de correos electrónicos en formato HTML premium (oscuro y dorado).
    Registra el historial de alertas de forma permanente en `notification_logs`.
    
    types: "weekly_report", "noise_alert", "budget_limit", "critical"
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Comprobar si el cliente tiene habilitado este tipo de alertas en notification_settings
    if notification_type != "critical":
        cursor.execute(
            f"SELECT {notification_type} FROM notification_settings WHERE client_id = ?",
            (client_id,)
        )
        setting = cursor.fetchone()
        
        # Si el cliente tiene desactivadas las alertas de este tipo, salimos
        if setting and setting[0] == 0:
            conn.close()
            print(f"[NOTIFICACIÓN OMITIDA] Cliente: {client_id} | Tipo: {notification_type} desactivado.")
            return False

    # 2. Registrar el log de la notificación en SQLite
    cursor.execute(
        "INSERT INTO notification_logs (client_id, title, message, timestamp) VALUES (?, ?, ?, ?)",
        (client_id, title, message, time.time())
    )
    conn.commit()
    conn.close()

    # 3. Diseñar y renderizar el correo HTML minimalista en consola
    html_email_template = f"""
    +========================================================================+
    |                        FOURIER IFA NOTIFICATIONS                       |
    +========================================================================+
    |  DE: infra@fourierifa.ai                                               |
    |  PARA: client_{client_id.lower()}@fourierifa.io                        |
    |  ASUNTO: {title}                                                       |
    +------------------------------------------------------------------------+
    |                                                                        |
    |   [ FOURIER IFA ] - Capa de Infraestructura de Datos Universal        |
    |                                                                        |
    |   Estimado {client_id},                                                |
    |                                                                        |
    |   Se ha registrado un evento relevante en tu cuenta:                   |
    |                                                                        |
    |   >> {message}                                                         |
    |                                                                        |
    |   Métrica de sintonización actual: 7.25 Hz                             |
    |                                                                        |
    |   © 2026 Fourier IFA.                                                  |
    +========================================================================+
    """
    print(html_email_template)
    return True
