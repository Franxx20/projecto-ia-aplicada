# Dockerfile para FastAPI Backend
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# IMPORTANTE: Copiar solo requirements primero (mejor caching)
# Si requirements.txt no cambia, Docker usará cache
COPY requirements.txt .

# Instalar dependencias de Python
# Esta capa se cachea si requirements.txt no cambia
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para seguridad
RUN addgroup --system appgroup && adduser --system --group appuser

# Ahora copiar el resto del código
# Los cambios en el código no invalidarán el cache de dependencias
COPY . .

# Crear directorios necesarios y cambiar permisos
RUN mkdir -p /app/logs /app/uploads /app/backups && \
    chown -R appuser:appgroup /app

USER appuser

# Exponer puerto
EXPOSE 8000

# Health check mejorado - dar más tiempo al inicio
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (sin reload para producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]