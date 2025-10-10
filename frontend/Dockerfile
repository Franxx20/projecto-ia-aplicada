# Dockerfile multi-stage para Next.js Frontend
# Optimizado para producción con standalone output

# Stage 1: Dependencias - Instalar todas las dependencias
FROM node:20-alpine AS deps
WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar TODAS las dependencias (necesarias para build)
RUN npm ci && npm cache clean --force

# Stage 2: Builder - Build de la aplicación Next.js
FROM node:20-alpine AS builder
WORKDIR /app

# Copiar dependencias desde deps
COPY --from=deps /app/node_modules ./node_modules

# Copiar código fuente
COPY . .

# Variables de entorno necesarias para build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build de Next.js con standalone output
RUN npm run build

# Stage 3: Runner - Imagen final optimizada
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Crear usuario no-root para seguridad
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copiar archivos necesarios para standalone
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Cambiar a usuario no-root
USER nextjs

# Exponer puerto 4200
EXPOSE 4200

# Variables de entorno de runtime
ENV PORT=4200
ENV HOSTNAME="0.0.0.0"

# Health check para verificar que Next.js responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:4200/', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Comando por defecto - Next.js standalone server
CMD ["node", "server.js"]