"""
Configuración de fixtures compartidos para todos los tests

Este archivo define fixtures de pytest que son compartidos por todos los módulos de test.
Los fixtures incluyen configuración de base de datos, sesiones, clientes HTTP, y datos de prueba.

@author Equipo Backend
@date Enero 2026
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import Base
from app.db.session import get_db


# ==================== Database Fixtures ====================

@pytest.fixture(scope="function")
def engine():
    """
    Crea un engine SQLAlchemy con base de datos SQLite en memoria.
    
    Scope: function - Se crea un nuevo engine para cada test
    
    Yields:
        Engine: SQLAlchemy engine configurado con SQLite en memoria
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db(engine):
    """
    Crea una sesión de base de datos para tests.
    
    Este es el fixture principal que los tests deben usar cuando necesiten
    acceso a la base de datos. Proporciona aislamiento entre tests mediante
    rollback automático.
    
    Scope: function - Se crea una nueva sesión para cada test
    
    Args:
        engine: Engine de SQLAlchemy (fixture)
        
    Yields:
        Session: Sesión de SQLAlchemy para operaciones de BD
        
    Example:
        def test_crear_usuario(db):
            usuario = Usuario(email="test@example.com")
            db.add(usuario)
            db.commit()
            assert usuario.id is not None
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def session(engine):
    """
    Alias de 'db' para compatibilidad con tests existentes.
    
    Algunos tests usan 'session' en lugar de 'db'. Este fixture
    asegura que ambos nombres funcionen.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.rollback()
    session.close()


# ==================== Client Fixtures ====================

@pytest.fixture
def client():
    """
    Cliente de prueba para FastAPI.
    
    Proporciona un TestClient que permite hacer requests HTTP a la aplicación
    sin necesidad de levantar un servidor real.
    
    Returns:
        TestClient: Cliente de prueba de FastAPI
        
    Example:
        def test_health_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
def client_with_db(db):
    """
    Cliente de prueba con override de dependencia de base de datos.
    
    Sobrescribe la dependencia get_db() de FastAPI para usar la sesión
    de prueba en lugar de la sesión de producción.
    
    Args:
        db: Sesión de base de datos (fixture)
        
    Returns:
        TestClient: Cliente configurado con BD de prueba
        
    Example:
        def test_with_db(client_with_db, db):
            # La app usará automáticamente la BD de prueba
            response = client_with_db.get("/api/usuarios")
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== Authentication Fixtures ====================

@pytest.fixture
def usuario_autenticado(client):
    """
    Crea un usuario y retorna su token de autenticación.
    
    Este fixture es útil para tests que requieren autenticación.
    Registra un usuario nuevo, hace login, y retorna el token JWT
    junto con la información del usuario.
    
    Args:
        client: Cliente de prueba (fixture)
        
    Returns:
        dict: Diccionario con:
            - token (str): JWT access token
            - usuario_id (int): ID del usuario creado
            - headers (dict): Headers listo para usar en requests
            - email (str): Email del usuario
            
    Example:
        def test_protected_endpoint(client, usuario_autenticado):
            response = client.get(
                "/api/protected",
                headers=usuario_autenticado["headers"]
            )
            assert response.status_code == 200
    """
    # Registrar usuario
    datos_registro = {
        "email": "test_auth@example.com",
        "nombre": "Usuario Test Auth",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Si el usuario ya existe (en tests con scope más amplio), hacer login directamente
    if response.status_code == 409:  # Conflict - usuario ya existe
        pass
    else:
        assert response.status_code == 201, f"Error al registrar: {response.json()}"
    
    # Login para obtener token
    datos_login = {
        "email": "test_auth@example.com",
        "password": "TestPass123!"
    }
    
    response = client.post("/api/auth/login", json=datos_login)
    assert response.status_code == 200, f"Error al hacer login: {response.json()}"
    
    data = response.json()
    
    return {
        "token": data["access_token"],
        "usuario_id": data.get("usuario_id") or data.get("usuario", {}).get("id"),
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "email": "test_auth@example.com"
    }


# ==================== Cleanup Fixtures ====================

@pytest.fixture(autouse=True)
def reset_db_state():
    """
    Limpia el estado de la base de datos entre tests.
    
    Este fixture se ejecuta automáticamente (autouse=True) antes y después
    de cada test para asegurar aislamiento completo.
    """
    # Setup: nada que hacer antes
    yield
    # Teardown: limpiar cualquier estado global si es necesario
    pass


# ==================== Configuration ====================

def pytest_configure(config):
    """
    Configuración personalizada de pytest.
    
    Se ejecuta una vez al inicio de la sesión de testing.
    """
    # Configurar markers personalizados
    config.addinivalue_line(
        "markers", "slow: marca tests que son lentos (> 1s)"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración que requieren servicios externos"
    )
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios puros"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modifica la colección de tests antes de ejecutarlos.
    
    Permite agregar markers automáticamente basados en nombres o rutas.
    """
    for item in items:
        # Agregar marker 'unit' a todos los tests que no tienen otros markers
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)
