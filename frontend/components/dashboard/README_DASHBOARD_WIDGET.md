# 📊 Dashboard Widget de Salud - Documentación

## 📌 Resumen

Widget para el dashboard principal que muestra un resumen agregado de la salud de todas las plantas del usuario. Proporciona una vista rápida del estado general del jardín con alertas, estadísticas y análisis recientes.

---

## ✨ Características

### **1. Estadísticas Agregadas**
- **Total de plantas** analizadas vs total en el jardín
- **Plantas saludables** (excelente + saludable)
- **Plantas que necesitan atención** (necesita_atención)
- **Plantas críticas** (enfermedad + plaga + crítica)
- **Porcentaje de salud** con progress bar visual
- **Confianza promedio** de todos los análisis

### **2. Alertas Críticas**
- **Banner rojo** para plantas en estado crítico/enfermedad/plaga
- Lista de plantas críticas con:
  - Nombre de la planta
  - Estado actual
  - Click para navegar a detalle
- **Icono de alerta** (⚠️) visible
- Hover effect para mejor UX

### **3. Últimos Análisis**
- Muestra los **5 análisis más recientes** de todas las plantas
- Para cada análisis:
  - 🌟 Emoji del estado de salud
  - Nombre de la planta
  - Días desde el análisis ("Hoy", "Hace X días")
  - Badge de confianza (%)
  - Click para navegar

### **4. Estados del Widget**

#### **Loading State**
```tsx
<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
```
- Spinner verde animado
- Mensaje "Cargando..."

#### **Error State**
```tsx
<div className="bg-red-50 border border-red-200 rounded-lg p-4">
  <AlertCircle />
  <p>Error al cargar datos de salud</p>
  <Button>Reintentar</Button>
</div>
```
- Banner rojo con icono de error
- Mensaje descriptivo
- Botón de reintentar

#### **Empty State - Sin Plantas**
```tsx
<Leaf className="w-12 h-12 text-gray-400" />
<h3>No hay plantas registradas</h3>
<p>Agrega plantas a tu jardín...</p>
<Button>Agregar Primera Planta</Button>
```
- Icono de hoja gris
- Mensaje amigable
- CTA para agregar plantas

#### **Empty State - Sin Análisis**
```tsx
<Activity className="w-12 h-12 text-gray-400" />
<h3>No hay análisis de salud</h3>
<p>Realiza el primer análisis...</p>
<Button>Analizar Plantas</Button>
```
- Icono de actividad
- Mensaje para iniciar análisis
- CTA para analizar

---

## 🎨 Diseño Visual

### **Layout**
```
┌─────────────────────────────────┐
│ 🏃 Salud del Jardín       🔄   │ ← Header con refresh
│ X de Y plantas analizadas       │ ← Subtitle
├─────────────────────────────────┤
│ ⚠️ ALERTAS CRÍTICAS             │ ← Banner rojo (si hay)
│   • Planta 1 - Enfermedad       │
│   • Planta 2 - Plaga            │
├─────────────────────────────────┤
│  [42]    [12]    [3]            │ ← Stats grid
│ Saludables Atención Críticas    │
├─────────────────────────────────┤
│ Salud General         [██░░] 75%│ ← Progress bar
├─────────────────────────────────┤
│ 🏃 Confianza Promedio    85.5%  │ ← Badge
├─────────────────────────────────┤
│ Análisis Recientes              │
│ ┌─────────────────────────────┐ │
│ │ 🌟 Mi Potus    Hoy    92.5% │ │ ← Recent analysis
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ ⚠️ Ficus  Hace 2 días  65%  │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### **Colores**
- **Verde** (`green-600`): Saludables, success, iconos principales
- **Amarillo** (`yellow-600`): Necesitan atención, warnings
- **Rojo** (`red-600`): Críticas, errores, alertas
- **Azul** (`blue-600`): Confianza, información
- **Gris** (`gray-400`): Empty states, disabled

### **Espaciado**
- Padding interno: `p-4` (1rem)
- Gap entre secciones: `space-y-6` (1.5rem)
- Gap en grids: `gap-4` (1rem)
- Border radius: `rounded-lg` (0.5rem)

---

## 🔧 Props

```typescript
interface SaludWidgetProps {
  /** Clase CSS adicional para customización */
  className?: string
}
```

**Uso:**
```tsx
<SaludWidget />
<SaludWidget className="mb-8" />
<SaludWidget className="col-span-2" />
```

---

## 📊 Tipos de Datos

### **SaludJardinStats** (Interno)
```typescript
interface SaludJardinStats {
  total_plantas: number
  total_con_analisis: number
  saludables: number
  necesitan_atencion: number
  criticas: number
  porcentaje_saludables: number  // 0-100
  promedio_confianza: number     // 0-100
  tendencia_general?: 'mejorando' | 'estable' | 'empeorando'
}
```

### **PlantaCritica** (Interno)
```typescript
interface PlantaCritica {
  planta_id: number
  nombre: string
  estado: string  // "Enferma", "Plaga Detectada", etc.
  dias_desde_analisis: number
}
```

---

## ⚙️ Lógica de Cálculo

### **1. Clasificación de Estados**
```typescript
// Saludables
if (estado === 'excelente' || estado === 'saludable') {
  saludables++
}

// Necesitan atención
else if (estado === 'necesita_atencion') {
  necesitanAtencion++
}

// Críticas
else {
  // enfermedad, plaga, critica
  criticas++
  agregarAListaCriticas()
}
```

### **2. Porcentaje de Salud**
```typescript
porcentajeSaludables = (saludables / total_con_analisis) * 100
```

### **3. Confianza Promedio**
```typescript
promedioConfianza = sumaConfianza / total_con_analisis
```

### **4. Últimos Análisis**
1. Obtener historial de cada planta (límite 2)
2. Combinar todos los análisis
3. Ordenar por `fecha_analisis` DESC
4. Tomar top 5

---

## 🔗 Integración con Servicios

### **Services Utilizados**

#### **1. dashboardService.obtenerPlantas()**
```typescript
const plantas = await dashboardService.obtenerPlantas(100, 0)
```
- Obtiene todas las plantas del usuario
- Límite: 100 plantas
- Offset: 0 (desde inicio)

#### **2. saludService.obtenerEstadisticas()**
```typescript
const stats = await saludService.obtenerEstadisticas(planta.id)
```
- Por cada planta
- Retorna: último estado, confianza promedio, días desde análisis, tendencia

#### **3. saludService.obtenerHistorial()**
```typescript
const historial = await saludService.obtenerHistorial(planta.id, {
  limite: 2,
  offset: 0
})
```
- Últimos 2 análisis por planta
- Para construir lista de "Análisis Recientes"

---

## 🚀 Uso en Dashboard

### **Ubicación**
El widget se coloca **después de las estadísticas** (Stats Cards) y **antes del grid de plantas**:

```tsx
{/* Stats - Cards existentes */}
<div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
  {/* Total Plantas, Necesitan Riego, etc. */}
</div>

{/* Health Widget - NUEVO */}
<div className="mb-8">
  <SaludWidget />
</div>

{/* Plants Grid - Grid existente */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Tarjetas de plantas */}
</div>
```

### **Import**
```tsx
import { SaludWidget } from "@/components/dashboard/SaludWidget"
```

---

## 🎯 Interacciones

### **Navegación**
- **Click en planta crítica** → `/plant/{id}`
- **Click en análisis reciente** → `/plant/{id}`
- **Botón "Agregar Primera Planta"** → `/identificar`
- **Botón "Analizar Plantas"** → `/plant/{id}`

### **Refresh**
- Botón de refresh (🔄) en header
- Ejecuta `cargarDatosSalud()` nuevamente
- Actualiza todas las estadísticas

---

## 📈 Performance

### **Optimizaciones**
1. **Promise.all** para cargar stats de múltiples plantas en paralelo
2. **Límite de 10 plantas** para historial (evita sobrecarga)
3. **Top 5 análisis** solamente (no cargar todo el historial)
4. **Try-catch por planta** (una falla no bloquea otras)

### **Tiempos Estimados**
- **5 plantas**: ~2-3 segundos
- **10 plantas**: ~3-5 segundos
- **20+ plantas**: ~5-8 segundos

### **Estrategia de Carga**
```typescript
const statsPromises = plantas.plantas.map(async (planta) => {
  try {
    const stats = await saludService.obtenerEstadisticas(planta.id)
    return { planta, stats }
  } catch (err) {
    return { planta, stats: null }  // No bloquear por error
  }
})
```

---

## 🐛 Manejo de Errores

### **Errores Capturados**
1. **Error al obtener plantas** → Empty state "Sin plantas"
2. **Error al obtener stats de una planta** → Ignorar esa planta, continuar
3. **Error al obtener historial** → Array vacío, continuar
4. **Error general** → Mostrar error state con botón reintentar

### **Console Logs**
```typescript
console.error('Error al cargar datos de salud:', err)
```
- Útil para debugging
- No expuesto al usuario final

---

## 🧪 Testing Recomendado

### **Unit Tests**
```typescript
describe('SaludWidget', () => {
  it('debe mostrar loading state inicialmente', () => {
    render(<SaludWidget />)
    expect(screen.getByText(/Cargando/i)).toBeInTheDocument()
  })

  it('debe mostrar empty state sin plantas', async () => {
    mockDashboardService.obtenerPlantas.mockResolvedValue({ plantas: [] })
    render(<SaludWidget />)
    await waitFor(() => {
      expect(screen.getByText(/No hay plantas/i)).toBeInTheDocument()
    })
  })

  it('debe mostrar alertas críticas', async () => {
    // Mock plantas con estado crítico
    render(<SaludWidget />)
    await waitFor(() => {
      expect(screen.getByText(/plantas? críticas?/i)).toBeInTheDocument()
    })
  })

  it('debe navegar a planta al hacer click', async () => {
    const push = jest.fn()
    mockRouter.push = push
    render(<SaludWidget />)
    // Click en planta
    fireEvent.click(screen.getByText(/Mi Potus/i))
    expect(push).toHaveBeenCalledWith('/plant/123')
  })
})
```

---

## 📦 Archivos

### **Componente Principal**
- `frontend/components/dashboard/SaludWidget.tsx` (430 líneas)

### **Documentación**
- `frontend/components/dashboard/README_DASHBOARD_WIDGET.md` (este archivo)

### **Dependencias**
- `frontend/models/salud.ts` (tipos)
- `frontend/lib/salud.service.ts` (API calls)
- `frontend/lib/dashboard.service.ts` (plantas)
- `@/components/ui/*` (shadcn/ui)

---

## 📊 Estadísticas del Código

| Métrica | Valor |
|---------|-------|
| **Líneas totales** | ~430 |
| **Interfaces** | 3 (SaludJardinStats, PlantaCritica, SaludWidgetProps) |
| **Estados** | 5 (estadisticas, ultimosAnalisis, plantasCriticas, cargando, error) |
| **Funciones** | 3 (cargarDatosSalud, navegarAPlanta, obtenerIconoTendencia) |
| **Estados UI** | 5 (loading, error, empty sin plantas, empty sin análisis, success) |
| **Iconos** | 9 (Activity, AlertTriangle, TrendingUp, Leaf, RefreshCw, etc.) |
| **Colors** | 5 (green, yellow, red, blue, gray) |

---

## 🎓 Lecciones Aprendidas

1. **Promise.all para paralelismo**: Cargar stats de múltiples plantas simultáneamente reduce tiempo de carga
2. **Try-catch por item**: No dejar que un error bloquee toda la carga
3. **Empty states claros**: Diferenciar entre "sin plantas" y "sin análisis"
4. **Alertas visuales**: Banner rojo para críticas llama la atención inmediatamente
5. **Click-through navigation**: Facilitar acceso rápido a detalles desde el widget

---

## 🚀 Resultado Final

✅ **Widget completamente funcional** integrado en dashboard

✅ **Resumen visual claro** de la salud del jardín

✅ **Alertas críticas prominentes** para acción inmediata

✅ **Navegación intuitiva** a plant details

✅ **Estados de error/loading/empty** bien manejados

✅ **Performance optimizado** con carga paralela

✅ **Documentación completa** para mantenimiento

---

**Fecha de implementación**: Noviembre 8, 2025  
**Sprint**: Feature - Health Check AI Extensions  
**Desarrollador**: GitHub Copilot + Human Review  
**Estado**: ✅ Completado y Documentado
