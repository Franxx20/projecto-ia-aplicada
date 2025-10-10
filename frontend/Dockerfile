# Dockerfile multi-stage para React Frontend con Vite

# Stage 1: Build de la aplicación React
FROM node:18-alpine AS build

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci && npm cache clean --force

# Copiar código fuente
COPY . .

# Build de la aplicación con Vite
RUN npm run build

# Stage 2: Servir con Nginx
FROM nginx:alpine

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos built desde stage anterior (Vite genera en /dist)
COPY --from=build /app/dist /usr/share/nginx/html

# Crear directorios con permisos apropiados para nginx
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Comando por defecto (nginx se ejecuta con el usuario nginx por defecto)
CMD ["nginx", "-g", "daemon off;"]