"""
Tests para T-001: Configuración FastAPI con estructura MVC

Este módulo contiene tests unitarios para verificar que la estructura
MVC del proyecto FastAPI está correctamente configurada según los
criterios de aceptación de T-001.

Tests incluidos:
- Verificación de estructura de carpetas
- Tests de configuración (core/config.py)
- Tests de endpoints básicos
- Tests de middleware CORS
- Tests de health check
"""

import pytest
import os
from pathlib import Path


# ==================== Tests de Estructura de Carpetas ====================

class TestEstructuraMVC:
    """Tests para verificar que la estructura de carpetas MVC está completa"""
    
    def test_carpeta_app_existe(self):
        """Verificar que la carpeta principal /app existe"""
        app_path = Path(__file__).parent.parent / "app"
        assert app_path.exists(), "La carpeta /app debe existir"
        assert app_path.is_dir(), "app debe ser un directorio"
    
    def test_carpeta_api_existe(self):
        """Verificar que la carpeta /api existe"""
        api_path = Path(__file__).parent.parent / "app" / "api"
        assert api_path.exists(), "La carpeta /api debe existir"
        assert (api_path / "__init__.py").exists(), "/api debe tener __init__.py"
    
    def test_carpeta_core_existe(self):
        """Verificar que la carpeta /core existe con config.py"""
        core_path = Path(__file__).parent.parent / "app" / "core"
        assert core_path.exists(), "La carpeta /core debe existir"
        assert (core_path / "__init__.py").exists(), "/core debe tener __init__.py"
        assert (core_path / "config.py").exists(), "/core debe tener config.py"
    
    def test_carpeta_db_existe(self):
        """Verificar que la carpeta /db existe"""
        db_path = Path(__file__).parent.parent / "app" / "db"
        assert db_path.exists(), "La carpeta /db debe existir"
        assert (db_path / "__init__.py").exists(), "/db debe tener __init__.py"
    
    def test_carpeta_schemas_existe(self):
        """Verificar que la carpeta /schemas existe"""
        schemas_path = Path(__file__).parent.parent / "app" / "schemas"
        assert schemas_path.exists(), "La carpeta /schemas debe existir"
        assert (schemas_path / "__init__.py").exists(), "/schemas debe tener __init__.py"
    
    def test_carpeta_services_existe(self):
        """Verificar que la carpeta /services existe"""
        services_path = Path(__file__).parent.parent / "app" / "services"
        assert services_path.exists(), "La carpeta /services debe existir"
        assert (services_path / "__init__.py").exists(), "/services debe tener __init__.py"
    
    def test_carpeta_utils_existe(self):
        """Verificar que la carpeta /utils existe"""
        utils_path = Path(__file__).parent.parent / "app" / "utils"
        assert utils_path.exists(), "La carpeta /utils debe existir"
        assert (utils_path / "__init__.py").exists(), "/utils debe tener __init__.py"
    
    def test_main_py_existe(self):
        """Verificar que main.py existe en /app"""
        main_path = Path(__file__).parent.parent / "app" / "main.py"
        assert main_path.exists(), "main.py debe existir en /app"


# ==================== Tests de Configuración ====================

class TestConfiguracion:
    """Tests para el módulo de configuración"""
    
    def test_importar_configuracion(self):
        """Verificar que se puede importar la configuración"""
        from app.core.config import obtener_configuracion, Configuracion
        
        config = obtener_configuracion()
        assert isinstance(config, Configuracion), "debe retornar instancia de Configuracion"
    
    def test_configuracion_tiene_atributos_requeridos(self):
        """Verificar que la configuración tiene todos los atributos requeridos"""
        from app.core.config import obtener_configuracion
        
        config = obtener_configuracion()
        
        # Atributos básicos
        assert hasattr(config, "nombre_app"), "debe tener nombre_app"
        assert hasattr(config, "version"), "debe tener version"
        assert hasattr(config, "descripcion"), "debe tener descripcion"
        assert hasattr(config, "debug"), "debe tener debug"
        assert hasattr(config, "entorno"), "debe tener entorno"
        
        # Atributos de base de datos
        assert hasattr(config, "url_base_datos"), "debe tener url_base_datos"
        assert hasattr(config, "db_pool_size"), "debe tener db_pool_size"
        
        # Atributos de seguridad
        assert hasattr(config, "jwt_secret_key"), "debe tener jwt_secret_key"
        assert hasattr(config, "jwt_algorithm"), "debe tener jwt_algorithm"
        assert hasattr(config, "jwt_expiracion_minutos"), "debe tener jwt_expiracion_minutos"
        
        # Atributos de CORS
        assert hasattr(config, "origenes_cors"), "debe tener origenes_cors"
        assert hasattr(config, "cors_allow_credentials"), "debe tener cors_allow_credentials"
    
    def test_configuracion_cors_es_lista(self):
        """Verificar que origenes_cors es una lista"""
        from app.core.config import obtener_configuracion
        
        config = obtener_configuracion()
        assert isinstance(config.origenes_cors, list), "origenes_cors debe ser una lista"
        assert len(config.origenes_cors) > 0, "origenes_cors no debe estar vacía"
    
    def test_configuracion_singleton(self):
        """Verificar que la configuración sigue patrón Singleton"""
        from app.core.config import obtener_configuracion
        
        config1 = obtener_configuracion()
        config2 = obtener_configuracion()
        
        assert config1 is config2, "obtener_configuracion() debe retornar la misma instancia"
    
    def test_valores_por_defecto(self):
        """Verificar valores por defecto de la configuración"""
        from app.core.config import obtener_configuracion
        
        config = obtener_configuracion()
        
        assert config.version == "0.1.0", "version por defecto debe ser 0.1.0"
        assert config.jwt_algorithm == "HS256", "algoritmo JWT debe ser HS256"
        assert config.host == "0.0.0.0", "host por defecto debe ser 0.0.0.0"
        assert config.puerto == 8000, "puerto por defecto debe ser 8000"


# ==================== Tests de Aplicación FastAPI ====================

class TestAplicacionFastAPI:
    """Tests para la aplicación FastAPI principal"""
    
    def test_crear_aplicacion(self):
        """Verificar que se puede crear la aplicación"""
        from app.main import crear_aplicacion
        
        app = crear_aplicacion()
        assert app is not None, "crear_aplicacion() debe retornar una instancia"
    
    def test_app_tiene_configuracion_correcta(self):
        """Verificar que la app tiene la configuración correcta"""
        from app.main import app
        from app.core.config import obtener_configuracion
        
        config = obtener_configuracion()
        
        assert app.title == config.nombre_app, "título debe coincidir con configuración"
        assert app.version == config.version, "versión debe coincidir con configuración"
    
    def test_middleware_cors_configurado(self):
        """Verificar que el middleware CORS está configurado"""
        from app.main import app
        
        # Verificar que hay middleware configurados
        assert len(app.user_middleware) > 0, "debe tener middleware configurados"
        
        # Buscar CORSMiddleware
        tiene_cors = any(
            "CORSMiddleware" in str(middleware) 
            for middleware in app.user_middleware
        )
        assert tiene_cors, "debe tener CORSMiddleware configurado"


# ==================== Tests de Endpoints ====================

class TestEndpoints:
    """Tests para los endpoints básicos de la aplicación"""
    
    @pytest.fixture
    def client(self):
        """Fixture que proporciona un cliente de prueba"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        return TestClient(app)
    
    def test_endpoint_raiz_retorna_200(self, client):
        """Verificar que el endpoint raíz retorna 200 OK"""
        response = client.get("/")
        assert response.status_code == 200, "endpoint raíz debe retornar 200"
    
    def test_endpoint_raiz_estructura(self, client):
        """Verificar la estructura de la respuesta del endpoint raíz"""
        response = client.get("/")
        data = response.json()
        
        assert "mensaje" in data, "debe tener campo mensaje"
        assert "version" in data, "debe tener campo version"
        assert "estado" in data, "debe tener campo estado"
        assert "timestamp" in data, "debe tener campo timestamp"
        assert "endpoints_disponibles" in data, "debe tener endpoints_disponibles"
    
    def test_endpoint_salud_retorna_200(self, client):
        """Verificar que el endpoint /salud retorna 200 OK"""
        response = client.get("/salud")
        assert response.status_code == 200, "/salud debe retornar 200"
    
    def test_endpoint_salud_estructura(self, client):
        """Verificar la estructura del health check"""
        response = client.get("/salud")
        data = response.json()
        
        assert "estado" in data, "debe tener campo estado"
        assert "servicio" in data, "debe tener campo servicio"
        assert "version" in data, "debe tener campo version"
        assert "componentes" in data, "debe tener campo componentes"
        assert data["estado"] == "saludable", "estado debe ser 'saludable'"
    
    def test_endpoint_salud_componentes(self, client):
        """Verificar que el health check incluye estado de componentes"""
        response = client.get("/salud")
        data = response.json()
        
        componentes = data.get("componentes", {})
        assert "api" in componentes, "debe incluir estado de api"
        assert "base_datos" in componentes, "debe incluir estado de base_datos"
        assert "almacenamiento" in componentes, "debe incluir estado de almacenamiento"
    
    def test_endpoint_info_retorna_200(self, client):
        """Verificar que /info retorna 200 OK"""
        response = client.get("/info")
        assert response.status_code == 200, "/info debe retornar 200"
    
    def test_endpoint_info_estructura(self, client):
        """Verificar la estructura de /info"""
        response = client.get("/info")
        data = response.json()
        
        assert "aplicacion" in data, "debe tener campo aplicacion"
        assert "sistema" in data, "debe tener campo sistema"
        assert "base_datos" in data, "debe tener campo base_datos"
        assert "seguridad" in data, "debe tener campo seguridad"
    
    def test_endpoint_metricas_retorna_200(self, client):
        """Verificar que /metricas retorna 200 OK"""
        response = client.get("/metricas")
        assert response.status_code == 200, "/metricas debe retornar 200"
    
    def test_endpoint_metricas_estructura(self, client):
        """Verificar la estructura de /metricas"""
        response = client.get("/metricas")
        data = response.json()
        
        assert "aplicacion" in data, "debe tener campo aplicacion"
        assert "version" in data, "debe tener campo version"
        assert "metricas" in data, "debe tener campo metricas"
    
    def test_cors_headers_presentes(self, client):
        """Verificar que las cabeceras CORS están presentes"""
        response = client.options("/", headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET"
        })
        
        # Verificar que la respuesta incluye cabeceras CORS
        assert "access-control-allow-origin" in response.headers, \
            "debe tener cabecera access-control-allow-origin"


# ==================== Tests de Documentación ====================

class TestDocumentacion:
    """Tests para verificar que la documentación está disponible"""
    
    @pytest.fixture
    def client(self):
        """Fixture que proporciona un cliente de prueba"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        return TestClient(app)
    
    def test_docs_swagger_disponible(self, client):
        """Verificar que Swagger UI está disponible en modo debug"""
        from app.core.config import obtener_configuracion
        config = obtener_configuracion()
        
        if config.debug:
            response = client.get("/docs")
            assert response.status_code == 200, "/docs debe estar disponible en debug"
    
    def test_openapi_json_disponible(self, client):
        """Verificar que el schema OpenAPI está disponible"""
        from app.core.config import obtener_configuracion
        config = obtener_configuracion()
        
        if config.debug:
            response = client.get("/openapi.json")
            assert response.status_code == 200, "/openapi.json debe estar disponible"


# ==================== Tests de Archivos de Configuración ====================

class TestArchivosConfiguracion:
    """Tests para verificar que los archivos de configuración existen"""
    
    def test_env_example_existe(self):
        """Verificar que .env.example existe"""
        env_example_path = Path(__file__).parent.parent / ".env.example"
        assert env_example_path.exists(), ".env.example debe existir"
    
    def test_requirements_txt_existe(self):
        """Verificar que requirements.txt existe"""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt debe existir"
    
    def test_pytest_ini_existe(self):
        """Verificar que pytest.ini existe"""
        pytest_ini_path = Path(__file__).parent.parent / "pytest.ini"
        assert pytest_ini_path.exists(), "pytest.ini debe existir"


# ==================== Marker para tests de T-001 ====================
pytestmark = pytest.mark.unit
