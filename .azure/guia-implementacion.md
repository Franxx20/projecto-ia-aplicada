# 🚀 Guía de Implementación - Asistente Plantitas Ágil

Esta guía te ayudará a implementar el proyecto ágil "Asistente de Jardinería y Cuidado de Plantas" en Azure DevOps paso a paso.

## 🔧 Configuración de Acceso a Azure DevOps

Antes de comenzar, asegúrate de tener acceso configurado a Azure DevOps:

### Acceso Web
- Accede a https://dev.azure.com/tu-organizacion
- Verifica que puedes ver proyectos y work items

### Acceso desde Editores (MCP)
Si necesitas conectar VS Code u otros editores con Azure DevOps:

**📚 Guía completa:** [Azure DevOps MCP Setup](azure-devops-mcp-setup.md)

**Solución rápida de errores:** [Solución Error Autenticación](SOLUCION-ERROR-AUTENTICACION.md)

### Errores Comunes de Autenticación

Si recibes el error `AADSTS900021: Invalid tenant identifier`, consulta:
- [SOLUCION-ERROR-AUTENTICACION.md](SOLUCION-ERROR-AUTENTICACION.md) - Solución rápida
- [azure-devops-mcp-setup.md](azure-devops-mcp-setup.md) - Guía completa

## 📋 PASO 1: Configuración Inicial de Azure DevOps

### 1.1 Crear Proyecto
```bash
# Accede a https://dev.azure.com/tu-organizacion
# Crea nuevo proyecto: "Asistente Plantitas"
# Selecciona: Git + Agile Process Template
```

### 1.2 Configurar Team y Áreas
```
Areas:
├── Asistente Plantitas (Root)
│   ├── Backend (FastAPI/Python)
│   ├── Frontend (Angular/TypeScript)  
│   ├── AI (Machine Learning/LLM)
│   ├── DevOps (Infrastructure/CI-CD)
│   └── Marketplace (External APIs)
```

### 1.3 Configurar Iteraciones
```
Iterations:
├── Asistente Plantitas (Root)
│   ├── Sprint 1 (29/09/2025 - 12/10/2025) - Fundación
│   ├── Sprint 2 (13/10/2025 - 26/10/2025) - MVP 
│   ├── Sprint 3 (27/10/2025 - 09/11/2025) - Asistente IA
│   └── Sprint 4 (10/11/2025 - 23/11/2025) - Final
```

## 📊 PASO 2: Importar Work Items

### 2.1 Usar CSV de Importación
1. Ve a **Azure DevOps** → **Boards** → **Work Items**
2. Selecciona **"Import Work Items"**
3. Sube el archivo `workitems-import.csv`
4. Mapea las columnas correctamente
5. Ejecuta la importación

### 2.2 Verificar Jerarquía
```
✅ 4 Epics creadas
✅ 13 Features vinculadas
✅ 21 User Stories definidas  
✅ 35+ Tasks técnicas
✅ Criterios de aceptación completos
```

## 🎯 PASO 3: Configurar Boards Ágiles

### 3.1 Customizar Kanban Board

#### Estados Personalizados
```yaml
User Story States:
  - New: Historia creada
  - Ready: Lista para desarrollo  
  - Active: En progreso
  - In Review: Code review/testing
  - Done: Completada

Task States:
  - To Do: Pendiente
  - In Progress: Desarrollando
  - Testing: En pruebas  
  - Done: Terminada
```

#### Configurar WIP Limits
```yaml
Columns:
  Ready: Max 8 items
  Active: Max 6 items
  In Review: Max 4 items
```

#### Swim Lanes por Especialidad
- **Backend**: FastAPI, Database, APIs
- **Frontend**: Angular, UI/UX, Components  
- **AI/ML**: Computer Vision, LLM, APIs
- **DevOps**: Infrastructure, CI/CD, Monitoring

### 3.2 Sprint Planning Board
```bash
# Configurar Sprint Planning
1. Backlog Refinement: Jueves antes de sprint
2. Sprint Planning: Lunes 9:00 AM (4 horas)
3. Daily Standups: Diario 9:00 AM (15 min)
4. Sprint Review: Viernes 2:00 PM (2 horas)  
5. Retrospective: Viernes 4:00 PM (1 hora)
```

## 👥 PASO 4: Configurar Equipos y Roles

### 4.1 Crear Teams
```yaml
Teams:
  - name: "Plantitas Dev Team"
    members: 5
    permissions:
      - Create work items
      - Edit work items  
      - Manage sprints
      - View analytics

  - name: "Plantitas Stakeholders"  
    members: 2
    permissions:
      - View work items
      - Comment
      - View reports
```

### 4.2 Asignar Roles y Responsabilidades
```yaml
Scrum Master/PO:
  - Sprint planning facilitation
  - Backlog management
  - Stakeholder communication
  - Remove impediments

Backend Developers (2):  
  - FastAPI development
  - Database design
  - API integration
  - Security implementation

IA/ML Specialist (1):
  - Computer vision models
  - LLM integration  
  - Plant identification
  - Disease detection

DevOps/QA Engineer (1):
  - Infrastructure setup
  - CI/CD pipelines
  - Testing automation
  - Monitoring setup
```

## 🔧 PASO 5: Configurar Automatización

### 5.1 Work Item Rules

#### Auto-Assignment por Área
```yaml
# Regla: Auto-asignar por área
when: 
  - WorkItemType = 'Task'
  - AreaPath CHANGED
then:
  - if AreaPath = 'Backend': assign to backend-dev
  - if AreaPath = 'Frontend': assign to frontend-dev  
  - if AreaPath = 'AI': assign to ai-specialist
  - if AreaPath = 'DevOps': assign to devops-engineer
```

#### Sprint Health Alerts
```yaml
# Regla: Alerta sprint en riesgo
when:
  - Sprint.DaysRemaining <= 3  
  - Sprint.CompletionRate < 70%
then:
  - notify: scrum-master@team.com
  - create: Risk work item
```

#### Definition of Done Validation
```yaml  
# Regla: Validar DoD al marcar Done
when: UserStory.State = 'Done'
then:
  - require: CodeReview = 'Approved'
  - require: TestCoverage >= 80%
  - require: Documentation = 'Updated'
```

### 5.2 Dashboard y Métricas

#### Sprint Dashboard
```yaml
Widgets:
  - Sprint Burndown Chart
  - Sprint Capacity vs Planned  
  - Cumulative Flow Diagram
  - Velocity Chart
  - Test Results Summary
  - Code Coverage Trend
```

#### Team Performance Dashboard  
```yaml
Widgets:
  - Team Velocity (last 6 sprints)
  - Lead Time Trend
  - Cycle Time by Work Item Type
  - Bug Trend Analysis
  - Feature Delivery Rate
```

## 🔄 PASO 6: Configurar CI/CD Integration

### 6.1 Vincular Work Items con Commits
```bash
# Formato de commits
git commit -m "feat: implementar login JWT #US-002

- Agregar endpoint POST /auth/login
- Implementar validación de credenciales  
- Configurar JWT token generation
- Tests unitarios para auth service

Closes #US-002"
```

### 6.2 Pipeline con Work Item Updates
```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

variables:
  - group: plantitas-secrets

stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    steps:
    - task: UpdateWorkItems@1
      inputs:
        workItemIds: '$(System.PullRequest.AssociatedWorkItems)'  
        state: 'In Review'
        
- stage: Deploy
  jobs:
  - job: DeployToAzure
    steps:  
    - task: UpdateWorkItems@1
      inputs:
        workItemIds: '$(System.PullRequest.AssociatedWorkItems)'
        state: 'Done'
```

## 📈 PASO 7: Métricas y Reportes

### 7.1 Queries Personalizadas

#### Velocity por Sprint
```sql
SELECT 
  [System.IterationPath],
  SUM(CAST([Microsoft.VSTS.Scheduling.StoryPoints] AS float)) as Velocity
FROM WorkItems 
WHERE [System.WorkItemType] = 'User Story'
  AND [System.State] = 'Done'  
  AND [System.IterationPath] UNDER 'Asistente Plantitas'
GROUP BY [System.IterationPath]
ORDER BY [System.IterationPath]
```

#### Burndown Actual vs Planeado
```sql
SELECT 
  [System.Id],
  [System.Title],
  [Microsoft.VSTS.Scheduling.StoryPoints],
  [System.CreatedDate],
  [Microsoft.VSTS.Common.ResolvedDate],
  [System.IterationPath]
FROM WorkItems
WHERE [System.IterationPath] = 'Asistente Plantitas\Sprint 1'  
  AND [System.WorkItemType] IN ('User Story', 'Task')
```

#### Calidad de Código
```sql  
SELECT
  [System.AreaPath],
  COUNT(*) as BugCount,
  AVG(CAST([Microsoft.VSTS.Common.Severity] AS float)) as AvgSeverity
FROM WorkItems
WHERE [System.WorkItemType] = 'Bug'
  AND [System.CreatedDate] >= '2025-09-29'
GROUP BY [System.AreaPath]
```

### 7.2 PowerBI Integration
```yaml
# Configurar Power BI con Azure DevOps
Data Sources:
  - Azure DevOps Analytics
  - Azure DevOps REST API  
  - Custom queries

Reports:
  - Sprint Health Dashboard
  - Team Performance Metrics
  - Feature Delivery Timeline  
  - Quality Trends Analysis
```

## 🎯 PASO 8: Ceremonias Ágiles

### 8.1 Sprint Planning Template

```markdown
# Sprint X Planning - [Fecha]

## Objetivos del Sprint
- [ ] Objetivo 1: [Descripción]  
- [ ] Objetivo 2: [Descripción]
- [ ] Objetivo 3: [Descripción]

## Capacity Planning
| Team Member | Capacity (hours) | Availability |
|-------------|------------------|--------------|
| Developer 1 | 72 | 90% |
| Developer 2 | 80 | 100% |
| AI Specialist | 76 | 95% |
| DevOps | 64 | 80% |

## User Stories Selected
| ID | Title | Story Points | Assignee |
|----|-------|-------------|----------|
| US-001 | [Story] | 5 | Dev1 |
| US-002 | [Story] | 8 | AI |

## Definition of Ready Checklist  
- [ ] Acceptance criteria defined
- [ ] Dependencies identified
- [ ] Effort estimated  
- [ ] Testable
- [ ] Small enough for sprint
```

### 8.2 Daily Standup Template
```markdown  
# Daily Standup - [Fecha]

## [Team Member Name]
**Ayer completé:**
- Task 1
- Task 2

**Hoy trabajaré en:**  
- Task 3
- Task 4

**Impedimentos/Ayuda:**
- [Ninguno / Descripción]

---
```

### 8.3 Sprint Review Template
```markdown
# Sprint X Review - [Fecha]

## Demo Agenda
1. **Feature 1**: [Owner] - 15 min
2. **Feature 2**: [Owner] - 10 min  
3. **Q&A**: All - 10 min

## Sprint Metrics
- **Velocity**: 42 story points
- **Completion Rate**: 95%  
- **Stories Delivered**: 8/8
- **Bugs Found**: 2

## Stakeholder Feedback
- Feedback 1
- Feedback 2
- Action items

## Next Sprint Preview
- Epic focus: [Name]
- Key features planned
- Dependencies
```

### 8.4 Sprint Retrospective Template
```markdown
# Sprint X Retrospective - [Fecha]

## What Went Well? 🟢
- Item 1
- Item 2
- Item 3

## What Could Improve? 🟡  
- Item 1
- Item 2
- Item 3

## What Should We Stop? 🔴
- Item 1  
- Item 2

## Action Items
| Action | Owner | Due Date |
|--------|--------|----------|
| Action 1 | Person | Date |
| Action 2 | Person | Date |

## Team Health Score: X/10
```

## 🔍 PASO 9: Monitoring y Health Checks

### 9.1 Sprint Health Indicators
```yaml
Green (Healthy):
  - Burndown on track (±10%)
  - Velocity consistent with history  
  - No blocked items >2 days
  - Team capacity utilization 80-90%

Yellow (At Risk):
  - Burndown behind 10-25%
  - 1-2 blocked items
  - Capacity utilization <80% or >95%
  - 1-2 impediments

Red (Critical):  
  - Burndown behind >25%
  - Multiple blocked items
  - Major impediments unresolved  
  - Team capacity issues
```

### 9.2 Quality Gates
```yaml
Definition of Done:
  - [ ] Code review approved (2 reviewers)
  - [ ] Unit tests written and passing
  - [ ] Integration tests passing  
  - [ ] Code coverage ≥ 80%
  - [ ] Documentation updated
  - [ ] Acceptance criteria met
  - [ ] No critical/high bugs
  - [ ] Deployed to dev environment
```

## 🎉 PASO 10: Go-Live y Handoff

### 10.1 Sprint 1 Launch Checklist
```bash
Infrastructure:
✅ Azure DevOps project configured  
✅ Git repositories created
✅ CI/CD pipelines setup
✅ Development environment ready

Team:  
✅ Roles and responsibilities defined
✅ Sprint planning completed
✅ Daily standup scheduled  
✅ Work items created and prioritized

Stakeholders:
✅ Project charter reviewed
✅ MVP scope agreed
✅ Communication plan established
✅ Demo schedule confirmed
```

### 10.2 Handoff Documentation  
```markdown
## Project Handoff - Asistente Plantitas

### Access & Credentials
- Azure DevOps: [URL]
- Azure Subscription: [ID]  
- Repository: [URL]
- Documentation: [Wiki URL]

### Key Contacts  
- Product Owner: [Name/Email]
- Scrum Master: [Name/Email]
- Tech Lead: [Name/Email]

### Important Links
- Sprint Boards: [URL]
- Backlogs: [URL]
- Dashboards: [URL]
- Architecture Docs: [URL]

### Next Steps
1. Complete Sprint 1 planning
2. Begin development Sprint 1  
3. Schedule stakeholder demos
4. Set up monitoring alerts
```

---

## ✅ CHECKLIST FINAL DE IMPLEMENTACIÓN

### Configuración Técnica
- [ ] Proyecto Azure DevOps creado
- [ ] Areas e iteraciones configuradas  
- [ ] Work items importados correctamente
- [ ] Boards personalizados setup
- [ ] Automatización rules configuradas

### Equipo y Procesos  
- [ ] Roles asignados al equipo
- [ ] Ceremonias agendadas
- [ ] Templates de reuniones creados
- [ ] Communication plan establecido
- [ ] Definition of Done acordada

### Herramientas y Integración
- [ ] Git repositories vinculados
- [ ] CI/CD pipelines configurados  
- [ ] Dashboards y métricas setup
- [ ] Notification rules configuradas
- [ ] Documentation wiki creada

### Governance y Calidad
- [ ] Quality gates definidos
- [ ] Code review process establecido
- [ ] Testing strategy definida  
- [ ] Risk mitigation plan creado
- [ ] Stakeholder communication setup

---

**🚀 ¡Tu proyecto ágil "Asistente Plantitas" está listo para comenzar el desarrollo! 🌱**

*Sigue esta guía paso a paso y tendrás un proyecto ágil completamente funcional en Azure DevOps, listo para entregar valor incremental cada 2 semanas.*