# 🧪 Estrategia de Testing con PostgreSQL en Docker

## 📋 Resumen

**CAMBIO IMPORTANTE:** Los tests ahora se ejecutan en **Docker con PostgreSQL** en lugar de SQLite en memoria.

### ✅ Ventajas de PostgreSQL para Tests

1. **Paridad con Producción**: Misma base de datos que en Docker/producción
2. **Tests Más Confiables**: Detectan problemas reales de PostgreSQL
3. **Sin Conversiones Manuales**: JSON types nativos
4. **Comportamiento Idéntico**: CASCADE, RETURNING, tipos de datos, etc.
5. **CI/CD Robusto**: Tests idénticos en todos los ambientes

### ❌ Problemas de SQLite (eliminados)

- ~~Diferencias de comportamiento con PostgreSQL~~
- ~~Conversión manual de JSON a strings~~
- ~~Tests pasan localmente pero fallan en producción~~
- ~~Bugs no detectados hasta despliegue~~

---

## 🚀 Cómo Ejecutar Tests

### **Opción 1: Script PowerShell (Windows) - RECOMENDADO** ⭐

```powershell
# Navegar al directorio de tests
cd backend\tests

# Ejecutar todos los tests
.\docker_test_runner.ps1

# Ejecutar solo tests de salud
.\docker_test_runner.ps1 health

# Ejecutar con reporte de cobertura
.\docker_test_runner.ps1 coverage
```

### **Opción 2: Script Bash (Linux/Mac)**

```bash
# Navegar al directorio de tests
cd backend/tests

# Hacer script ejecutable (solo primera vez)
chmod +x docker_test_runner.sh

# Ejecutar todos los tests
./docker_test_runner.sh

# Ejecutar solo tests de salud
./docker_test_runner.sh health

# Ejecutar con reporte de cobertura
./docker_test_runner.sh coverage
```

### **Opción 3: Docker Compose Manual**

```bash
# 1. Levantar PostgreSQL de test
docker-compose -f docker-compose.test.yml up -d db_test

# 2. Esperar a que esté listo
sleep 5

# 3. Ejecutar migraciones
docker-compose -f docker-compose.test.yml run --rm backend_test alembic upgrade head

# 4. Ejecutar tests
docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -v

# 5. Limpiar
docker-compose -f docker-compose.test.yml down -v
```

---

## 🏗️ Arquitectura de Testing

### **Servicios Docker**

```yaml
db_test:
  - PostgreSQL 15 Alpine
  - Base de datos: plantitas_test
  - Usuario: test_user
  - Puerto: 5433 (no conflictúa con desarrollo)
  - Datos en tmpfs (RAM) para velocidad

backend_test:
  - FastAPI con pytest
  - Conectado a db_test
  - Variables de entorno de testing
  - Volúmenes montados para hot-reload
```

### **Variables de Entorno de Test**

```bash
DATABASE_URL=postgresql://test_user:test_password@db_test:5432/plantitas_test
ENVIRONMENT=testing
DEBUG=false
SECRET_KEY=test_secret_key_for_testing_only
```

---

## 📂 Estructura de Archivos

```
backend/
├── tests/
│   ├── conftest.py                    # ✅ Actualizado para PostgreSQL
│   ├── docker_test_runner.ps1         # 🆕 Script Windows
│   ├── docker_test_runner.sh          # 🆕 Script Linux/Mac
│   ├── test_health_endpoints.py       # Tests de salud (Task 7)
│   └── test_*.py                      # Otros tests
│
├── pytest.ini                         # Configuración pytest
└── requirements.txt                   # Dependencias (incluye pytest, pytest-cov)

docker-compose.test.yml                # 🆕 Config Docker para tests
```

---

## 🔧 Configuración de conftest.py

### **Antes (SQLite):**
```python
engine = create_engine("sqlite:///:memory:", echo=False)
```

### **Ahora (PostgreSQL):**
```python
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://test_user:test_password@localhost:5433/plantitas_test"
)
engine = create_engine(database_url, echo=False)
```

---

## 🧪 Escribir Tests

### **Fixtures Disponibles**

```python
def test_mi_funcion(client_with_db, db, usuario_autenticado):
    """
    client_with_db: TestClient con BD de prueba
    db: Sesión de PostgreSQL
    usuario_autenticado: Usuario con token JWT
    """
    # Tu código de test aquí
    pass
```

### **Ejemplo: Test de Endpoint**

```python
import pytest
from fastapi import status

@pytest.mark.integration
def test_crear_planta(client_with_db, db, usuario_autenticado):
    """Test crear planta con PostgreSQL"""
    
    # Datos de prueba
    planta_data = {
        "nombre_personal": "Mi Potus",
        "ubicacion": "Sala"
    }
    
    # Request con autenticación
    response = client_with_db.post(
        "/api/plantas",
        json=planta_data,
        headers=usuario_autenticado["headers"]
    )
    
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nombre_personal"] == "Mi Potus"
    
    # Verificar en BD (PostgreSQL)
    from app.db.models import Planta
    planta = db.query(Planta).filter_by(
        id=data["id"]
    ).first()
    assert planta is not None
    assert planta.nombre_personal == "Mi Potus"
```

### **Ejemplo: Test con JSON Types**

```python
import json

def test_analisis_salud_json(db, planta_test):
    """Test que JSON types funcionan nativamente en PostgreSQL"""
    from app.db.models import AnalisisSalud
    
    # Crear análisis con JSON nativo (sin json.dumps)
    analisis = AnalisisSalud(
        planta_id=planta_test.id,
        estado_salud="saludable",
        confianza=85.5,
        problemas_detectados=[  # ✅ Lista Python directa
            {
                "nombre": "Amarillamiento",
                "severidad": "baja"
            }
        ],
        recomendaciones=[  # ✅ Lista Python directa
            {
                "titulo": "Regar más",
                "prioridad": "media"
            }
        ]
    )
    
    db.add(analisis)
    db.commit()
    db.refresh(analisis)
    
    # PostgreSQL maneja JSON nativamente
    assert isinstance(analisis.problemas_detectados, list)
    assert analisis.problemas_detectados[0]["nombre"] == "Amarillamiento"
```

---

## 📊 Cobertura de Tests

### **Generar Reporte de Cobertura**

```powershell
# Windows
.\docker_test_runner.ps1 coverage

# Linux/Mac
./docker_test_runner.sh coverage
```

### **Ver Reporte HTML**

```bash
# El reporte se genera en backend/htmlcov/
# Abrir en navegador:
start backend/htmlcov/index.html  # Windows
open backend/htmlcov/index.html   # Mac
xdg-open backend/htmlcov/index.html  # Linux
```

---

## 🎯 Markers de Pytest

```python
@pytest.mark.unit           # Tests unitarios
@pytest.mark.integration    # Tests de integración
@pytest.mark.database       # Tests que usan BD
@pytest.mark.api            # Tests de API endpoints
@pytest.mark.auth           # Tests de autenticación
@pytest.mark.slow           # Tests lentos (>1s)
```

### **Ejecutar solo tests específicos:**

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de API
pytest -m api

# Excluir tests lentos
pytest -m "not slow"

# Solo tests de salud
pytest tests/test_health_endpoints.py
```

---

## 🔍 Debugging

### **Ver logs detallados:**

```bash
docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -vv
```

### **Detener en primer error:**

```bash
docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -x
```

### **Ver output de prints:**

```bash
docker-compose -f docker-compose.test.yml run --rm backend_test pytest tests/ -s
```

---

## ⚡ Performance

### **Optimizaciones Aplicadas:**

1. **tmpfs para PostgreSQL**: Datos en RAM en lugar de disco
2. **Connection pooling**: Reuso de conexiones
3. **Cleanup automático**: Limpieza rápida entre tests
4. **Parallelización** (opcional): `pytest -n auto` con pytest-xdist

### **Tiempos Esperados:**

- Test unitario: < 0.1s
- Test de integración: < 0.5s
- Test con BD: < 1s
- Suite completa (50 tests): < 30s

---

## 🚨 Troubleshooting

### **Problema: Puerto 5433 en uso**

```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr 5433  # Windows
lsof -i :5433                # Linux/Mac

# Cambiar puerto en docker-compose.test.yml
ports:
  - "5434:5432"  # Usar 5434 en lugar de 5433
```

### **Problema: PostgreSQL no inicia**

```bash
# Ver logs
docker-compose -f docker-compose.test.yml logs db_test

# Reiniciar servicios
docker-compose -f docker-compose.test.yml restart db_test
```

### **Problema: Tests fallan por timeout**

```bash
# Aumentar timeout en docker-compose.test.yml
environment:
  DB_CONNECTION_TIMEOUT: 60  # Aumentar a 60s
```

---

## 📝 Checklist para Task 7

- [x] Crear `docker-compose.test.yml`
- [x] Crear `docker_test_runner.ps1`
- [x] Crear `docker_test_runner.sh`
- [x] Actualizar `conftest.py` para PostgreSQL
- [ ] Simplificar `test_health_endpoints.py`
- [ ] Eliminar conversiones JSON manuales
- [ ] Corregir fixtures de Imagen
- [ ] Ejecutar tests en Docker
- [ ] Validar 23/23 tests pasando
- [ ] Generar reporte de cobertura >80%

---

## 🔗 Referencias

- [PostgreSQL in Docker](https://hub.docker.com/_/postgres)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/core/testing.html)

---

**Última actualización:** 8 de Noviembre, 2025  
**Autor:** Backend Team
