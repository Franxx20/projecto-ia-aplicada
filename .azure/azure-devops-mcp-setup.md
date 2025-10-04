# 🔧 Configuración de Azure DevOps MCP (Model Context Protocol)

## 📋 Descripción General

Esta guía te ayudará a configurar y solucionar problemas con Azure DevOps MCP, una herramienta que permite a los editores de código (como VS Code) interactuar con Azure DevOps para listar proyectos, work items y más.

## ⚙️ Requisitos Previos

- Node.js instalado (versión 16 o superior)
- NPX disponible en tu sistema
- Cuenta de Azure DevOps con acceso a una organización
- VS Code u otro editor compatible con MCP

## 🚀 Configuración Inicial

### Paso 1: Identificar tu Organización de Azure DevOps

Tu organización aparece en la URL cuando accedes a Azure DevOps:

**Formato de URL:**
```
https://dev.azure.com/{TU-ORGANIZACIÓN}/
```

**Ejemplos:**
- `https://dev.azure.com/ia-grupo-5/`
- `https://dev.azure.com/grupo-5-UNLAM/`

### Paso 2: Crear un Personal Access Token (PAT)

1. Ve a Azure DevOps y accede a tu organización
2. Haz clic en tu **avatar** (esquina superior derecha)
3. Selecciona **"Personal access tokens"** (Tokens de acceso personal)
4. Haz clic en **"+ New Token"** (Nuevo Token)

**Configuración recomendada del token:**

| Campo | Valor |
|-------|-------|
| **Name** | MCP Access Token |
| **Organization** | Selecciona tu organización |
| **Expiration** | 90 días (o custom) |
| **Scopes** | Custom defined |

**Permisos necesarios (mínimos):**
- ✅ **Code**: Read
- ✅ **Work Items**: Read, Write
- ✅ **Project and Team**: Read
- ✅ **Build**: Read
- ✅ **Release**: Read

5. Haz clic en **"Create"**
6. **¡IMPORTANTE!** Copia el token generado inmediatamente (solo se muestra una vez)

**Ejemplo de token generado:**
```
qwertyuiopasdfghjklzxcvbnm1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

### Paso 3: Configurar el archivo `mcp.json`

La ubicación del archivo depende de tu sistema operativo:

**Windows:**
```
C:\Users\{TU-USUARIO}\.aitk\mcp.json
```

**Linux/Mac:**
```
~/.aitk/mcp.json
```

### Paso 4: Editar la Configuración

Abre el archivo `mcp.json` y configúralo de la siguiente manera:

```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "TU-ORGANIZACIÓN-AQUÍ"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "TU-TOKEN-AQUÍ",
        "AZURE_DEVOPS_EXT_PAT": "TU-TOKEN-AQUÍ"
      }
    }
  }
}
```

**Ejemplo con datos reales:**

```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "ia-grupo-5"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "qwertyuiopasdfghjklzxcvbnm1234567890",
        "AZURE_DEVOPS_EXT_PAT": "qwertyuiopasdfghjklzxcvbnm1234567890"
      }
    }
  }
}
```

⚠️ **IMPORTANTE:** 
- Reemplaza `TU-ORGANIZACIÓN-AQUÍ` con el nombre de tu organización
- Reemplaza `TU-TOKEN-AQUÍ` con tu Personal Access Token
- NO uses `{{YOUR_ADO_ORG}}` - este es solo un placeholder
- NO uses GUIDs vacíos como `00000000-0000-0000-0000-000000000000`

### Paso 5: Reiniciar VS Code

Después de guardar los cambios en `mcp.json`:

1. **Cierra completamente VS Code** (no solo la ventana actual)
2. **Vuelve a abrir VS Code**
3. Los cambios en la configuración de MCP solo se aplican al reiniciar

## 🔍 Verificación de la Configuración

### Verificar desde PowerShell/Terminal

Puedes verificar que tu configuración funciona ejecutando:

```powershell
# Windows PowerShell
$env:AZURE_DEVOPS_PAT = "tu-token-aquí"
npx -y @azure-devops/mcp tu-organizacion
```

```bash
# Linux/Mac
export AZURE_DEVOPS_PAT="tu-token-aquí"
npx -y @azure-devops/mcp tu-organizacion
```

### Verificar con API REST

Verifica tu token directamente con la API de Azure DevOps:

```powershell
# PowerShell
$pat = "tu-token-aquí"
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
$headers = @{Authorization = "Basic $token"}
Invoke-RestMethod -Uri "https://dev.azure.com/tu-organizacion/_apis/projects?api-version=7.0" -Headers $headers
```

```bash
# Linux/Mac
PAT="tu-token-aquí"
TOKEN=$(echo -n ":$PAT" | base64)
curl -H "Authorization: Basic $TOKEN" \
  "https://dev.azure.com/tu-organizacion/_apis/projects?api-version=7.0"
```

## 🐛 Solución de Problemas

### Error: AADSTS900021 - Invalid Tenant Identifier

**Error completo:**
```
Lo sentimos, tenemos problemas para iniciar su sesión.
AADSTS900021: Requested tenant identifier '00000000-0000-0000-0000-000000000000' 
is not valid. Tenant identifiers may not be an empty GUID.
```

**Causa:** El servidor MCP está intentando hacer autenticación interactiva con Azure AD, pero no tiene un tenant ID válido.

**Soluciones:**

#### Solución 1: Verificar que el PAT esté configurado correctamente

```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "ia-grupo-5"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "token-válido-aquí",
        "AZURE_DEVOPS_EXT_PAT": "token-válido-aquí"
      }
    }
  }
}
```

#### Solución 2: Agregar el Tenant ID explícitamente

Si conoces tu Tenant ID de Azure AD, agrégalo a la configuración:

```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "ia-grupo-5"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "tu-token",
        "AZURE_DEVOPS_EXT_PAT": "tu-token",
        "AZURE_TENANT_ID": "tu-tenant-id"
      }
    }
  }
}
```

**Ejemplo con Tenant ID real:**
```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "ia-grupo-5"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "tu-token",
        "AZURE_DEVOPS_EXT_PAT": "tu-token",
        "AZURE_TENANT_ID": "659e1dba-b3cc-4dcc-8730-d23877e7ab7b"
      }
    }
  }
}
```

#### Solución 3: Reiniciar VS Code completamente

**¡MUY IMPORTANTE!** Los cambios en `mcp.json` **NO** se aplican automáticamente:

1. Guarda los cambios en `mcp.json`
2. **Cierra TODAS las ventanas de VS Code**
3. Abre VS Code nuevamente
4. Intenta conectar nuevamente

### Error: Token Expirado o Inválido

**Síntomas:**
- Error 401 Unauthorized
- Error 403 Forbidden
- "Invalid authentication credentials"

**Solución:**

1. Ve a Azure DevOps → Personal Access Tokens
2. Verifica el estado de tu token:
   - ¿Está expirado?
   - ¿Tiene los permisos correctos?
3. Si está expirado o inválido, **crea un nuevo token**
4. Actualiza el `mcp.json` con el nuevo token
5. **Reinicia VS Code**

### Error: Organización no encontrada

**Error:**
```
Organization 'xxx' not found
```

**Solución:**

1. Verifica que el nombre de la organización sea correcto
2. Accede a `https://dev.azure.com` y confirma el nombre exacto
3. El nombre es **case-sensitive** (distingue mayúsculas/minúsculas)

### Error: NPX no encontrado

**Error:**
```
'npx' is not recognized as an internal or external command
```

**Solución:**

1. Instala Node.js desde https://nodejs.org/
2. Reinicia tu terminal/PowerShell
3. Verifica la instalación:
   ```bash
   node --version
   npx --version
   ```

## ✅ Checklist de Configuración

Usa esta lista para verificar que todo esté configurado correctamente:

- [ ] Node.js y NPX instalados
- [ ] Organización de Azure DevOps identificada
- [ ] Personal Access Token creado con permisos correctos
- [ ] Token copiado y guardado de forma segura
- [ ] Archivo `mcp.json` ubicado correctamente
- [ ] Organización configurada sin placeholders como `{{YOUR_ADO_ORG}}`
- [ ] PAT configurado en variables de entorno
- [ ] VS Code reiniciado después de los cambios
- [ ] Conexión verificada exitosamente

## 🔐 Seguridad

### Mejores Prácticas

1. **Nunca compartas tu PAT** con nadie
2. **No subas el `mcp.json`** a repositorios públicos
3. **Usa tokens con permisos mínimos** necesarios
4. **Rota los tokens regularmente** (cada 90 días recomendado)
5. **Revoca tokens** que ya no uses

### Agregar `mcp.json` al `.gitignore`

Si tienes un `mcp.json` en tu repositorio (no recomendado), agrégalo al `.gitignore`:

```bash
# .gitignore
.aitk/
mcp.json
*.mcp.json
```

## 📚 Recursos Adicionales

- **Azure DevOps REST API**: https://learn.microsoft.com/en-us/rest/api/azure/devops/
- **Personal Access Tokens**: https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate
- **Model Context Protocol**: https://github.com/modelcontextprotocol

## 🆘 Soporte

Si después de seguir esta guía aún tienes problemas:

1. Verifica los logs de VS Code:
   - `View` → `Output` → `MCP`
2. Intenta la verificación manual con PowerShell/curl
3. Verifica que tu cuenta tenga acceso a la organización en Azure DevOps
4. Contacta al administrador de tu organización para verificar permisos

---

**Última actualización:** 2024

**Versión:** 1.0.0
