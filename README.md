# Tzanix Tensor-Zero Core

Este proyecto implementa la infraestructura universal del motor matemático **Tzanix Tensor-Zero Core**. Actúa como una capa previa de procesamiento de datos secuenciales a alta velocidad, utilizando una simulación de **arquitectura de tensores cuánticos** para sintonizar y filtrar el ruido caótico a una frecuencia exacta de **7.25 Hz**.

Su diseño principal radica en la **eficiencia extrema**: delega la computación matricial pesada a una aproximación tensorial, logrando que el consumo de CPU baje drásticamente. Esto permite que los nodos Edge de Tzanix requieran una energía cercana a cero y mantengan una **huella de carbono ultra baja** (Zero-Carbon Mode).

El sistema es completamente agnóstico al dominio de datos de entrada: procesa con la misma eficacia series temporales financieras (como la volatilidad de Bitcoin), logs de vibración industrial, telemetría logística, o flujos secuenciales para modelos de Inteligencia Artificial.

## Estructura del Proyecto

- `main.py`: Código principal que contiene la aplicación FastAPI, los esquemas de datos `UniversalDataPayload` y `UniversalIFAResponse` (ahora con métricas energéticas y de huella de carbono), la lógica del motor `TzanixQuantumCore`, y los endpoints de purificación y salud.
- `requirements.txt`: Dependencias del sistema (FastAPI, Uvicorn, NumPy, Requests).
- `test_client.py`: Script cliente para la validación automatizada de la purificación y medición de eficiencia.

## Requisitos Previos

Necesitas tener Python instalado en tu máquina. Se recomienda usar un entorno virtual.

## Instalación y Configuración

1. Instala las dependencias necesarias ejecutando el siguiente comando:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el servidor FastAPI de forma local:
   ```bash
   uvicorn main:app --reload
   ```
   El servidor estará disponible en [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. Puedes abrir tu navegador y consultar la documentación interactiva (Swagger UI) en:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Ejecución de Pruebas

Para validar los escenarios de purificación de datos y visualizar el ahorro de la huella de carbono, ejecuta en otra consola:
```bash
python test_client.py
```
El script generará señales de prueba ruidosas, consultará a la API universal y mostrará los resultados de purificación junto a la métrica de ganancia de eficiencia de cómputo del motor cuántico.
