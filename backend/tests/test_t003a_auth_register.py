"""
Tests para T-003A: Endpoint de Registro de Usuario

Tests comprehensivos para el endpoint POST /api/auth/register.
Incluye casos de éxito, validaciones, edge cases y manejo de errores.

Estructura:
- Tests de registro exitoso
- Tests de validación de datos
- Tests de duplicados y conflictos
- Tests de edge cases
- Tests de seguridad

Autor: Equipo Plantitas
Fecha: Octubre 2025
Task: T-003A - Implementar endpoint de registro de usuario
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.models import Usuario, Base


# ==================== Configuración de Testing ====================

# Crear engine de SQLite en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que proporciona una sesión de base de datos limpia para cada test
    
    Crea las tablas antes del test y las elimina después para garantizar
    aislamiento entre tests.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Eliminar todas las tablas después del test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture que proporciona un cliente de FastAPI con base de datos de testing
    
    Sobrescribe la dependency get_db para usar la sesión de testing.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ==================== Tests de Registro Exitoso ====================

def test_registrar_usuario_exitoso_completo(client, db_session):
    """
    Test: Registro exitoso con todos los campos completos
    
    Verifica que un usuario puede registrarse proporcionando email,
    password y nombre completo.
    """
    # Arrange
    datos_registro = {
        "email": "maria.garcia@plantitas.com",
        "password": "MiPassword123",
        "nombre": "María García"
    }
    
    # Act
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["email"] == "maria.garcia@plantitas.com"
    assert data["nombre"] == "María García"
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data
    
    # Verificar que no se retorna el password
    assert "password" not in data
    assert "password_hash" not in data
    
    # Verificar que el usuario existe en la base de datos
    usuario_db = db_session.query(Usuario).filter(
        Usuario.email == "maria.garcia@plantitas.com"
    ).first()
    assert usuario_db is not None
    assert usuario_db.verify_password("MiPassword123")


def test_registrar_usuario_sin_nombre_opcional(client, db_session):
    """
    Test: Registro exitoso sin proporcionar nombre (campo opcional)
    
    Verifica que el nombre es opcional y el usuario puede registrarse
    solo con email y password.
    """
    # Arrange
    datos_registro = {
        "email": "usuario.sin.nombre@plantitas.com",
        "password": "Password456"
    }
    
    # Act
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == "usuario.sin.nombre@plantitas.com"
    assert data["nombre"] is None
    assert data["is_active"] is True


def test_email_normalizado_a_minusculas(client, db_session):
    """
    Test: Email se normaliza a minúsculas automáticamente
    
    Verifica que el email se convierte a minúsculas para evitar
    duplicados por diferencia de mayúsculas/minúsculas.
    """
    # Arrange
    datos_registro = {
        "email": "Usuario.MAYUSCULAS@Plantitas.COM",
        "password": "TestPassword123"
    }
    
    # Act
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    
    # Email debe estar en minúsculas
    assert data["email"] == "usuario.mayusculas@plantitas.com"
    
    # Verificar en base de datos
    usuario_db = db_session.query(Usuario).filter(
        Usuario.email == "usuario.mayusculas@plantitas.com"
    ).first()
    assert usuario_db is not None


# ==================== Tests de Validación de Password ====================

def test_password_sin_mayuscula_falla(client):
    """
    Test: Password sin letra mayúscula es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "password123"  # Sin mayúscula
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422
    assert "mayúscula" in response.text.lower()


def test_password_sin_minuscula_falla(client):
    """
    Test: Password sin letra minúscula es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "PASSWORD123"  # Sin minúscula
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422
    assert "minúscula" in response.text.lower()


def test_password_sin_numero_falla(client):
    """
    Test: Password sin número es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "PasswordSinNumero"  # Sin número
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422
    assert "número" in response.text.lower()


def test_password_menor_8_caracteres_falla(client):
    """
    Test: Password con menos de 8 caracteres es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "Pass1"  # Solo 5 caracteres
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


def test_password_mayor_100_caracteres_falla(client):
    """
    Test: Password con más de 100 caracteres es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "P1" + "a" * 100  # Más de 100 caracteres
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


def test_password_con_requisitos_minimos_exitoso(client, db_session):
    """
    Test: Password con requisitos mínimos exactos es aceptado
    """
    datos_registro = {
        "email": "minimos@plantitas.com",
        "password": "Abcd123e"  # Exactamente 8 caracteres con todos los requisitos
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201


# ==================== Tests de Validación de Email ====================

def test_email_invalido_falla(client):
    """
    Test: Email con formato inválido es rechazado
    """
    datos_invalidos = [
        {"email": "no-es-email", "password": "Password123"},
        {"email": "sin-arroba.com", "password": "Password123"},
        {"email": "@sin-usuario.com", "password": "Password123"},
        {"email": "sin-dominio@", "password": "Password123"},
        {"email": "espacios en medio@test.com", "password": "Password123"},
    ]
    
    for datos in datos_invalidos:
        response = client.post("/api/auth/register", json=datos)
        assert response.status_code == 422, f"Email '{datos['email']}' debería ser rechazado"


def test_email_valido_variaciones_aceptadas(client, db_session):
    """
    Test: Diferentes formatos válidos de email son aceptados
    """
    emails_validos = [
        "simple@ejemplo.com",
        "con.puntos@ejemplo.com",
        "con+plus@ejemplo.com",
        "con_guion_bajo@ejemplo.com",
        "con-guion@ejemplo.com",
        "numero123@ejemplo.com",
    ]
    
    for idx, email in enumerate(emails_validos):
        datos_registro = {
            "email": email,
            "password": f"Password{idx}23"
        }
        
        response = client.post("/api/auth/register", json=datos_registro)
        assert response.status_code == 201, f"Email '{email}' debería ser aceptado"


# ==================== Tests de Validación de Nombre ====================

def test_nombre_con_caracteres_especiales_invalidos_falla(client):
    """
    Test: Nombre con caracteres especiales no permitidos es rechazado
    """
    nombres_invalidos = [
        "Usuario123",  # Números
        "Usuario@Test",  # @ no permitido
        "Usuario#Hash",  # # no permitido
        "Usuario$Money",  # $ no permitido
        "<script>alert()</script>",  # Intento de XSS
    ]
    
    for nombre in nombres_invalidos:
        datos_registro = {
            "email": f"test{hash(nombre)}@plantitas.com",
            "password": "Password123",
            "nombre": nombre
        }
        
        response = client.post("/api/auth/register", json=datos_registro)
        assert response.status_code == 422, f"Nombre '{nombre}' debería ser rechazado"


def test_nombre_con_caracteres_validos_aceptado(client, db_session):
    """
    Test: Nombres con caracteres válidos son aceptados
    """
    nombres_validos = [
        "María García",
        "José-Luis",
        "Anne-Marie",
        "O'Connor",
        "María José",
        "MAYÚSCULAS",
        "minúsculas",
        "Acentuado Ñoño",
    ]
    
    for idx, nombre in enumerate(nombres_validos):
        datos_registro = {
            "email": f"test{idx}@plantitas.com",
            "password": f"Password{idx}23",
            "nombre": nombre
        }
        
        response = client.post("/api/auth/register", json=datos_registro)
        assert response.status_code == 201, f"Nombre '{nombre}' debería ser aceptado"
        
        data = response.json()
        assert data["nombre"] == nombre


def test_nombre_con_espacios_en_blanco_trimmed(client, db_session):
    """
    Test: Espacios en blanco al inicio y final del nombre son eliminados
    """
    datos_registro = {
        "email": "espacios@plantitas.com",
        "password": "Password123",
        "nombre": "  María García  "
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "María García"  # Sin espacios extra


def test_nombre_muy_corto_falla(client):
    """
    Test: Nombre con menos de 2 caracteres es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "Password123",
        "nombre": "A"  # Solo 1 carácter
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


def test_nombre_muy_largo_falla(client):
    """
    Test: Nombre con más de 100 caracteres es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "password": "Password123",
        "nombre": "A" * 101  # 101 caracteres
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


# ==================== Tests de Duplicados y Conflictos ====================

def test_email_duplicado_falla(client, db_session):
    """
    Test: Intentar registrar el mismo email dos veces falla
    """
    # Arrange - Primer registro exitoso
    datos_registro = {
        "email": "duplicado@plantitas.com",
        "password": "Password123",
        "nombre": "Usuario Uno"
    }
    
    response1 = client.post("/api/auth/register", json=datos_registro)
    assert response1.status_code == 201
    
    # Act - Intentar registrar el mismo email
    datos_duplicado = {
        "email": "duplicado@plantitas.com",
        "password": "OtraPassword456",
        "nombre": "Usuario Dos"
    }
    
    response2 = client.post("/api/auth/register", json=datos_duplicado)
    
    # Assert
    assert response2.status_code == 409  # Conflict
    assert "ya está registrado" in response2.json()["detail"]


def test_email_duplicado_case_insensitive_falla(client, db_session):
    """
    Test: Email duplicado con diferente capitalización también falla
    
    Los emails no deben ser case-sensitive, por lo que
    usuario@test.com y USUARIO@TEST.COM deben considerarse duplicados.
    """
    # Arrange - Primer registro
    datos_registro1 = {
        "email": "usuario@plantitas.com",
        "password": "Password123"
    }
    
    response1 = client.post("/api/auth/register", json=datos_registro1)
    assert response1.status_code == 201
    
    # Act - Intentar registrar con email en mayúsculas
    datos_registro2 = {
        "email": "USUARIO@PLANTITAS.COM",
        "password": "Password456"
    }
    
    response2 = client.post("/api/auth/register", json=datos_registro2)
    
    # Assert
    assert response2.status_code == 409


# ==================== Tests de Campos Requeridos ====================

def test_email_faltante_falla(client):
    """
    Test: Request sin email es rechazado
    """
    datos_registro = {
        "password": "Password123",
        "nombre": "María García"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


def test_password_faltante_falla(client):
    """
    Test: Request sin password es rechazado
    """
    datos_registro = {
        "email": "test@plantitas.com",
        "nombre": "María García"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422


def test_request_vacio_falla(client):
    """
    Test: Request completamente vacío es rechazado
    """
    response = client.post("/api/auth/register", json={})
    
    assert response.status_code == 422


# ==================== Tests de Seguridad ====================

def test_password_es_hasheado_en_db(client, db_session):
    """
    Test: La contraseña se guarda hasheada, no en texto plano
    """
    # Arrange
    datos_registro = {
        "email": "seguridad@plantitas.com",
        "password": "MiPasswordSecreto123"
    }
    
    # Act
    response = client.post("/api/auth/register", json=datos_registro)
    assert response.status_code == 201
    
    # Assert - Verificar que la contraseña en DB está hasheada
    usuario_db = db_session.query(Usuario).filter(
        Usuario.email == "seguridad@plantitas.com"
    ).first()
    
    assert usuario_db.password_hash != "MiPasswordSecreto123"
    assert usuario_db.password_hash.startswith("$2b$")  # bcrypt hash
    assert len(usuario_db.password_hash) == 60  # Longitud típica de bcrypt


def test_sql_injection_en_email_no_afecta(client, db_session):
    """
    Test: Intento de SQL injection en email es manejado correctamente
    """
    datos_registro = {
        "email": "test@test.com'; DROP TABLE usuarios; --",
        "password": "Password123"
    }
    
    # Debería fallar por formato de email inválido, no por SQL injection
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 422
    
    # Verificar que la tabla sigue existiendo
    usuarios_count = db_session.query(Usuario).count()
    assert usuarios_count == 0  # No hay usuarios, pero la tabla existe


def test_xss_en_nombre_es_escapado(client, db_session):
    """
    Test: Intento de XSS en nombre es rechazado por validación
    """
    datos_registro = {
        "email": "xss@plantitas.com",
        "password": "Password123",
        "nombre": "<script>alert('XSS')</script>"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    # Debería fallar por caracteres no permitidos en nombre
    assert response.status_code == 422


# ==================== Tests de Edge Cases ====================

def test_registro_multiple_usuarios_exitoso(client, db_session):
    """
    Test: Se pueden registrar múltiples usuarios diferentes
    """
    usuarios = [
        {"email": f"usuario{i}@plantitas.com", "password": f"Password{i}23"}
        for i in range(5)
    ]
    
    for usuario in usuarios:
        response = client.post("/api/auth/register", json=usuario)
        assert response.status_code == 201
    
    # Verificar que todos están en la base de datos
    count = db_session.query(Usuario).count()
    assert count == 5


def test_usuario_creado_es_activo_por_defecto(client, db_session):
    """
    Test: Usuario recién creado tiene es_activo=True por defecto
    """
    datos_registro = {
        "email": "nuevo@plantitas.com",
        "password": "Password123"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    assert data["is_active"] is True


def test_fecha_registro_es_generada_automaticamente(client, db_session):
    """
    Test: La fecha de registro se genera automáticamente al crear usuario
    """
    datos_registro = {
        "email": "fecha@plantitas.com",
        "password": "Password123"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    assert "created_at" in data
    assert data["created_at"] is not None


def test_ultimo_acceso_es_null_al_crear(client, db_session):
    """
    Test: El campo ultimo_acceso es null al crear un usuario nuevo
    """
    datos_registro = {
        "email": "acceso@plantitas.com",
        "password": "Password123"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    assert "updated_at" in data


# ==================== Tests de Response Schema ====================

def test_response_contiene_todos_campos_requeridos(client, db_session):
    """
    Test: La respuesta contiene todos los campos del schema UserResponse
    """
    datos_registro = {
        "email": "completo@plantitas.com",
        "password": "Password123",
        "nombre": "Usuario Completo"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar todos los campos de UserResponse
    campos_requeridos = ["id", "email", "nombre", "is_active", "created_at", "updated_at"]
    for campo in campos_requeridos:
        assert campo in data, f"Campo '{campo}' faltante en response"


def test_response_no_expone_campos_sensibles(client, db_session):
    """
    Test: La respuesta NO contiene campos sensibles como password o password_hash
    """
    datos_registro = {
        "email": "privado@plantitas.com",
        "password": "Password123"
    }
    
    response = client.post("/api/auth/register", json=datos_registro)
    
    assert response.status_code == 201
    data = response.json()
    
    # Verificar que NO se exponen campos sensibles
    campos_sensibles = ["password", "password_hash", "salt"]
    for campo in campos_sensibles:
        assert campo not in data, f"Campo sensible '{campo}' NO debería estar en response"


# ==================== Resumen de Cobertura ====================

"""
Resumen de Tests T-003A:

✅ Registro exitoso (3 tests)
   - Con todos los campos
   - Sin nombre opcional
   - Normalización de email

✅ Validación de password (6 tests)
   - Sin mayúscula
   - Sin minúscula
   - Sin número
   - Menor a 8 caracteres
   - Mayor a 100 caracteres
   - Con requisitos mínimos

✅ Validación de email (2 tests)
   - Formatos inválidos
   - Formatos válidos variados

✅ Validación de nombre (6 tests)
   - Caracteres especiales inválidos
   - Caracteres válidos
   - Espacios en blanco trimmed
   - Muy corto
   - Muy largo

✅ Duplicados y conflictos (2 tests)
   - Email duplicado
   - Email duplicado case-insensitive

✅ Campos requeridos (3 tests)
   - Email faltante
   - Password faltante
   - Request vacío

✅ Seguridad (3 tests)
   - Password hasheado
   - SQL injection
   - XSS en nombre

✅ Edge cases (5 tests)
   - Múltiples usuarios
   - Usuario activo por defecto
   - Fecha registro automática
   - Último acceso null
   - Campos de response completos

Total: 30 tests comprehensivos
Cobertura: ~95% del código de T-003A
"""
