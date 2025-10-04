# 📚 Documentación Azure DevOps - Proyecto IA Aplicada

Esta carpeta contiene toda la documentación relacionada con Azure DevOps para el proyecto.

## 📋 Índice de Documentos

### 🔧 Configuración y Solución de Problemas

| Documento | Descripción | Uso |
|-----------|-------------|-----|
| **[SOLUCION-ERROR-AUTENTICACION.md](SOLUCION-ERROR-AUTENTICACION.md)** | ⚡ Solución rápida para errores de autenticación MCP | **¡EMPIEZA AQUÍ!** Si tienes error `AADSTS900021` |
| **[azure-devops-mcp-setup.md](azure-devops-mcp-setup.md)** | 📖 Guía completa de configuración de Azure DevOps MCP | Configuración detallada y troubleshooting avanzado |
| **[guia-implementacion.md](guia-implementacion.md)** | 🚀 Guía de implementación del proyecto en Azure DevOps | Configurar proyecto, boards, sprints, y work items |

### 📊 Planificación Ágil

| Documento | Descripción | Uso |
|-----------|-------------|-----|
| **[proyecto-agile-plan.md](proyecto-agile-plan.md)** | 🌱 Plan ágil completo del proyecto | Roadmap, sprints, épicas y features |
| **[azure-devops-workitems.md](azure-devops-workitems.md)** | 📊 Estructura de work items | Definición de épicas, features, user stories y tasks |
| **[workitems-import.csv](workitems-import.csv)** | 📁 Archivo CSV para importar work items | Importar directamente en Azure DevOps |

## 🚨 Problemas Comunes

### Error: AADSTS900021 - Invalid Tenant Identifier

**Síntoma:**
```
Lo sentimos, tenemos problemas para iniciar su sesión.
AADSTS900021: Requested tenant identifier '00000000-0000-0000-0000-000000000000' 
is not valid.
```

**Solución:** 👉 [SOLUCION-ERROR-AUTENTICACION.md](SOLUCION-ERROR-AUTENTICACION.md)

### Token Expirado o Inválido

**Síntoma:**
- Error 401 Unauthorized
- Error 403 Forbidden

**Solución:** 
1. Crea un nuevo Personal Access Token en Azure DevOps
2. Actualiza el archivo `mcp.json`
3. Reinicia VS Code

Ver [azure-devops-mcp-setup.md](azure-devops-mcp-setup.md#error-token-expirado-o-inválido)

### Organización No Encontrada

**Síntoma:**
```
Organization 'xxx' not found
```

**Solución:**
- Verifica el nombre exacto en `https://dev.azure.com`
- El nombre es case-sensitive (distingue mayúsculas/minúsculas)

Ver [azure-devops-mcp-setup.md](azure-devops-mcp-setup.md#error-organización-no-encontrada)

## 🎯 Flujo de Trabajo Recomendado

### Para Configurar Azure DevOps MCP por Primera Vez:

```
1. Lee → SOLUCION-ERROR-AUTENTICACION.md (solución rápida)
   ↓
2. Si necesitas más detalles → azure-devops-mcp-setup.md (guía completa)
   ↓
3. Verifica tu configuración con los comandos de verificación
   ↓
4. ¡Listo! Ya puedes usar Azure DevOps desde tu editor
```

### Para Configurar el Proyecto en Azure DevOps:

```
1. Lee → guia-implementacion.md
   ↓
2. Revisa → proyecto-agile-plan.md (entender el roadmap)
   ↓
3. Consulta → azure-devops-workitems.md (estructura de work items)
   ↓
4. Importa → workitems-import.csv (en Azure DevOps)
   ↓
5. ¡Proyecto configurado! Comienza el desarrollo
```

## 📖 Estructura del Proyecto Ágil

### 4 Sprints - 8 Semanas

| Sprint | Fechas | Épica | Objetivo |
|--------|--------|-------|----------|
| **Sprint 1** | 29 Sep - 12 Oct | Fundación | Sistema de autenticación + subida de imágenes |
| **Sprint 2** | 13 Oct - 26 Oct | Identificación IA | Motor de IA para identificar plantas |
| **Sprint 3** | 27 Oct - 09 Nov | Asistente LLM | Chat conversacional con LLM |
| **Sprint 4** | 10 Nov - 23 Nov | Diagnóstico | Detección de enfermedades + Marketplace |

Ver detalles completos en [proyecto-agile-plan.md](proyecto-agile-plan.md)

## 🔐 Seguridad

⚠️ **Información Sensible:**
- Los archivos `mcp.json` con tokens NO deben subirse al repositorio
- Los Personal Access Tokens son secretos y personales
- Rota tus tokens cada 90 días
- Usa permisos mínimos necesarios

✅ **Archivos seguros en este repositorio:**
- Toda la documentación en esta carpeta es segura para compartir
- No contiene credenciales ni secretos
- Puedes hacer fork y compartir libremente

## 🆘 ¿Necesitas Ayuda?

### Orden de Consulta:

1. **Problema de autenticación MCP:** → [SOLUCION-ERROR-AUTENTICACION.md](SOLUCION-ERROR-AUTENTICACION.md)
2. **Configuración detallada MCP:** → [azure-devops-mcp-setup.md](azure-devops-mcp-setup.md)
3. **Configuración del proyecto:** → [guia-implementacion.md](guia-implementacion.md)
4. **Planificación y roadmap:** → [proyecto-agile-plan.md](proyecto-agile-plan.md)
5. **Work items:** → [azure-devops-workitems.md](azure-devops-workitems.md)

### Recursos Externos:

- **Azure DevOps Docs:** https://learn.microsoft.com/en-us/azure/devops/
- **Personal Access Tokens:** https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate
- **Azure DevOps REST API:** https://learn.microsoft.com/en-us/rest/api/azure/devops/

## 📝 Notas de Versión

**Versión:** 1.0.0  
**Última actualización:** 2024  
**Mantenedor:** Equipo Proyecto IA Aplicada

---

**¿Encontraste esta documentación útil?** ⭐ Dale una estrella al repositorio!

**¿Tienes sugerencias?** Abre un issue en GitHub con tus ideas de mejora.
