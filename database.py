import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "fourier_ifa.db")

def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa las tablas de la base de datos y agrega datos de semilla si está vacía."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Crear tabla de API Keys
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        api_key TEXT PRIMARY KEY,
        client_profile TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    # Crear tabla de logs de uso
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_stream_id TEXT NOT NULL,
        client_profile TEXT NOT NULL,
        compute_efficiency_gain REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    
    # Insertar semillas si la tabla de llaves está vacía
    cursor.execute("SELECT COUNT(*) FROM api_keys")
    if cursor.fetchone()[0] == 0:
        seed_keys = [
            ("IFA-KEY-FINANCIAL-TRADER", "Financial_Trader", 1),
            ("IFA-KEY-INDUSTRIAL-CLIENT", "Industrial_Client", 1),
            ("IFA-KEY-AI-RESEARCH", "AI_Research", 1)
        ]
        cursor.executemany("INSERT INTO api_keys (api_key, client_profile, is_active) VALUES (?, ?, ?)", seed_keys)
        conn.commit()
        print("Base de datos inicializada y llaves semilla creadas correctamente.")
        
    conn.close()

def verify_key(api_key: str) -> Optional[str]:
    """
    Verifica si una llave existe y está activa en la base de datos.
    Retorna el perfil del cliente si es válida, o None si no lo es.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_profile FROM api_keys WHERE api_key = ? AND is_active = 1", (api_key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def log_usage(data_stream_id: str, client_profile: str, efficiency_gain: float):
    """Registra una llamada exitosa al motor universal de purificación de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usage_logs (data_stream_id, client_profile, compute_efficiency_gain) VALUES (?, ?, ?)",
        (data_stream_id, client_profile, efficiency_gain)
    )
    conn.commit()
    conn.close()
