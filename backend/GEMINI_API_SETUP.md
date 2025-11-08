# 🔑 Guía: Obtener API Key de Google Gemini Pro

Esta guía te ayudará a obtener tu API key de Google Gemini para usar en el proyecto.

---

## 📋 Requisitos

- Cuenta de Google
- Acceso a Google AI Studio (gratis)

---

## 🚀 Paso a Paso

### 1. Acceder a Google AI Studio

Ve a una de estas URLs:
- **Opción A (Recomendada):** https://aistudio.google.com/app/apikey
- **Opción B:** https://makersuite.google.com/app/apikey

### 2. Iniciar Sesión

Inicia sesión con tu cuenta de Google.

### 3. Crear API Key

1. Clic en **"Get API Key"** o **"Create API Key"**
2. Selecciona o crea un proyecto de Google Cloud
   - Si no tienes proyecto, clic en **"Create API key in new project"**
3. Espera unos segundos mientras se genera la key

### 4. Copiar la API Key

Tu API key se verá algo así:
```
AIzaSyB....(39 caracteres)....xyz123
```

⚠️ **IMPORTANTE:** Copia inmediatamente la key, no la compartas con nadie.

### 5. Configurar en el Proyecto

#### Opción A: Archivo .env (Recomendado)

1. En el directorio `backend/`, copia el archivo de ejemplo:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edita el archivo `.env` y pega tu API key:
   ```bash
   GEMINI_API_KEY="AIzaSyB....tu-api-key-aqui"
   GEMINI_MODEL="gemini-1.5-pro"
   ```

#### Opción B: Variable de Entorno del Sistema

En PowerShell (Windows):
```powershell
$env:GEMINI_API_KEY="AIzaSyB....tu-api-key-aqui"
```

En Bash (Linux/Mac):
```bash
export GEMINI_API_KEY="AIzaSyB....tu-api-key-aqui"
```

---

## 🧪 Verificar Instalación

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Ejecutar Test de Configuración

```bash
python test_gemini_setup.py
```

Deberías ver:
```
✅ API Key encontrada: AIzaSyB...xyz123
✅ API Key configurada correctamente
✅ Modelo creado correctamente
✅ Respuesta recibida: 'Azul'
...
🎉 ¡ÉXITO! Tu configuración de Gemini está lista.
```

---

## 📊 Planes y Límites

### Free Tier (Gratis)

- **Límite:** 60 requests por minuto
- **Límite diario:** Varía (generalmente 1,500+)
- **Modelos disponibles:**
  - `gemini-1.5-flash` (más rápido, económico)
  - `gemini-1.5-pro` (más potente)

### Verificar tu Cuota

Ve a: https://aistudio.google.com/app/prompts

En la parte superior derecha verás tu uso actual.

---

## 🎯 Modelos Disponibles

### gemini-1.5-flash ⚡

- **Velocidad:** Muy rápida
- **Costo:** Menor
- **Uso recomendado:** Producción, análisis rápidos
- **Token limit:** 1M tokens context

```bash
GEMINI_MODEL="gemini-1.5-flash"
```

### gemini-1.5-pro 🧠

- **Velocidad:** Más lenta
- **Calidad:** Superior
- **Uso recomendado:** Análisis complejos, desarrollo
- **Token limit:** 2M tokens context

```bash
GEMINI_MODEL="gemini-1.5-pro"
```

---

## 🔒 Seguridad

### ✅ Buenas Prácticas

- ✅ Usa archivo `.env` (incluido en `.gitignore`)
- ✅ Nunca hagas commit de la API key
- ✅ Usa variables de entorno en producción
- ✅ Rota la key si se expone

### ❌ NO Hagas Esto

- ❌ Hardcodear la key en el código
- ❌ Subirla a GitHub/GitLab
- ❌ Compartirla en Slack/Discord
- ❌ Incluirla en logs o screenshots

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY no está configurada"

**Solución:**
1. Verifica que el archivo `.env` existe en `backend/`
2. Verifica que la variable está sin espacios:
   ```bash
   GEMINI_API_KEY="tu-key-sin-espacios"
   ```
3. Reinicia el terminal/servidor

### Error: "API key not valid"

**Posibles causas:**
1. Key incorrecta o con caracteres extra
2. Key expirada o deshabilitada
3. Proyecto de Google Cloud suspendido

**Solución:**
- Ve a https://aistudio.google.com/app/apikey
- Verifica que la key está activa
- Genera una nueva si es necesario

### Error: "Quota exceeded"

**Causas:**
- Límite diario alcanzado
- Límite por minuto excedido

**Solución:**
- Espera hasta el reset diario
- Reduce la frecuencia de requests
- Considera upgrade a plan pago

### Error: "Model not found"

**Solución:**
Verifica el nombre del modelo en `.env`:
```bash
# Correcto:
GEMINI_MODEL="gemini-1.5-pro"

# Incorrecto:
GEMINI_MODEL="gemini-pro"  # Versión antigua
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **Gemini API Docs:** https://ai.google.dev/docs
- **Python SDK:** https://ai.google.dev/tutorials/python_quickstart
- **Pricing:** https://ai.google.dev/pricing

### Tutoriales

- **Getting Started:** https://ai.google.dev/tutorials/setup
- **Vision (Imágenes):** https://ai.google.dev/tutorials/vision_quickstart
- **JSON Mode:** https://ai.google.dev/tutorials/json_capabilities

### Community

- **Discord:** https://discord.gg/google-dev
- **GitHub Issues:** https://github.com/google/generative-ai-python/issues

---

## 🎓 Próximos Pasos

Una vez configurada tu API key:

1. ✅ **Test completado** → `python test_gemini_setup.py`
2. 📝 **Continuar con Task 2:** Implementar `gemini_service.py`
3. 🏗️ **Crear schemas:** Definir estructuras de datos
4. 🌐 **Implementar endpoints:** API REST para análisis

---

## 📝 Ejemplo de .env Completo

```bash
# Google Gemini API
GEMINI_API_KEY="AIzaSyB....tu-api-key-real-aqui"
GEMINI_MODEL="gemini-1.5-pro"
GEMINI_TEMPERATURE=0.4
GEMINI_MAX_OUTPUT_TOKENS=2048
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_REQUESTS_PER_DAY=1500
GEMINI_MAX_REQUESTS_PER_USER_PER_DAY=10
```

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o contacta al equipo de desarrollo.

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0
