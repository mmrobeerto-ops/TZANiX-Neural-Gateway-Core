import sqlite3
import asyncio
import json
import logging
import subprocess
import os

class TzanixShield:
    def __init__(self, db_path="singularity.db"):
        """
        Inicializa el TzanixShield.
        Conecta a la base de datos, activa el modo WAL, crea la cola en RAM
        y enciende al Demonio Guardián.
        """
        self.db_path = db_path
        self.queue = asyncio.Queue()
        
        # 1. Conectar a la BD y activar modo WAL
        self._init_db()
        
        # 2. Encender el Demonio Guardián
        self.daemon_task = asyncio.create_task(self._guardian_daemon())
        logging.info("TzanixShield inicializado: DB (WAL mode) lista, Demonio Guardián activo.")

    def _init_db(self):
        """Configura SQLite en modo WAL y crea la tabla de logs."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quantum_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_data TEXT,
                    output_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    async def _guardian_daemon(self):
        """
        Demonio Guardián: corre en segundo plano esperando logs en la RAM Queue
        y persistiéndolos de forma segura en SQLite.
        """
        while True:
            log_entry = await self.queue.get()
            if log_entry is None:
                self.queue.task_done()
                break
            try:
                await asyncio.to_thread(self._write_to_db, log_entry)
            except Exception as e:
                logging.error(f"Error en Demonio Guardián al escribir a BD: {e}")
            finally:
                self.queue.task_done()

    def _write_to_db(self, log_entry):
        """Inserta un registro en la base de datos (operación bloqueante)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO quantum_logs (input_data, output_data) VALUES (?, ?)", 
                (log_entry.get("input"), log_entry.get("output"))
            )

    def _rust_bridge_executor(self, datos):
        """
        Llama al motor de Rust ejecutando el binario compilado.
        Asumimos que el proyecto Rust ya está compilado con `cargo build --release`.
        Se le puede pasar argumentos, pero en este ejemplo usamos cargo run directo.
        """
        try:
            # Ejecutamos el motor cuántico en Rust y pedimos la salida en JSON
            exe_path = os.path.join(os.path.dirname(__file__), "tzanix-singularity-core")
            result = subprocess.run(
                [exe_path, "--json"], 
                capture_output=True, 
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            
            # Buscar el inicio del JSON (por si cargo imprime avisos de compilación antes)
            start_idx = output.find("[")
            if start_idx != -1:
                json_str = output[start_idx:]
                particles = json.loads(json_str)
                return {"status": "success", "particles": particles}
            else:
                return {"status": "error", "message": "No se encontro JSON en la salida de Rust"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def process(self, datos):
        """
        Método principal que utiliza el usuario o la API.
        Ejecuta el puente a Rust en hilo secundario, encola el log y retorna el JSON.
        """
        # 1. Ejecutar el puente a Rust en un hilo secundario
        resultado = await asyncio.to_thread(self._rust_bridge_executor, datos)
        
        # 2. Empujar el log a la Cola en RAM
        log_entry = {
            "input": json.dumps(datos),
            "output": json.dumps(resultado)
        }
        await self.queue.put(log_entry)
        
        # 3. Devolver la respuesta purificada
        return resultado

    async def shutdown(self):
        """Apaga el demonio de forma segura."""
        await self.queue.put(None)
        await self.daemon_task
        logging.info("TzanixShield apagado correctamente.")
