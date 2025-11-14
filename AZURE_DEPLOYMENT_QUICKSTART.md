# 🚀 Azure Deployment - Guía Rápida

**Demo Académica Temporal** | **Costo estimado: $10-15 por 4 semanas**

---

## ⚡ Quick Start (30-45 minutos)

### 1. Prerequisites

```powershell
# Verificar Azure CLI
az --version

# Login
az login

# Verificar créditos
az account show
```

### 2. Deploy Completo (Automatizado)

```powershell
cd scripts

# Ejecutar deployment completo
.\azure-deploy-full.ps1 `
  -ResourceGroup "rg-plantitas-demo-temp" `
  -Location "eastus" `
  -DBPassword "TuPasswordSeguro123!" `
  -GeminiApiKey "tu-gemini-api-key"
```

**⏱️ Duración**: 30-45 minutos

**Qué hace**:
- ✅ Crea Resource Group
- ✅ Deploy PostgreSQL Flexible Server (B1ms)
- ✅ Deploy Azure Blob Storage
- ✅ Crea Container Apps Environment
- ✅ Crea Azure Container Registry
- ✅ Build y push imágenes Docker
- ✅ Deploy Backend Container App
- ✅ Deploy Frontend Container App
- ✅ Configura CORS
- ✅ Ejecuta migraciones de DB

---

## 📋 Gestión de Servicios

### Pausar (cuando no usas)

```powershell
.\scripts\azure-demo-pause.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Costo pausado**: ~$0.50/día (solo DB + Storage)

### Reactivar (para demos)

```powershell
.\scripts\azure-demo-resume.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**Listo en**: ~30-60 segundos

### Eliminar Todo (al finalizar)

```powershell
.\scripts\azure-cleanup.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

**⚠️ Acción irreversible** - Elimina todos los recursos

---

## 🔐 Configuración de Variables

### Validar Configuración

```powershell
.\scripts\validate-env-azure.ps1 -ResourceGroup "rg-plantitas-demo-temp"
```

### Variables Requeridas

Ver documentación completa en: [AZURE_ENVIRONMENT_VARIABLES.md](AZURE_ENVIRONMENT_VARIABLES.md)

**Backend (15 variables)**:
- Database: `DATABASE_URL`
- Storage: `AZURE_STORAGE_CONNECTION_STRING`
- Auth: `JWT_SECRET_KEY`
- API: `GEMINI_API_KEY`
- CORS: `CORS_ORIGINS`

**Frontend (3 variables)**:
- API: `NEXT_PUBLIC_API_URL`
- Env: `NODE_ENV=production`

---

## 💰 Costos

### Breakdown (4 semanas activo 8h/día)

| Servicio | Costo/mes | 4 semanas |
|----------|-----------|-----------|
| Frontend Container | $3-5 | ~$3 |
| Backend Container | $3-5 | ~$3 |
| PostgreSQL B1ms | $15-20 | ~$18 |
| Blob Storage | $0.50 | ~$0.50 |
| **TOTAL** | | **~$24-25** |

**Con pausas** (solo usar 3 días/semana): **~$10-12**

**Sobran de $100**: **$75-90**

---

## 📊 Monitoreo

### Ver Costos Actuales

```powershell
az consumption usage list `
  --start-date (Get-Date).AddDays(-7).ToString("yyyy-MM-dd") `
  --end-date (Get-Date).ToString("yyyy-MM-dd") `
  --query "[?contains(instanceName, 'plantitas')]" `
  --output table
```

### Obtener URLs

```powershell
# Backend
$BACKEND = az containerapp show `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Write-Host "Backend: https://$BACKEND"
Write-Host "API Docs: https://$BACKEND/docs"

# Frontend
$FRONTEND = az containerapp show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --query properties.configuration.ingress.fqdn `
  --output tsv

Write-Host "Frontend: https://$FRONTEND"
```

---

## 🆘 Troubleshooting

### Logs del Backend

```powershell
az containerapp logs show `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp `
  --follow
```

### Logs del Frontend

```powershell
az containerapp logs show `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp `
  --follow
```

### Reiniciar Servicios

```powershell
# Backend
az containerapp revision restart `
  --name plantitas-backend `
  --resource-group rg-plantitas-demo-temp

# Frontend
az containerapp revision restart `
  --name plantitas-frontend `
  --resource-group rg-plantitas-demo-temp
```

---

## 📚 Documentación Completa

- **[AZURE_DEMO_TEMPORAL.md](AZURE_DEMO_TEMPORAL.md)** - Guía completa (1000+ líneas)
- **[AZURE_ENVIRONMENT_VARIABLES.md](AZURE_ENVIRONMENT_VARIABLES.md)** - Variables de entorno
- **[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)** - Comparación de opciones

---

## ✅ Checklist

### Pre-Deployment

- [ ] Azure CLI instalado
- [ ] Azure for Students activado ($100 créditos)
- [ ] Gemini API Key obtenida
- [ ] Contraseña PostgreSQL preparada (8+ chars, segura)

### Post-Deployment

- [ ] Backend responde en `/health`
- [ ] Frontend carga correctamente
- [ ] Login funciona
- [ ] Subida de imágenes funciona
- [ ] Identificación de plantas funciona
- [ ] HTTPS habilitado (automático)

### Al Finalizar Demo

- [ ] Exportar datos importantes
- [ ] Backup final de DB
- [ ] Ejecutar `azure-cleanup.ps1`
- [ ] Verificar que no quedan recursos ($0/mes)

---

## 🎯 Timeline

| Fase | Duración | Costo acumulado |
|------|----------|-----------------|
| **Setup inicial** | 1 día | $0.50 |
| **Semana 1-2** (demos) | 2 semanas | $7-10 |
| **Semana 3-4** (demos) | 2 semanas | $15-20 |
| **Cleanup final** | 1 hora | $20-25 |
| **Sobra de $100** | | **$75-80** |

---

## 📞 Soporte

- **Azure Docs**: https://learn.microsoft.com/azure/container-apps/
- **Azure for Students**: https://azure.microsoft.com/free/students/
- **Troubleshooting**: Ver [AZURE_DEMO_TEMPORAL.md](AZURE_DEMO_TEMPORAL.md#troubleshooting)

---

**Autor**: Franco Garcete  
**Proyecto**: Asistente Plantitas  
**Fecha**: 12 de Noviembre de 2025  
**Deployment**: Azure Container Apps
