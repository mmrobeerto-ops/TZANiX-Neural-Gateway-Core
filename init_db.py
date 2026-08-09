import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), "fourier_ifa.db")

def init_db():
    print(f"Abriendo conexión con la base de datos en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Eliminar tablas antiguas para asegurar una alineación limpia
    print("Limpiando tablas anteriores si existen...")
    cursor.execute("DROP TABLE IF EXISTS users_keys")
    cursor.execute("DROP TABLE IF EXISTS stream_logs")
    cursor.execute("DROP TABLE IF EXISTS notification_settings")
    cursor.execute("DROP TABLE IF EXISTS notification_logs")
    
    # 2. Crear tabla users_keys con columna stripe_customer_id y status suspendida
    print("Creando tabla users_keys...")
    cursor.execute("""
    CREATE TABLE users_keys (
        api_key TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        plan_type TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('active', 'revoked', 'suspended')),
        stripe_customer_id TEXT
    )
    """)
    
    # 3. Crear tabla stream_logs
    print("Creando tabla stream_logs...")
    cursor.execute("""
    CREATE TABLE stream_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        data_stream_id TEXT NOT NULL,
        stream_type TEXT NOT NULL,
        sequences_count INTEGER NOT NULL,
        efficiency_gain REAL NOT NULL,
        timestamp REAL NOT NULL
    )
    """)

    # 4. Crear tabla notification_settings
    print("Creando tabla notification_settings...")
    cursor.execute("""
    CREATE TABLE notification_settings (
        client_id TEXT PRIMARY KEY,
        weekly_report INTEGER DEFAULT 1,
        noise_alert INTEGER DEFAULT 1,
        budget_limit INTEGER DEFAULT 1
    )
    """)

    # 5. Crear tabla notification_logs
    print("Creando tabla notification_logs...")
    cursor.execute("""
    CREATE TABLE notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp REAL NOT NULL
    )
    """)
    
    conn.commit()
    
    # 6. Insertar llaves semilla con IDs de clientes de Stripe
    seed_keys = [
        ("ifa_live_btc_trader_99x", "Financial_Trader", "Financial_Trader", "active", "cus_test_btc123"),
        ("ifa_live_industrial_plc_01z", "Industrial_Client", "Industrial_Tijuana", "active", "cus_test_ind456"),
        ("ifa_live_ai_research_05w", "AI_Research", "AI_Research", "active", "cus_test_ai789")
    ]
    
    print("Insertando llaves semilla de prueba...")
    cursor.executemany(
        "INSERT INTO users_keys (api_key, client_id, plan_type, status, stripe_customer_id) VALUES (?, ?, ?, ?, ?)",
        seed_keys
    )

    # 7. Insertar configuraciones semilla de notificaciones
    seed_settings = [
        ("Financial_Trader", 1, 1, 1),
        ("Industrial_Client", 1, 0, 1),
        ("AI_Research", 1, 1, 0)
    ]
    print("Insertando configuraciones semilla de alertas...")
    cursor.executemany(
        "INSERT INTO notification_settings (client_id, weekly_report, noise_alert, budget_limit) VALUES (?, ?, ?, ?)",
        seed_settings
    )

    # 8. Insertar logs semilla de notificaciones
    seed_logs = [
        ("Financial_Trader", "Conexión WebSocket Establecida", "Suscripción activa al feed de cotización de Binance. Filtro Fourier a 7.25 Hz funcionando correctamente.", time.time() - 3600),
        ("Industrial_Client", "Límite de Consumo Gratuito al 20%", "Has consumido 2,000 secuencias este periodo bajo el plan Industrial_Tijuana.", time.time() - 7200)
    ]
    print("Insertando logs semilla de alertas...")
    cursor.executemany(
        "INSERT INTO notification_logs (client_id, title, message, timestamp) VALUES (?, ?, ?, ?)",
        seed_logs
    )
    
    conn.commit()
    conn.close()
    print("Base de datos inicializada y tablas con semillas creadas correctamente.")

if __name__ == "__main__":
    init_db()
