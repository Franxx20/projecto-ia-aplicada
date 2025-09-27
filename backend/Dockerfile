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

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root para seguridad
RUN addgroup --system appgroup && adduser --system --group appuser

# Copiar código de la aplicación
COPY . .

# Cambiar permisos al usuario no-root
RUN chown -R appuser:appgroup /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check - usar nuestro endpoint de salud
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/salud || exit 1

# Comando por defecto (sin reload para producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]