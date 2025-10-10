# Dockerfile multi-stage para Next.js Frontend
# Optimizado para output standalone y Docker

# Stage 1: Dependencies - Instalar solo dependencias de producción
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias (solo producción para optimizar tamaño)
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Builder - Build de la aplicación Next.js
FROM node:20-alpine AS builder
WORKDIR /app

# Copiar dependencias desde stage anterior
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Variables de entorno necesarias para build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Instalar todas las dependencias (incluidas dev para build)
RUN npm ci

# Build de Next.js con output standalone
RUN npm run build

# Stage 3: Runner - Imagen final optimizada
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=4200
ENV HOSTNAME=0.0.0.0

# Crear usuario no-root para seguridad
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copiar archivos públicos
COPY --from=builder /app/public ./public

# Copiar standalone output (Next.js genera estructura optimizada)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Cambiar a usuario no-root
USER nextjs

# Exponer puerto configurado
EXPOSE 4200

# Health check para verificar que Next.js responde
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:4200/api/health', (r) => {if(r.statusCode !== 200) throw new Error(r.statusCode)})"

# Comando por defecto - Next.js standalone server
CMD ["node", "server.js"]