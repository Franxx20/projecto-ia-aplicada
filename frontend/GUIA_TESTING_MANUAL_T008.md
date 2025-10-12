# 🧪 Guía de Testing Manual - T-008: Componente de Subida de Fotos

**Fecha:** 12 de octubre de 2025  
**URL de Testing:** http://localhost:4200/identificar  
**Componente:** `ImageUpload` + Hook `useImageUpload`

---

## 🎯 Objetivo

Verificar que todas las funcionalidades del componente de subida de fotos funcionan correctamente en el navegador real.

---

## ✅ Checklist de Funcionalidades

### 1. Renderizado Inicial

**Acción:** Abrir http://localhost:4200/identificar

**Verificar:**
- [ ] ✅ Se muestra el área de drag-and-drop con borde punteado
- [ ] ✅ Se ve el ícono de imagen en el centro
- [ ] ✅ Texto: "Arrastra tu imagen aquí, o haz click para seleccionar"
- [ ] ✅ Texto de formatos permitidos: "Soporta: JPG, PNG, WEBP, HEIC (máx. 10 MB)"
- [ ] ✅ Botón "Seleccionar Archivo" visible
- [ ] ✅ Botón "Tomar Foto" visible (con ícono de cámara)
- [ ] ✅ Sección "💡 Tips para mejores resultados" visible con 4 tips

**Estado:** ⬜ Pendiente

---

### 2. Selección de Archivo (Click)

**Acción:** 
1. Click en botón "Seleccionar Archivo"
2. Seleccionar una imagen válida (JPG, PNG, < 10MB)

**Verificar:**
- [ ] Se abre el selector de archivos del sistema
- [ ] Después de seleccionar:
  - [ ] ✅ Se muestra preview de la imagen
  - [ ] ✅ Se muestra el nombre del archivo
  - [ ] ✅ Se muestra el tamaño del archivo formateado (ej: "2.5 MB")
  - [ ] ✅ Aparece barra de progreso
  - [ ] ✅ Aparece botón "Cambiar Imagen"
  - [ ] ✅ Aparece botón "Eliminar"
  - [ ] ✅ Desaparece el área de drag-and-drop

**Estado:** ⬜ Pendiente

**Captura de Pantalla:** _[Adjuntar aquí]_

---

### 3. Drag and Drop

**Acción:**
1. Arrastrar una imagen desde el explorador de archivos
2. Soltar sobre el área de drag-and-drop

**Verificar:**
- [ ] Al pasar el mouse sobre el área:
  - [ ] ✅ El borde cambia de color (hover effect)
- [ ] Al soltar la imagen:
  - [ ] ✅ Se muestra preview de la imagen
  - [ ] ✅ Funcionalidad idéntica a selección por click

**Estado:** ⬜ Pendiente

**Captura de Pantalla:** _[Adjuntar aquí]_

---

### 4. Validación de Tamaño

**Acción:**
1. Intentar subir un archivo > 10MB

**Verificar:**
- [ ] ✅ Se muestra mensaje de error
- [ ] ✅ Mensaje indica: "El archivo excede el tamaño máximo permitido de 10 MB"
- [ ] ✅ El color del mensaje es rojo/destructivo
- [ ] ✅ NO se muestra preview de la imagen
- [ ] ✅ NO se inicia el upload

**Estado:** ⬜ Pendiente

**Notas:** _Si no tienes archivo > 10MB, puedes saltarte este test_

---

### 5. Validación de Tipo de Archivo

**Acción:**
1. Intentar subir un archivo no permitido (PDF, TXT, etc.)

**Verificar:**
- [ ] ✅ Se muestra mensaje de error
- [ ] ✅ Mensaje indica tipo no permitido
- [ ] ✅ NO se muestra preview
- [ ] ✅ NO se inicia el upload

**Estado:** ⬜ Pendiente

**Notas:** _Si el sistema no permite seleccionar archivos no-imagen, eso es correcto (accept="image/*")_

---

### 6. Barra de Progreso

**Acción:**
1. Seleccionar una imagen válida
2. Observar durante el upload

**Verificar:**
- [ ] ✅ Aparece barra de progreso animada
- [ ] ✅ Muestra porcentaje (0% → 100%)
- [ ] ✅ Color de la barra es visible
- [ ] ✅ La barra se actualiza suavemente

**Estado:** ⬜ Pendiente

**Captura de Pantalla:** _[Adjuntar aquí]_

**Notas:** _El upload puede ser muy rápido en local, es normal_

---

### 7. Botón "Cambiar Imagen"

**Acción:**
1. Subir una imagen
2. Esperar a que termine el upload
3. Click en "Cambiar Imagen"

**Verificar:**
- [ ] ✅ Se abre selector de archivos
- [ ] ✅ Al seleccionar nueva imagen:
  - [ ] Se reemplaza el preview
  - [ ] Se inicia nuevo upload
  - [ ] Estado se resetea correctamente

**Estado:** ⬜ Pendiente

---

### 8. Botón "Eliminar"

**Acción:**
1. Subir una imagen
2. Click en botón "Eliminar"

**Verificar:**
- [ ] ✅ El preview desaparece
- [ ] ✅ Vuelve a mostrarse el área de drag-and-drop
- [ ] ✅ Estado se resetea a inicial
- [ ] ✅ No hay mensajes de error

**Estado:** ⬜ Pendiente

---

### 9. Botón "Tomar Foto" (Solo en Mobile/Tablet)

**Acción:**
1. Abrir desde dispositivo móvil O usar DevTools para simular móvil
2. Click en "Tomar Foto"

**Verificar:**
- [ ] Se abre la cámara del dispositivo
- [ ] Permite capturar foto
- [ ] Foto capturada se procesa igual que archivo seleccionado

**Estado:** ⬜ Pendiente / ⏭️ Skip (si no tienes móvil)

**Notas:** _En desktop puede no funcionar o abrir webcam según navegador_

---

### 10. Integración con Página de Identificación

**Acción:**
1. Subir imagen exitosamente
2. Observar qué pasa después

**Verificar:**
- [ ] ✅ Se ejecuta función `onUploadSuccess`
- [ ] ✅ Se muestra algún indicador de que se va a identificar
- [ ] ✅ (Pendiente implementación PlantNet) Debería mostrar resultados

**Estado:** ⬜ Pendiente

**Notas:** _La identificación real aún no está implementada (T-017)_

---

## 🐛 Bugs Encontrados

### Bug #1: [Título del bug]
- **Descripción:** 
- **Pasos para reproducir:**
- **Comportamiento esperado:**
- **Comportamiento actual:**
- **Severidad:** 🔴 Alta / 🟡 Media / 🟢 Baja

---

## 📸 Capturas de Pantalla

### Estado Inicial
_[Adjuntar captura]_

### Preview con Imagen
_[Adjuntar captura]_

### Mensaje de Error
_[Adjuntar captura]_

### Barra de Progreso
_[Adjuntar captura]_

---

## ✅ Resultado Final

**Total de Tests:** 10  
**Pasados:** ___ / 10  
**Fallados:** ___ / 10  
**Skipped:** ___ / 10

**¿El componente está listo para producción?** ⬜ SÍ / ⬜ NO / ⬜ CON AJUSTES

**Comentarios Generales:**
_[Escribe aquí tus observaciones]_

---

## 📋 Próximos Pasos

- [ ] Documentar bugs encontrados como issues
- [ ] Implementar T-017: Integración PlantNet API
- [ ] Testing E2E con Playwright (futuro)
- [ ] Mejorar tests unitarios (refactorizar mocks)

---

**Testeado por:** [Tu nombre]  
**Navegador:** _[Chrome / Firefox / Safari / Edge]_  
**Fecha:** 12 de octubre de 2025
