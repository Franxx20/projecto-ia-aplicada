# 🧪 Guía de Pruebas - Componente de Subida de Fotos

## Prerequisitos

1. Contenedores Docker levantados:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

2. Verificar que todos los servicios estén saludables:
```bash
docker ps
```

Deberías ver:
- ✅ `projecto-ia_frontend_dev` - Healthy
- ✅ `projecto-ia_backend_dev` - Healthy
- ✅ `projecto-ia_db` - Healthy
- ✅ `projecto-ia_azurite_dev` - Running

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Página de Identificación**: http://localhost:4200/identificar

## 📝 Casos de Prueba

### Test 1: Renderizado Básico
**Objetivo**: Verificar que el componente se renderiza correctamente

1. Navegar a: http://localhost:4200/identificar
2. **Verificar que aparece**:
   - ✅ Título "Identificar Planta"
   - ✅ Área de drag & drop con texto "Arrastra tu imagen aquí..."
   - ✅ Botón "Seleccionar Archivo"
   - ✅ Botón "Tomar Foto"
   - ✅ Sección de tips con 4 consejos
   - ✅ Sección "Cómo funciona" con 3 pasos

### Test 2: Selección de Archivo Válido
**Objetivo**: Upload exitoso de una imagen válida

1. Preparar una imagen JPG/PNG de menos de 10MB
2. Click en "Seleccionar Archivo"
3. Seleccionar la imagen
4. **Verificar**:
   - ✅ La imagen aparece en preview
   - ✅ Se muestra el nombre del archivo
   - ✅ Se muestra el tamaño en MB
   - ✅ Aparece automáticamente la barra de progreso
   - ✅ El progreso va de 0% a 100%
   - ✅ Al completar, aparece overlay verde con ✓
   - ✅ Aparece botón "Subir Otra Imagen"
   - ✅ Aparece botón "Identificar Planta"

### Test 3: Drag and Drop
**Objetivo**: Verificar funcionalidad de arrastrar y soltar

1. Tener una imagen en el explorador de archivos
2. Arrastrar la imagen sobre el área de drop
3. **Verificar durante el arrastre**:
   - ✅ El borde del área cambia de color
   - ✅ El fondo tiene un tinte de color
4. Soltar la imagen
5. **Verificar**:
   - ✅ La imagen se carga automáticamente
   - ✅ Aparece el preview
   - ✅ Inicia el upload automático

### Test 4: Validación de Tamaño
**Objetivo**: Validar que archivos muy grandes son rechazados

1. Preparar una imagen mayor a 10MB
2. Intentar subirla
3. **Verificar**:
   - ✅ Aparece mensaje de error rojo
   - ✅ El mensaje indica "El archivo es demasiado grande"
   - ✅ Se muestra el tamaño máximo permitido (10MB)
   - ✅ Se muestra el tamaño actual del archivo
   - ✅ NO se muestra preview de la imagen

### Test 5: Validación de Tipo
**Objetivo**: Validar que solo se aceptan tipos de imagen válidos

1. Intentar subir un archivo PDF, DOCX o TXT
2. **Verificar**:
   - ✅ Aparece mensaje de error rojo
   - ✅ El mensaje indica "Tipo de archivo no permitido"
   - ✅ Se muestran los tipos permitidos
   - ✅ NO se muestra preview

### Test 6: Cancelar/Limpiar Selección
**Objetivo**: Verificar que se puede cancelar y seleccionar otra imagen

1. Subir una imagen válida
2. Click en el botón X (eliminar) en la esquina superior derecha del preview
3. **Verificar**:
   - ✅ El preview desaparece
   - ✅ Vuelve a aparecer el área de drag & drop
   - ✅ Los tips reaparecen
   - ✅ Se puede seleccionar otra imagen

### Test 7: Botón de Cámara (Solo en Móvil o con Webcam)
**Objetivo**: Verificar captura desde cámara

**En Desktop con Webcam**:
1. Click en "Tomar Foto"
2. Permitir acceso a la cámara
3. Tomar una foto
4. **Verificar**: Mismo flujo que selección de archivo

**En Móvil**:
1. Abrir http://localhost:4200/identificar en el navegador móvil
2. Click en "Tomar Foto"
3. La cámara del dispositivo se abre automáticamente
4. Tomar foto
5. **Verificar**: La foto se sube automáticamente

### Test 8: Responsividad
**Objetivo**: Verificar que la UI funciona en diferentes tamaños

**Desktop (>768px)**:
- ✅ Botones "Seleccionar" y "Tomar Foto" en fila (lado a lado)
- ✅ Tips en una sola columna
- ✅ "Cómo funciona" en 3 columnas

**Móvil (<768px)**:
- ✅ Botones apilados verticalmente
- ✅ Tips en una columna
- ✅ "Cómo funciona" en 1 columna
- ✅ Imagen de preview ajustada al ancho

### Test 9: Integración con Backend
**Objetivo**: Verificar que las imágenes se guardan en el backend

1. Subir una imagen
2. Verificar logs del backend:
```bash
docker logs projecto-ia_backend_dev -f
```
3. **Verificar en logs**:
   - ✅ POST request a `/api/uploads/imagen`
   - ✅ Status 200 (éxito) o 201 (creado)
   - ✅ Respuesta JSON con ID de imagen

4. Verificar en Swagger UI (http://localhost:8000/docs):
   - Ir a endpoint GET `/api/uploads/{imagen_id}`
   - Usar el ID recibido
   - **Verificar**: La imagen existe y tiene todos los metadatos

### Test 10: Identificar Planta (Flujo Completo)
**Objetivo**: Probar el flujo completo de identificación

1. Subir una imagen de una planta
2. Esperar a que termine el upload (overlay verde ✓)
3. Click en "Identificar Planta"
4. **Verificar**:
   - ✅ El botón cambia a "Identificando Planta..."
   - ✅ Aparece icono de sparkles animado
   - ✅ Después de ~2 segundos, navega a la página de resultados
   - ✅ La URL cambia a `/identificar/resultados?imageId=...`

## 🔍 Verificaciones en DevTools

### Console de Navegador
**Verificar que NO aparecen**:
- ❌ Errores de compilación
- ❌ Warnings de React
- ❌ Errores de red (404, 500)

**Verificar que SÍ aparecen** (al subir imagen):
- ✅ Log: "Imagen subida exitosamente: {response}"
- ✅ El objeto response contiene: id, usuario_id, nombre_archivo, url, etc.

### Network Tab
**Verificar request de upload**:
1. Abrir Network tab
2. Subir una imagen
3. **Verificar**:
   - ✅ Request a `http://localhost:8000/api/uploads/imagen`
   - ✅ Method: POST
   - ✅ Content-Type: multipart/form-data
   - ✅ Request payload contiene el archivo
   - ✅ Response status: 200 o 201
   - ✅ Response body tiene estructura correcta

### Application Tab → Local Storage
**Verificar tokens de autenticación**:
- ✅ `access_token` presente
- ✅ `refresh_token` presente
- ✅ `user` presente (objeto JSON)

## ⚠️ Troubleshooting

### Problema: Error 401 Unauthorized
**Solución**: 
1. Asegúrate de estar logueado
2. Navega a http://localhost:4200/login
3. Inicia sesión con credenciales válidas

### Problema: Error CORS
**Solución**:
1. Verificar que el backend esté corriendo
2. Revisar logs del backend
3. Verificar variable de entorno `CORS_ORIGINS` en backend

### Problema: Imagen no se sube
**Solución**:
1. Verificar logs del backend: `docker logs projecto-ia_backend_dev -f`
2. Verificar que Azure Storage esté corriendo
3. Verificar conexión de red en DevTools

### Problema: Preview no aparece
**Solución**:
1. Abrir Console y buscar errores
2. Verificar que el archivo sea una imagen válida
3. Intentar con otra imagen

## 📊 Checklist de Pruebas Completo

- [ ] Renderizado básico
- [ ] Selección de archivo válido
- [ ] Drag and drop
- [ ] Validación de tamaño
- [ ] Validación de tipo
- [ ] Cancelar/limpiar selección
- [ ] Botón de cámara
- [ ] Responsividad (desktop)
- [ ] Responsividad (móvil)
- [ ] Integración con backend
- [ ] Flujo completo de identificación
- [ ] Progreso de upload visible
- [ ] Mensajes de error claros
- [ ] Mensajes de éxito visibles
- [ ] Tips de uso visibles
- [ ] Sin errores en console
- [ ] Requests correctos en Network tab

## ✅ Criterios de Éxito

**La implementación es exitosa si**:
- ✅ Todos los tests manuales pasan
- ✅ No hay errores en la consola del navegador
- ✅ Las imágenes se suben correctamente al backend
- ✅ El preview funciona correctamente
- ✅ Las validaciones funcionan
- ✅ La UI es responsiva
- ✅ El drag and drop funciona
- ✅ La barra de progreso se actualiza

---

**Tiempo estimado de pruebas**: 15-20 minutos
**Última actualización**: 12 de Octubre, 2025
