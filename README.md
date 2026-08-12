# TZANiX Neural Gateway Core

**Motor de Purificación de Datasets y Telemetría para Modelos de IA (LLMs)**

Este repositorio contiene la infraestructura del motor de procesamiento backend **TZANiX Neural Gateway**. Actúa como la puerta de enlace neuronal (Gateway) de alta velocidad que purifica flujos de datos entrantes utilizando algoritmos basados en el **TZANiX Quantum Core (Rust)** antes de enviarlos a clusters de inferencia (NVIDIA H100).

## La Misión de Negocio (FinOps & ESG)

El ruido en los datasets cuesta millones de dólares en poder de cómputo GPU desperdiciado y emisiones de CO2 innecesarias. TZANiX intercepta estos datos crudos, aplica un filtro matemático tensorial, y descarta los vectores basura.
Esto permite:
- **Reducción de Consumo GPU:** Menos TFLOPS desperdiciados procesando ruido.
- **Eficiencia ESG (Impacto Ambiental):** Menor disipación térmica y huella de carbono ultra-baja.
- **Altísimo Rendimiento:** Arquitectura asíncrona de FastAPI + Rust capaz de soportar alta frecuencia (WebSockets).

## Despliegue en Producción (Docker)

El motor está empaquetado para despliegues de grado empresarial (Enterprise) en máquinas virtuales dedicadas (AWS EC2, DigitalOcean Droplets).
Utiliza **Gunicorn** con **Uvicorn Workers** para evadir el GIL de Python y exprimir todos los núcleos de la CPU.

```bash
# Construir e iniciar el contenedor en segundo plano (Modo Producción)
docker-compose up -d --build
```

El servidor estará escuchando en el puerto `8000`.

## Requisitos y Configuración Local
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar localmente (Desarrollo): `uvicorn main:app --reload`
3. Documentación API (Swagger): `http://127.0.0.1:8000/docs`

## Tecnologías Principales
- **FastAPI / Python 3.11**
- **Rust** (Rutinas críticas de purificación vía FFIs)
- **SQLite WAL Mode** (Escritura en segundo plano sin bloqueos)
- **Docker & Gunicorn**
