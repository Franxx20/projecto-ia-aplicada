# 📝 Guía de Migración: Angular → Next.js

## ✅ Cambios Realizados

### 1. **Stack Tecnológico**
- ❌ Angular 17 + Angular CLI
- ❌ React 18 + TypeScript + Vite 5
- ✅ Next.js 15 + React 19 + TypeScript

### 2. **Archivos Principales**

#### Nuevos Archivos (Next.js)
- `app/layout.tsx` - Layout raíz de la aplicación
- `app/page.tsx` - Página principal (Home/Landing)
- `app/globals.css` - Estilos globales
- `next.config.ts` - Configuración de Next.js
- `tailwind.config.ts` - Configuración de Tailwind
- `postcss.config.js` - Configuración de PostCSS
- `.eslintrc.json` - Configuración de ESLint (Next.js)
- `components/ui/` - Componentes UI (shadcn/ui)
- `lib/utils.ts` - Utilidades generales

#### Archivos Eliminados/Obsoletos
- `angular.json` - Configuración de Angular CLI
- `vite.config.ts` - Configuración de Vite
- `index.html` - HTML de entrada (Vite)
- `src/main.tsx` - Punto de entrada de Vite
- `src/App.tsx` - Componente principal de Vite
- `.angular/` - Caché de Angular

### 3. **Estructura de Carpetas**

#### Antes (Angular)
```
frontend/src/
  app/
    components/
    pages/
    services/
    guards/
    interceptors/
    models/
    utils/
  assets/
  environments/
```

#### Después (Next.js - App Router)
```
frontend/
  app/                    # App Router de Next.js
    page.tsx             # Página principal (/)
    layout.tsx           # Layout raíz
    globals.css          # Estilos globales
    login/               # Ruta /login
      page.tsx
    register/            # Ruta /register
      page.tsx
    dashboard/           # Ruta /dashboard
      page.tsx
    api/                 # API Routes (opcional)
  components/            # Componentes reutilizables
    ui/                  # Componentes UI (shadcn)
  lib/                   # Utilidades y helpers
    utils.ts
    auth.service.ts
  models/                # Interfaces TypeScript
  public/                # Assets estáticos
```

### 4. **Scripts de NPM**

#### Antes (Angular)
```json
{
  "start": "ng serve --host 0.0.0.0 --port 4200 --disable-host-check",
  "build": "ng build"
}
```

#### Después (Next.js)
```json
{
  "dev": "next dev --hostname 0.0.0.0 --port 4200",
  "build": "next build",
  "start": "next start --hostname 0.0.0.0 --port 4200",
  "test": "vitest",
  "lint": "next lint"
}
```

### 5. **Testing**

#### Antes (Angular)
- Jasmine + Karma
- `@angular/testing`
- TestBed para configuración

#### Después (Next.js)
- Vitest (compatible con Jest)
- React Testing Library
- @testing-library/jest-dom
- Setup más simple y rápido
- Compatible con componentes de servidor y cliente

### 6. **Configuración de Docker**

#### Dockerfile
- Comando de build cambiado de `ng build` a `next build`
- Directorio de salida es `.next/` y `out/` (para export estático)
- Next.js se ejecuta en modo standalone para optimización

#### docker-compose.dev.yml
- Comando de dev cambiado de `npm run start` a `npm run dev`
- Variables de entorno configuradas con `NEXT_PUBLIC_` prefix para acceso desde cliente
- Soporte para hot reload con Next.js Fast Refresh

## 🚀 Comandos de Desarrollo

### Instalar Dependencias
```bash
cd frontend
npm install
```

### Desarrollo Local (sin Docker)
```bash
npm run dev
# Abre http://localhost:4200
```

### Ejecutar Tests
```bash
npm test              # Tests en watch mode
npm run test:ui       # Tests con interfaz visual
npm run test:coverage # Tests con reporte de cobertura
```

### Build de Producción
```bash
npm run build
npm run preview  # Preview del build
```

### Con Docker
```bash
# Modo desarrollo (hot reload)
./manage.sh dev
# o en Windows: manage.bat dev

# Modo producción
./manage.sh prod
# o en Windows: manage.bat prod
```

## 📋 Checklist de Migración

- [x] Actualizar `package.json` con dependencias de Next.js
- [x] Crear `next.config.ts`
- [x] Actualizar `tsconfig.json` para Next.js
- [x] Crear estructura `app/` con App Router
- [x] Crear `app/layout.tsx` y `app/page.tsx`
- [x] Configurar Tailwind CSS para Next.js
- [x] Actualizar `Dockerfile` para Next.js
- [x] Actualizar `docker-compose.yml`
- [x] Actualizar `docker-compose.dev.yml`
- [x] Configurar tests con Vitest
- [x] Actualizar `README.md`
- [x] Actualizar `.gitignore` (agregar `.next/`)
- [x] Actualizar `.dockerignore`
- [x] Configurar ESLint con eslint-config-next
- [x] Eliminar archivos obsoletos de Vite y Angular

## 🎯 Próximos Pasos

### Funcionalidades Recomendadas
1. **Next.js App Router** - Sistema de enrutamiento basado en archivos (ya implementado)
2. **Server Components** - Para mejor performance y SEO
3. **React Hook Form** - Para formularios con validaciones
4. **Axios** - Para llamadas HTTP al backend FastAPI
5. **Zod** - Para validación de schemas
6. **NextAuth.js** - Para autenticación (opcional)
7. **shadcn/ui** - Componentes UI ya configurados

### Estructura Recomendada
```typescript
// Ejemplo de servicio HTTP
// lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
})

export default api

// Ejemplo de servicio de autenticación
// lib/auth.service.ts
export const authService = {
  async login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },
  
  async register(userData: any) {
    const response = await api.post('/auth/register', userData)
    return response.data
  }
}

// Ejemplo de página con Server Component
// app/dashboard/page.tsx
export default async function DashboardPage() {
  // Esto se ejecuta en el servidor
  const data = await fetch('http://localhost:8000/api/data')
  
  return <div>Dashboard</div>
}
```

## 🔧 Troubleshooting

### Error: "Cannot find module 'react'"
```bash
rm -rf node_modules package-lock.json
npm install
```

### Error en hot reload de Docker
- Next.js Fast Refresh debería funcionar automáticamente
- Verificar que el volumen está montado correctamente en docker-compose
- Asegurar que el puerto 4200 esté disponible

### Error: "Module not found" en imports
- Verificar que `@/*` esté configurado en `tsconfig.json`
- Next.js usa `@/` como alias para la raíz del proyecto

### Tests no funcionan
```bash
npm install --save-dev @testing-library/jest-dom vitest jsdom @testing-library/react
```

### Build falla en Docker
- Verificar que `next.config.ts` tenga la configuración correcta
- Revisar que no haya imports de `import.meta.env` (usar `process.env.NEXT_PUBLIC_` en su lugar)

## 📚 Recursos

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [React Testing Library](https://testing-library.com/react)
- [Vitest](https://vitest.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)

---

**Nota**: Los archivos de Angular y Vite fueron eliminados después de verificar que Next.js funciona correctamente. La migración a Next.js proporciona mejor SEO, Server-Side Rendering, y optimizaciones automáticas de rendimiento.
