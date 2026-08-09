FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema operativo (para compilar SciPy/Numpy si es necesario)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y reinstalar dependencias optimizadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar el núcleo de la aplicación
COPY . .

# Exponer el puerto de la API
EXPOSE 8000

# Capa 1 y 2 activadas: Ejecutar con Gunicorn gestionando múltiples Uvicorn workers
# Esto multiplica el procesamiento por 4 núcleos, evadiendo el GIL de Python
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
