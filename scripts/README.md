# 🔧 Azure Deployment Scripts

Scripts PowerShell automatizados para gestionar el deployment en Azure Container Apps.

---

## 📜 Scripts Disponibles

### 1. `azure-deploy-full.ps1` - Deployment Completo

**Propósito**: Automatiza todo el proceso de deployment desde cero.

**Uso**:
```powershell
.\azure-deploy-full.ps1 `
  -ResourceGroup "rg-plantitas-demo-temp" `
  -Location "eastus" `
  -ProjectName "plantitas" `
  -DBPassword "TuPasswordSeguro123!" `
  -GeminiApiKey "tu-gemini-api-key"
```

**Parámetros**:
- `ResourceGroup`: Nombre del Resource Group (default: `rg-plantitas-demo-temp`)
- `Location`: Región de Azure (default: `eastus`)
- `ProjectName`: Prefijo para nombres de recursos (default: `plantitas`)
- `DBPassword`: Contraseña para PostgreSQL (requerido si no se proporciona interactivamente)
- `GeminiApiKey`: API Key de Gemini (requerido si no se proporciona interactivamente)

**Duración**: 30-45 minutos

**Qué hace**:
1. ✅ Valida prerequisites (Azure CLI, login)
2. ✅ Crea Resource Group
3. ✅ Deploy PostgreSQL Flexible Server (B1ms)
4. ✅ Deploy Azure Blob Storage
5. ✅ Crea Log Analytics Workspace
6. ✅ Crea Container Apps Environment
7. ✅ Crea Azure Container Registry
8. ✅ Build y push imágenes Docker (backend + frontend)
9. ✅ Deploy Backend Container App
10. ✅ Deploy Frontend Container App
11. ✅ Configura CORS
12. ✅ Ejecuta migraciones de base de datos
13. ✅ Guarda configuración en `azure-deployment-config.json`

**Output**: Guarda configuración en `../azure-deployment-config.json`

---

### 2. `azure-demo-pause.ps1` - Pausar Servicios

**Propósito**: Escala los Container Apps a 0 réplicas para ahorrar costos.

**Uso**:
```powershell
.\azure-demo-pause.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Parámetros**:
- `ResourceGroup`: Nombre del Resource Group (default: `rg-plantitas-demo-temp`)

**Duración**: ~10 segundos

**Qué hace**:
- Escala Backend a 0 réplicas (min=0, max=0)
- Escala Frontend a 0 réplicas (min=0, max=0)
- PostgreSQL y Storage siguen activos

**Costo pausado**: ~$0.50/día (solo PostgreSQL + Storage)

---

### 3. `azure-demo-resume.ps1` - Reactivar Servicios

**Propósito**: Reactiva los Container Apps para demos/presentaciones.

**Uso**:
```powershell
.\azure-demo-resume.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Parámetros**:
- `ResourceGroup`: Nombre del Resource Group (default: `rg-plantitas-demo-temp`)

**Duración**: ~10 segundos + 30-60 segundos para que los servicios estén listos

**Qué hace**:
- Escala Backend (min=0, max=2)
- Escala Frontend (min=0, max=2)
- Muestra URLs de acceso

**⏱️ Tiempo de warmup**: 30-60 segundos hasta que la app responde

---

### 4. `azure-cleanup.ps1` - Eliminar Recursos

**Propósito**: Elimina TODOS los recursos del Resource Group.

**Uso**:
```powershell
.\azure-cleanup.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Parámetros**:
- `ResourceGroup`: Nombre del Resource Group (default: `rg-plantitas-demo-temp`)
- `Force`: Omite confirmaciones (usar con precaución)

**Duración**: 5-10 minutos (en background)

**⚠️ ADVERTENCIA**: Esta acción es **IRREVERSIBLE**. Se perderán:
- Base de datos PostgreSQL + todos los datos
- Storage Account + todas las imágenes
- Container Apps
- Container Registry + imágenes Docker
- Logs y configuraciones

**Qué hace**:
1. Lista todos los recursos a eliminar
2. Solicita doble confirmación
3. Crea backup de `azure-deployment-config.json`
4. Crea log de eliminación
5. Elimina el Resource Group (y todos sus recursos)

**Output**: 
- `../azure-deployment-config-backup-<timestamp>.json`
- `../azure-deletion-log-<timestamp>.json`

---

### 5. `validate-env-azure.ps1` - Validar Configuración

**Propósito**: Valida que todas las variables de entorno estén correctamente configuradas.

**Uso**:
```powershell
.\validate-env-azure.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Parámetros**:
- `ResourceGroup`: Nombre del Resource Group (default: `rg-plantitas-demo-temp`)

**Duración**: ~10 segundos

**Qué valida**:
1. ✅ Backend: 15 variables requeridas
2. ✅ Frontend: 3 variables requeridas
3. ✅ Valores correctos (`DEBUG=false`, `ENVIRONMENT=production`, etc.)
4. ✅ CORS configuration (frontend URL en backend CORS_ORIGINS)
5. ✅ API URL (backend URL en frontend NEXT_PUBLIC_API_URL)
6. ✅ Conectividad (test de `/health`)

**Output**: Reporte de validación con errores/warnings

---

## 🔄 Flujo de Trabajo Típico

### Deployment Inicial

```powershell
# 1. Deploy completo
cd scripts
.\azure-deploy-full.ps1 -DBPassword "Pass123!" -GeminiApiKey "key"

# 2. Validar configuración
.\validate-env-azure.ps1

# 3. Probar la aplicación
# Abrir URLs mostradas en el output
```

### Uso Diario (Demo Académica)

```powershell
# Por la mañana (antes de demo):
.\azure-demo-resume.ps1
# Esperar 60 segundos

# Por la noche (después de demo):
.\azure-demo-pause.ps1
```

### Al Finalizar Demo

```powershell
# Eliminar todos los recursos
.\azure-cleanup.ps1

# Confirmar que no quedan recursos
az group exists --name rg-plantitas-demo-temp
# Debe devolver: false
```

---

## 💡 Tips y Mejores Prácticas

### Ahorro de Costos

1. **Pausar cuando no uses**: 
   - Usar `azure-demo-pause.ps1` después de cada demo
   - Ahorro: ~$0.50/día vs $1.00/día activo

2. **Scale to Zero automático**:
   - Los Container Apps ya están configurados con `min-replicas=0`
   - Después de 5 minutos sin tráfico, escalan a 0 automáticamente

3. **Eliminar al finalizar**:
   - Usar `azure-cleanup.ps1` cuando termine el semestre
   - Preserva tus $85-90 créditos restantes

### Troubleshooting

**Problema**: `azure-deploy-full.ps1` falla en build de imágenes

**Solución**:
```powershell
# Verificar que estás en el directorio correcto
cd C:\Users\franq\Desktop\ia-aplicada\projecto-ia-aplicada\scripts

# Verificar que Dockerfiles existen
Test-Path ..\backend\Dockerfile
Test-Path ..\frontend\Dockerfile
```

**Problema**: Backend no responde después de `azure-demo-resume.ps1`

**Solución**:
```powershell
# Esperar 60 segundos adicionales
Start-Sleep -Seconds 60

# Ver logs
az containerapp logs show --name plantitas-backend --resource-group rg-plantitas-demo-temp --follow

# Reiniciar manualmente
az containerapp revision restart --name plantitas-backend --resource-group rg-plantitas-demo-temp
```

**Problema**: CORS errors en frontend

**Solución**:
```powershell
# Ejecutar validación
.\validate-env-azure.ps1

# Actualizar CORS manualmente
$FRONTEND_URL = az containerapp show --name plantitas-frontend --resource-group rg-plantitas-demo-temp --query properties.configuration.ingress.fqdn --output tsv
az containerapp update --name plantitas-backend --resource-group rg-plantitas-demo-temp --set-env-vars "CORS_ORIGINS=https://$FRONTEND_URL"
```

---

## 📊 Monitoreo de Costos

### Ver Costos en Tiempo Real

```powershell
# Costo de hoy
az consumption usage list `
  --start-date (Get-Date).ToString("yyyy-MM-dd") `
  --end-date (Get-Date).ToString("yyyy-MM-dd") `
  --query "[?contains(instanceName, 'plantitas')]" `
  --output table

# Costo de la última semana
az consumption usage list `
  --start-date (Get-Date).AddDays(-7).ToString("yyyy-MM-dd") `
  --end-date (Get-Date).ToString("yyyy-MM-dd") `
  --query "[?contains(instanceName, 'plantitas')]" `
  --output table
```

### Configurar Alertas de Presupuesto

```powershell
# Alerta al gastar $30 (30% de $100)
az consumption budget create `
  --budget-name "plantitas-demo-budget" `
  --amount 30 `
  --time-grain Monthly `
  --start-date (Get-Date).ToString("yyyy-MM-01") `
  --end-date (Get-Date).AddMonths(1).ToString("yyyy-MM-01") `
  --resource-group rg-plantitas-demo-temp
```

---

## 🔐 Seguridad

### Gestión de Secrets

**❌ NUNCA**:
- Commits de contraseñas o API keys en Git
- Shares de `azure-deployment-config.json` (contiene secrets)
- Hardcoding de secrets en scripts

**✅ SIEMPRE**:
- Usar parámetros para passwords
- Generar JWT secrets únicos (64 caracteres)
- Rotar API keys regularmente

### Permisos Mínimos

Los scripts requieren permisos de:
- Contributor en el Resource Group
- Lector en la Subscription (para ver costos)

---

## 📚 Referencias

- **Documentación completa**: [AZURE_DEMO_TEMPORAL.md](../AZURE_DEMO_TEMPORAL.md)
- **Variables de entorno**: [AZURE_ENVIRONMENT_VARIABLES.md](../AZURE_ENVIRONMENT_VARIABLES.md)
- **Guía rápida**: [AZURE_DEPLOYMENT_QUICKSTART.md](../AZURE_DEPLOYMENT_QUICKSTART.md)

---

## 🐛 Reportar Issues

Si encuentras problemas con los scripts:

1. Ejecutar con `-Verbose`:
```powershell
.\azure-deploy-full.ps1 -Verbose
```

2. Revisar logs de Azure:
```powershell
az monitor activity-log list --resource-group rg-plantitas-demo-temp --output table
```

3. Contactar al equipo con:
   - Output completo del script
   - Logs de Azure CLI
   - Resource Group y región usados

---

**Autor**: Franco Garcete  
**Proyecto**: Asistente Plantitas  
**Fecha**: 12 de Noviembre de 2025  
**Versión Scripts**: 1.0
