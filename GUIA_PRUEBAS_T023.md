# 🎉 T-023: Implementación Completada - Guía de Pruebas

## ✅ Estado de Implementación

### Backend ✅ COMPLETADO
- ✅ Schema `AgregarPlantaDesdeIdentificacionRequest`
- ✅ Endpoint POST `/api/plantas/agregar-desde-identificacion`
- ✅ Service method `agregar_desde_identificacion()`
- ⏳ Tests creados (pendiente fixture de BD)

### Frontend ✅ COMPLETADO
- ✅ Types `AgregarPlantaRequest`, `PlantaUsuario`, `PlantaResponse`, `EspecieResponse`
- ✅ Servicios `agregarPlantaAlJardin()` y `obtenerMisPlantas()`
- ✅ Página resultados con carousel y confirmación
- ✅ Dashboard con sección "Mis Plantas Identificadas"

---

## 🚀 Cómo Probar la Funcionalidad

### 1. Verificar que los contenedores están corriendo

```powershell
docker-compose -f docker-compose.dev.yml ps
```

**Esperado:**
- ✅ backend: Up (healthy) - puerto 8000
- ✅ frontend: Up - puerto 4200
- ✅ db: Up (healthy) - puerto 5432
- ✅ azurite: Up - puerto 10000-10002

### 2. Verificar Backend API

Abrir en navegador: http://localhost:8000/docs

**Endpoints a verificar:**
1. **POST `/api/plantas/agregar-desde-identificacion`**
   - Requiere autenticación (JWT Bearer token)
   - Body:
     ```json
     {
       "identificacion_id": 123,
       "nombre_personalizado": "Mi Potus",
       "notas": "Primera planta",
       "ubicacion": "Balcón"
     }
     ```

2. **GET `/api/plantas`**
   - Requiere autenticación
   - Retorna array de plantas del usuario

### 3. Probar Frontend - Flujo Completo

#### Paso 1: Login
1. Abrir http://localhost:4200
2. Si no tienes cuenta:
   - Ir a `/register`
   - Crear usuario con email y contraseña
3. Login con credenciales

#### Paso 2: Identificar Planta
1. Ir a `/identificar` o click en botón "Identificar Planta"
2. **Opción A: Subir desde archivo**
   - Click en "Subir Imágenes"
   - Seleccionar 1-5 imágenes de plantas
   - Para cada imagen, seleccionar órgano:
     * `leaf` - Hoja
     * `flower` - Flor
     * `fruit` - Fruto
     * `bark` - Corteza
     * `auto` - Automático (IA decide)
   - Click "Identificar"

3. **Opción B: Usar imágenes de prueba**
   - Si hay imágenes ya subidas, seleccionarlas
   - Especificar órganos
   - Click "Identificar"

#### Paso 3: Ver Resultados
1. La página `/identificar/resultados?identificacionId=X` se abrirá automáticamente
2. **Verificar que se muestra:**
   - ✅ Carousel/grid con las imágenes subidas
   - ✅ Card informativa sobre niveles de confianza
   - ✅ Lista de especies identificadas (hasta 10 resultados)
   - ✅ Para cada especie:
     * Badge con % de confianza
     * Nombre científico (italic)
     * Nombres comunes
     * Género y familia
     * Barra de progreso de confianza
     * Enlaces a GBIF y POWO
     * **Botón "Confirmar esta planta"**

#### Paso 4: Confirmar Planta
1. En la especie que mejor coincida, click en **"Confirmar esta planta"**
2. **Verificar:**
   - ✅ Botón cambia a loading ("Agregando...")
   - ✅ Aparece toast de éxito: "¡Planta agregada!"
   - ✅ Botón cambia a verde con check: "Confirmado"
   - ✅ Después de 2 segundos, redirección automática al dashboard

#### Paso 5: Ver Dashboard
1. La página `/dashboard` se carga automáticamente
2. **Verificar sección "Mis Plantas Identificadas":**
   - ✅ Título: "Mis Plantas Identificadas"
   - ✅ Subtítulo: "Plantas agregadas desde identificaciones"
   - ✅ Badge con contador de plantas
   - ✅ Grid de cards de plantas

3. **Para cada planta verificar:**
   - ✅ Imagen de identificación
   - ✅ Badge verde "Identificada" en esquina superior derecha
   - ✅ Nombre personalizado (o nombre común si no se especificó)
   - ✅ Nombre científico en italic y color verde
   - ✅ Nombre común (si disponible)
   - ✅ Familia botánica (si disponible)
   - ✅ Badge de estado de salud ("Buena" por defecto)
   - ✅ Ícono de ubicación + texto (si se especificó)
   - ✅ Ícono de riego + "Riego cada 7 días" (default)
   - ✅ Notas en italic (si se especificaron)
   - ✅ Botón "Ver Detalles"

---

## 🔧 Pruebas de Edge Cases

### Test 1: Confirmar múltiples especies de la misma identificación
1. En resultados, confirmar la primera especie (mejor match)
2. Hacer scroll y confirmar otra especie con menos confianza
3. Ir al dashboard
4. **Verificar:** Ambas plantas aparecen con nombres diferentes

### Test 2: Confirmar planta sin especie (confianza < 40%)
1. Identificar una imagen con resultados de baja confianza
2. Confirmar un resultado con <40% de confianza
3. **Verificar:** 
   - Planta se agrega sin `especie_id`
   - Usa nombre común de la identificación
   - Aparece en dashboard

### Test 3: Sin autenticación
1. Abrir DevTools → Network
2. Borrar localStorage o logout
3. Intentar confirmar una planta
4. **Verificar:** 
   - Request falla con 401/403
   - Toast de error aparece
   - Usuario no se redirige

### Test 4: Identificación de otro usuario
1. Login como Usuario A
2. Obtener `identificacionId` de Usuario B (via DB o API)
3. Intentar POST a `/api/plantas/agregar-desde-identificacion` con identificación de B
4. **Verificar:** 
   - Backend retorna 403 Forbidden
   - Mensaje: "no tienes permiso para acceder a esta identificación"

---

## 🐛 Troubleshooting

### Problema: Frontend no carga
**Solución:**
```powershell
docker-compose -f docker-compose.dev.yml restart frontend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Problema: Backend retorna 500 Internal Server Error
**Verificar:**
1. Logs del backend:
   ```powershell
   docker-compose -f docker-compose.dev.yml logs backend --tail=50
   ```
2. Base de datos está corriendo:
   ```powershell
   docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d plantitas_dev -c "SELECT COUNT(*) FROM plantas;"
   ```

### Problema: Toast no aparece al confirmar
**Verificar:**
1. Abrir DevTools → Console
2. Buscar errores de JavaScript
3. Verificar que `useToast` está importado correctamente
4. Verificar que Sonner está instalado:
   ```powershell
   docker-compose -f docker-compose.dev.yml exec frontend npm list sonner
   ```

### Problema: Imágenes no se muestran en carousel
**Verificar:**
1. Azure Blob Storage (Azurite) está corriendo
2. URLs de imágenes son accesibles:
   - Abrir DevTools → Network
   - Verificar requests a blob storage
3. CORS está configurado correctamente en Azurite

### Problema: Redirección no funciona
**Verificar:**
1. `useRouter` de `next/navigation` está importado
2. No hay errores en console
3. Toast se mostró correctamente antes de redirigir

---

## 📊 Verificación en Base de Datos

### Verificar plantas creadas

```powershell
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d plantitas_dev
```

```sql
-- Ver todas las plantas del usuario
SELECT 
    p.id,
    p.usuario_id,
    p.nombre_personalizado,
    p.estado_salud,
    p.ubicacion,
    p.notas,
    e.nombre_cientifico,
    e.nombre_comun,
    i.nombre_archivo AS imagen
FROM plantas p
LEFT JOIN especies e ON p.especie_id = e.id
LEFT JOIN imagenes i ON p.imagen_principal_id = i.id
ORDER BY p.fecha_creacion DESC
LIMIT 10;

-- Contar plantas por usuario
SELECT 
    u.nombre,
    COUNT(p.id) AS total_plantas
FROM usuarios u
LEFT JOIN plantas p ON u.id = p.usuario_id
GROUP BY u.id, u.nombre;

-- Ver identificaciones recientes
SELECT 
    id,
    usuario_id,
    nombre_cientifico,
    confianza,
    fecha_identificacion,
    cantidad_imagenes
FROM identificaciones
ORDER BY fecha_identificacion DESC
LIMIT 5;
```

---

## 📝 Checklist de Pruebas

### Frontend
- [ ] Login funciona
- [ ] Página de identificación carga
- [ ] Subida de múltiples imágenes funciona
- [ ] Identificación se procesa correctamente
- [ ] Página de resultados muestra carousel de imágenes
- [ ] Cards de especies muestran toda la información
- [ ] Botón "Confirmar esta planta" funciona
- [ ] Loading state aparece durante confirmación
- [ ] Toast de éxito aparece
- [ ] Botón cambia a "Confirmado" con check verde
- [ ] Redirección a dashboard funciona (2s)
- [ ] Dashboard carga correctamente
- [ ] Sección "Mis Plantas Identificadas" aparece
- [ ] Plantas agregadas se muestran con toda la información
- [ ] Imagen de identificación se muestra
- [ ] Badge "Identificada" aparece
- [ ] Información de especie es correcta
- [ ] Estado de salud muestra "Buena"
- [ ] Botón "Ver Detalles" funciona

### Backend (via /docs o Postman)
- [ ] Endpoint POST `/api/plantas/agregar-desde-identificacion` existe
- [ ] Requiere autenticación JWT
- [ ] Valida que identificación exista
- [ ] Valida ownership de identificación
- [ ] Crea planta con especie si disponible
- [ ] Crea planta sin especie si no disponible
- [ ] Usa nombre común como default si no hay nombre personalizado
- [ ] Asocia imagen principal correctamente
- [ ] Retorna 201 Created con planta creada
- [ ] Endpoint GET `/api/plantas` retorna plantas del usuario
- [ ] Incluye relaciones (especie, imagen_principal)

---

## 🎯 Criterios de Aceptación

### ✅ Cumplidos
1. **Backend:**
   - ✅ Endpoint POST para agregar planta desde identificación
   - ✅ Validación JWT
   - ✅ Validación de ownership
   - ✅ Manejo de especies
   - ✅ Manejo de imágenes múltiples
   - ✅ Defaults inteligentes (estado_salud, frecuencia_riego)

2. **Frontend:**
   - ✅ Carousel/grid de imágenes en resultados
   - ✅ Botones de confirmación por especie
   - ✅ Loading states
   - ✅ Toast notifications
   - ✅ Feedback visual (verde + check)
   - ✅ Redirección automática
   - ✅ Dashboard con sección de plantas identificadas
   - ✅ Cards completas con toda la información

3. **UX/UI:**
   - ✅ Flujo intuitivo
   - ✅ Responsive design
   - ✅ Feedback en cada paso
   - ✅ Manejo de errores

### ⏳ Pendientes
- ⏳ Tests unitarios backend (fixture DB pendiente)
- ⏳ Tests unitarios frontend
- ⏳ Tests E2E automatizados

---

## 📚 Documentación Adicional

- **Implementación completa:** `IMPLEMENTACION_T023_COMPLETADA.md`
- **Tarea Azure DevOps:** T-023 (ID: 55)
- **API Docs:** http://localhost:8000/docs
- **Frontend Dev:** http://localhost:4200

---

## 🎉 ¡Listo para Probar!

El feature está completamente implementado y listo para pruebas manuales.

**Próximos pasos recomendados:**
1. ✅ Pruebas manuales del flujo completo
2. ⏳ Fix de tests (agregar conftest.py con fixture `db`)
3. ⏳ Tests E2E con Playwright/Cypress
4. ⏳ Code review
5. ⏳ Merge a develop
6. ⏳ Deploy a staging

---

**Creado:** Enero 2026  
**Autor:** Equipo de Desarrollo  
**Sprint:** Sprint 3  
**Story Points:** 13
