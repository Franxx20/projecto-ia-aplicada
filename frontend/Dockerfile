# Dockerfile multi-stage para React + Vite Frontend
# Optimizado para producción con nginx

# Stage 1: Builder - Build de la aplicación Vite
FROM node:20-alpine AS builder
WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar todas las dependencias (incluidas dev para build)
RUN npm ci

# Copiar código fuente
COPY . .

# Variables de entorno necesarias para build
ENV NODE_ENV=production

# Build de Vite - genera carpeta dist/
RUN npm run build

# Stage 2: Runner - Imagen final optimizada con nginx
FROM nginx:alpine AS runner

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos estáticos compilados desde builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Exponer puerto 4200
EXPOSE 4200

# Health check para verificar que nginx responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:4200/ || exit 1

# Comando por defecto - nginx
CMD ["nginx", "-g", "daemon off;"]