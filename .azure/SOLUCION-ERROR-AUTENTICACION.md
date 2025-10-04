# 🔧 Solución Rápida: Error de Autenticación Azure DevOps MCP

## ❌ Error

```
Iniciar sesión
Lo sentimos, tenemos problemas para iniciar su sesión.

AADSTS900021: Requested tenant identifier '00000000-0000-0000-0000-000000000000' 
is not valid. Tenant identifiers may not be an empty GUID.
```

## ✅ Solución Rápida (3 pasos)

### 1. Crear Personal Access Token (PAT)

1. Ve a Azure DevOps: https://dev.azure.com/{tu-organización}
2. Click en tu avatar (arriba a la derecha)
3. Selecciona **"Personal access tokens"**
4. Click **"+ New Token"**
5. Configura:
   - **Name**: MCP Access
   - **Expiration**: 90 días
   - **Scopes**: 
     - ✅ Code: Read
     - ✅ Work Items: Read, Write
     - ✅ Project and Team: Read
6. Click **"Create"**
7. **¡COPIA EL TOKEN INMEDIATAMENTE!** (solo se muestra una vez)

### 2. Configurar el archivo `mcp.json`

**Ubicación del archivo:**
- Windows: `C:\Users\{TU-USUARIO}\.aitk\mcp.json`
- Linux/Mac: `~/.aitk/mcp.json`

**Contenido del archivo:**

```json
{
  "servers": {
    "azure devops": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "tu-organizacion-aqui"
      ],
      "env": {
        "AZURE_DEVOPS_PAT": "tu-token-aqui",
        "AZURE_DEVOPS_EXT_PAT": "tu-token-aqui"
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
        "AZURE_DEVOPS_PAT": "qw3rt4uio5asdf6hjkl7xcvbnm8234567890",
        "AZURE_DEVOPS_EXT_PAT": "qw3rt4uio5asdf6hjkl7xcvbnm8234567890"
      }
    }
  }
}
```

⚠️ **IMPORTANTE:**
- Reemplaza `tu-organizacion-aqui` con el nombre REAL de tu organización
- Reemplaza `tu-token-aqui` con tu Personal Access Token
- **NO uses** `{{YOUR_ADO_ORG}}` (es solo un placeholder)
- **NO dejes** GUIDs vacíos como `00000000-0000-0000-0000-000000000000`

### 3. Reiniciar VS Code

**MUY IMPORTANTE:** Los cambios NO se aplican automáticamente.

1. **Guarda** el archivo `mcp.json`
2. **Cierra COMPLETAMENTE VS Code** (todas las ventanas)
3. **Abre VS Code nuevamente**
4. Intenta conectar de nuevo

## 🔍 ¿Cómo encuentro mi organización?

Tu organización es la que aparece en la URL de Azure DevOps:

```
https://dev.azure.com/{ESTA-ES-TU-ORGANIZACIÓN}/
```

Ejemplos:
- Si tu URL es `https://dev.azure.com/ia-grupo-5/`, tu organización es `ia-grupo-5`
- Si tu URL es `https://dev.azure.com/grupo-5-UNLAM/`, tu organización es `grupo-5-UNLAM`

## 🧪 Verificar que funciona

### Opción 1: Verificar con PowerShell (Windows)

```powershell
$pat = "tu-token-aqui"
$token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
$headers = @{Authorization = "Basic $token"}
Invoke-RestMethod -Uri "https://dev.azure.com/tu-organizacion/_apis/projects?api-version=7.0" -Headers $headers
```

### Opción 2: Verificar con curl (Linux/Mac)

```bash
PAT="tu-token-aqui"
TOKEN=$(echo -n ":$PAT" | base64)
curl -H "Authorization: Basic $TOKEN" \
  "https://dev.azure.com/tu-organizacion/_apis/projects?api-version=7.0"
```

Si ves una lista de proyectos en JSON, ¡tu configuración funciona! ✅

## 🚨 Si el problema persiste

1. **Verifica permisos del token:**
   - Ve a Azure DevOps → Settings → Personal Access Tokens
   - Verifica que tu token tenga los permisos correctos
   - Verifica que no haya expirado

2. **Verifica el nombre de la organización:**
   - Debe coincidir EXACTAMENTE con el nombre en Azure DevOps
   - Es case-sensitive (distingue mayúsculas/minúsculas)

3. **Crea un nuevo token:**
   - A veces los tokens pueden tener problemas
   - Crea uno nuevo y actualiza la configuración

4. **Verifica que Node.js esté instalado:**
   ```bash
   node --version
   npx --version
   ```
   Si no están instalados, descarga Node.js de https://nodejs.org/

## 📚 Documentación Completa

Para más información y troubleshooting avanzado, consulta:

- [Guía completa de configuración](azure-devops-mcp-setup.md)
- [Plan ágil del proyecto](proyecto-agile-plan.md)
- [Work items de Azure DevOps](azure-devops-workitems.md)

## 🔐 Seguridad

⚠️ **NUNCA:**
- Compartas tu PAT con nadie
- Subas el `mcp.json` a repositorios públicos
- Publiques capturas de pantalla con tu token visible

✅ **SIEMPRE:**
- Usa tokens con permisos mínimos necesarios
- Revoca tokens que ya no uses
- Rota tokens cada 90 días

---

**Si esta guía te ayudó a resolver el problema, ¡excelente! 🎉**

**¿Aún tienes problemas?** Revisa la [guía completa](azure-devops-mcp-setup.md) para más soluciones.
