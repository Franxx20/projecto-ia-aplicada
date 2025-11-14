# 📋 Guía: Subir Épica a Azure DevOps

## 🎯 Objetivo

Este script crea automáticamente la épica **EPIC-DEPLOY-001** con sus **26 tareas** en Azure DevOps Boards.

---

## 📝 Pre-requisitos

1. **Azure DevOps CLI** instalado
   ```powershell
   # Verificar instalación
   az --version
   
   # Si no está instalado
   az extension add --name azure-devops
   ```

2. **Personal Access Token (PAT)** de Azure DevOps
   - Ir a: `https://dev.azure.com/{tu-org}/_usersSettings/tokens`
   - Click en "New Token"
   - Nombre: "Deployment Epic Creator"
   - Scopes: **Work Items (Read, Write, Manage)**
   - Expiration: 30 días
   - Click "Create" y **copiar el token**

---

## ⚙️ Configuración

### Paso 1: Editar el Script

Abre `scripts/create-epic-in-azuredevops.ps1` y edita las líneas 12-14:

```powershell
# CAMBIAR ESTAS VARIABLES
$ORGANIZATION_URL = "https://dev.azure.com/tu-organizacion"  # 👈 TU ORGANIZACIÓN
$PROJECT_NAME = "projecto-ia-aplicada"  # 👈 TU PROYECTO
$AREA_PATH = "$PROJECT_NAME"  # Ajustar si tienes área específica
```

**Ejemplo real**:
```powershell
$ORGANIZATION_URL = "https://dev.azure.com/unlam-plantitas"
$PROJECT_NAME = "Asistente-Plantitas"
$AREA_PATH = "Asistente-Plantitas\Backend"  # Si tienes áreas específicas
```

---

## 🚀 Ejecución

### Opción A: Script Automático (Recomendado)

El script te guiará para configurar la conexión:

```powershell
# Ejecutar desde la raíz del proyecto
.\scripts\create-epic-in-azuredevops.ps1
```

**El script hará**:
1. Verificar conexión a Azure DevOps
2. Solicitar PAT si no estás conectado
3. Crear la épica EPIC-DEPLOY-001
4. Crear las 26 tareas vinculadas
5. Mostrar resumen con URLs

---

### Opción B: Configuración Manual

Si prefieres configurar manualmente antes:

```powershell
# 1. Login con tu PAT
echo "TU_PAT_AQUI" | az devops login --organization https://dev.azure.com/tu-org

# 2. Configurar defaults
az devops configure --defaults `
    organization=https://dev.azure.com/tu-org `
    project=projecto-ia-aplicada

# 3. Ejecutar script
.\scripts\create-epic-in-azuredevops.ps1
```

---

## 📊 Qué se Crea

### Épica
- **Título**: EPIC-DEPLOY-001: Deployment a Azure para Estudiantes
- **Descripción**: Estrategia completa, arquitectura, 7 fases
- **Estimación**: 6-8 horas
- **Costo**: $0/mes

### 26 Tareas Organizadas

| Fase | Tareas | Tiempo |
|------|--------|--------|
| 1. Preparación | 5 | 55 min |
| 2. Infraestructura | 4 | 75 min |
| 3. Deployment | 5 | 110 min |
| 4. Pruebas | 3 | 65 min |
| 5. Controles Gasto | 3 | 50 min |
| 6. Documentación | 4 | 110 min |
| 7. Post-Demo | 2 | 10 min |

**Cada tarea incluye**:
- ✅ Criterios de aceptación detallados
- ⏱️ Estimación en minutos
- 🎯 Prioridad (Alta/Media/Baja)
- 🔗 Vinculación automática a la épica
- 📝 Referencia al documento completo

---

## ✅ Verificación

Después de ejecutar el script:

1. **Abrir Azure Boards**:
   ```
   https://dev.azure.com/{tu-org}/{tu-proyecto}/_boards/board
   ```

2. **Buscar la épica**: Filtrar por "EPIC-DEPLOY-001"

3. **Ver tareas vinculadas**: Click en la épica → Ver "Related Work"

4. **Verificar backlog**:
   ```
   https://dev.azure.com/{tu-org}/{tu-proyecto}/_backlogs/backlog
   ```

---

## 🛠️ Comandos Útiles

### Ver work items creados
```powershell
# Listar épicas
az boards work-item query --wiql "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.WorkItemType] = 'Epic' ORDER BY [System.CreatedDate] DESC"

# Listar tareas de la épica
az boards work-item query --wiql "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.Parent] = {EPIC_ID}"
```

### Actualizar work item
```powershell
az boards work-item update --id {ID} --state "In Progress"
```

### Eliminar work items (si algo sale mal)
```powershell
az boards work-item delete --id {ID} --yes
```

---

## 🐛 Troubleshooting

### Error: "Personal Access Token expired"
```powershell
# Crear nuevo PAT y reconectar
echo "NUEVO_PAT" | az devops login --organization https://dev.azure.com/tu-org
```

### Error: "Project not found"
```powershell
# Verificar proyectos disponibles
az devops project list --output table

# Usar el nombre exacto del proyecto
$PROJECT_NAME = "nombre-exacto-del-proyecto"
```

### Error: "Area path not found"
```powershell
# Listar áreas disponibles
az boards area project list --output table

# Usar el área correcta
$AREA_PATH = "nombre-exacto-del-area"
```

### Las tareas no se vinculan a la épica
```powershell
# Vincular manualmente
az boards work-item relation add `
    --id {TASK_ID} `
    --relation-type "Parent" `
    --target-id {EPIC_ID}
```

---

## 📚 Referencias

- **Azure DevOps CLI**: https://learn.microsoft.com/en-us/cli/azure/devops
- **Work Items API**: https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/
- **Personal Access Tokens**: https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate

---

## 📞 Soporte

Si tienes problemas:

1. **Verificar versión de Azure CLI**:
   ```powershell
   az --version
   az extension show --name azure-devops
   ```

2. **Actualizar extensión**:
   ```powershell
   az extension update --name azure-devops
   ```

3. **Revisar logs**: El script muestra cada paso con emojis de estado

---

## ✨ Siguiente Paso

Después de crear la épica en Azure DevOps:

1. **Organizar en Sprint**: Asignar tareas al Sprint actual
2. **Asignar responsable**: Asignarte las tareas
3. **Comenzar trabajo**: Mover primera tarea a "In Progress"
4. **Seguir épica**: Ver `EPICA_DEPLOYMENT_AZURE_ESTUDIANTES.md` para detalles

---

**¡Listo para empezar el deployment! 🚀**
