# ==========================================
# FASE 1: BUILDER (Compilación del Núcleo Rust)
# ==========================================
FROM rust:1.80-slim AS rust_builder
WORKDIR /usr/src/tzanix-core
COPY Cargo.toml ./
COPY src ./src
# Compilamos el binario para máximo rendimiento
RUN cargo build --release

# ==========================================
# FASE 2: Ofuscación Python (Cython)
# ==========================================
FROM python:3.11-slim AS py_builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc python3-dev
RUN pip install cython
COPY api.py shield.py public.pem ./
RUN cythonize -i -3 api.py shield.py

# ==========================================
# FASE 3: PRODUCCIÓN (Zero-Source)
# ==========================================
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt PyJWT cryptography

# Copiar el binario CERRADO desde la Fase 1 (Rust)
COPY --from=rust_builder /usr/src/tzanix-core/target/release/tzanix-neural-gateway-core /app/tzanix-neural-gateway-core

# Copiar SOLO los binarios ofuscados desde la Fase 2 (Cython)
COPY --from=py_builder /build/*.so ./
COPY --from=py_builder /build/public.pem ./

RUN chmod +x /app/tzanix-neural-gateway-core

EXPOSE 8003
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]
