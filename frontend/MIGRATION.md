# 📝 Guía de Migración: Angular → React

## ✅ Cambios Realizados

### 1. **Stack Tecnológico**
- ❌ Angular 17 + Angular CLI
- ✅ React 18 + TypeScript + Vite 5

### 2. **Archivos Principales**

#### Nuevos Archivos (React)
- `src/main.tsx` - Punto de entrada de React
- `src/App.tsx` - Componente principal
- `src/App.test.tsx` - Tests del componente
- `src/setupTests.ts` - Configuración de tests
- `vite.config.ts` - Configuración de Vite
- `tailwind.config.js` - Configuración de Tailwind
- `postcss.config.js` - Configuración de PostCSS
- `.eslintrc.cjs` - Configuración de ESLint

#### Archivos Eliminados/Obsoletos (Angular)
- `angular.json` - Configuración de Angular CLI
- `tsconfig.app.json` - TypeScript config de Angular
- `src/app/app.component.ts` - Componente de Angular
- `src/app/app.module.ts` - Módulo de Angular
- `src/main.ts` - Punto de entrada de Angular
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

#### Después (React)
```
frontend/src/
  components/
  pages/
  hooks/
  context/
  services/
  lib/
  models/
  utils/
  assets/
  config/
```

### 4. **Scripts de NPM**

#### Antes (Angular)
```json
{
  "start": "ng serve --host 0.0.0.0 --port 4200 --disable-host-check",
  "build": "ng build"
}
```

#### Después (React + Vite)
```json
{
  "dev": "vite --host 0.0.0.0 --port 4200",
  "build": "tsc && vite build",
  "test": "vitest"
}
```

### 5. **Testing**

#### Antes (Angular)
- Jasmine + Karma
- `@angular/testing`
- TestBed para configuración

#### Después (React)
- Vitest (compatible con Jest)
- React Testing Library
- Setup más simple y rápido

### 6. **Configuración de Docker**

#### Dockerfile
- Comando de build cambiado de `ng build` a `vite build`
- Directorio de salida sigue siendo `/dist`

#### docker-compose.dev.yml
- Comando de dev cambiado de `npm run start` a `npm run dev`
- Se agregó variable de entorno `VITE_API_URL`

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

- [x] Actualizar `package.json` con dependencias de React
- [x] Crear `vite.config.ts`
- [x] Actualizar `tsconfig.json` para React
- [x] Crear componente `App.tsx`
- [x] Configurar Tailwind CSS
- [x] Actualizar `Dockerfile`
- [x] Actualizar `docker-compose.yml`
- [x] Actualizar `docker-compose.dev.yml`
- [x] Crear tests con Vitest
- [x] Actualizar `README.md`
- [x] Actualizar `.gitignore`
- [x] Actualizar `.dockerignore`
- [x] Crear `.eslintrc.cjs`

## 🎯 Próximos Pasos

### Funcionalidades Recomendadas
1. **React Router** - Para navegación entre páginas
2. **Zustand o Context API** - Para manejo de estado global
3. **React Hook Form** - Para formularios
4. **Axios** - Para llamadas HTTP al backend
5. **Zod** - Para validación de schemas

### Estructura Recomendada
```typescript
// Ejemplo de servicio HTTP
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export default api

// Ejemplo de custom hook
// src/hooks/useAuth.ts
import { useState } from 'react'

export function useAuth() {
  const [user, setUser] = useState(null)
  
  const login = async (email: string, password: string) => {
    // Lógica de login
  }
  
  return { user, login }
}
```

## 🔧 Troubleshooting

### Error: "Cannot find module 'react'"
```bash
rm -rf node_modules package-lock.json
npm install
```

### Error en hot reload de Docker
- Verificar que `usePolling: true` esté en `vite.config.ts`
- Asegurar que el volumen está montado correctamente

### Tests no funcionan
```bash
npm install --save-dev @testing-library/jest-dom vitest jsdom
```

## 📚 Recursos

- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Vitest](https://vitest.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**Nota**: Los archivos de Angular fueron dejados temporalmente para referencia. Se recomienda eliminarlos después de verificar que todo funciona correctamente.
