import sqlite3

try:
    conn = sqlite3.connect('fourier_ifa.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users_keys (api_key, client_id, plan_type, status, stripe_customer_id)
        VALUES ('tzx_live_godmode_2026', 'godmode_tester', 'Enterprise', 'active', 'mock_godmode')
    """)
    conn.commit()
    conn.close()
    print("API Key tzx_live_godmode_2026 instalada correctamente.")
except Exception as e:
    print(f"Error: {e}")
