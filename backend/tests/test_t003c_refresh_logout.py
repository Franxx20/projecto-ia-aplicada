"""
Tests para T-003C: Implementar refresh token y logout

Tests comprehensivos para los endpoints de renovación de token JWT y logout.
Cubre happy path, casos de error, validaciones y seguridad.

Estructura:
- TestRefreshToken: Tests del endpoint POST /api/auth/refresh
- TestLogout: Tests del endpoint POST /api/auth/logout
- TestIntegracion: Tests de integración entre refresh y logout
- TestSeguridad: Tests de seguridad y edge cases
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.models import Usuario, Base
from app.utils.jwt import crear_token_acceso, crear_refresh_token, decodificar_token
from app.services.auth_service import limpiar_blacklist, agregar_token_a_blacklist
from app.core.config import obtener_configuracion


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


@pytest.fixture(autouse=True)
def limpiar_blacklist_antes_de_cada_test():
    """
    Limpiar la blacklist antes de cada test
    
    Esto asegura que cada test comience con un estado limpio
    y no haya interferencia entre tests.
    """
    limpiar_blacklist()
    yield
    limpiar_blacklist()


@pytest.fixture
def usuario_test(db_session):
    """
    Fixture: Usuario de prueba en base de datos
    
    Crea un usuario de prueba que puede ser usado en múltiples tests
    """
    usuario = Usuario(
        email="test@refresh.com",
        nombre="Usuario Test Refresh"
    )
    usuario.set_password("TestPassword123")
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
def token_valido(usuario_test):
    """
    Fixture: Token JWT válido para el usuario de prueba
    
    Returns:
        str: Token JWT válido con expiración de 30 minutos
    """
    config = obtener_configuracion()
    token_data = {
        "sub": usuario_test.email,
        "user_id": usuario_test.id,
        "nombre": usuario_test.nombre,
    }
    
    return crear_token_acceso(
        datos=token_data,
        expiracion_minutos=config.jwt_expiracion_minutos
    )


@pytest.fixture
def refresh_token_valido(usuario_test):
    """
    Fixture: Refresh token JWT válido para el usuario de prueba
    
    Returns:
        str: Refresh token JWT válido con expiración de 7 días
    """
    config = obtener_configuracion()
    token_data = {
        "sub": usuario_test.email,
        "user_id": usuario_test.id,
        "nombre": usuario_test.nombre,
    }
    
    return crear_refresh_token(
        datos=token_data,
        expiracion_dias=config.jwt_refresh_expiracion_dias
    )


# ==================== Tests de Refresh Token ====================

class TestRefreshToken:
    """Tests del endpoint POST /api/auth/refresh"""
    
    def test_refresh_token_happy_path(self, client, usuario_test, token_valido):
        """
        Test: Renovar token JWT exitosamente (Happy Path)
        
        Verifica que un token válido puede ser renovado y retorna:
        - access_token: Nuevo token JWT
        - token_type: "bearer"
        - expires_in: Tiempo de expiración en segundos (7 días)
        """
        # Arrange
        request_data = {
            "access_token": token_valido
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert "expires_in" in response_data
        
        assert response_data["token_type"] == "bearer"
        assert response_data["expires_in"] == 7 * 24 * 60 * 60  # 7 días en segundos
        
        # Verificar que el nuevo token es válido
        nuevo_token = response_data["access_token"]
        payload = decodificar_token(nuevo_token)
        assert payload is not None
        assert payload["sub"] == usuario_test.email
        assert payload["user_id"] == usuario_test.id
        assert payload["type"] == "refresh"  # Debe ser un refresh token
    
    def test_refresh_token_con_refresh_token_valido(self, client, usuario_test, refresh_token_valido):
        """
        Test: Renovar usando un refresh token existente
        
        Verifica que un refresh token también puede ser renovado
        """
        # Arrange
        request_data = {
            "access_token": refresh_token_valido
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert "access_token" in response_data
        
        # Verificar que el nuevo token es diferente del original
        assert response_data["access_token"] != refresh_token_valido
    
    def test_refresh_token_invalido(self, client):
        """
        Test: Renovar con token inválido retorna 401
        
        Verifica que un token mal formado o inválido retorna error
        """
        # Arrange
        request_data = {
            "access_token": "token_invalido_xyz123"
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
    
    def test_refresh_token_expirado(self, client, usuario_test):
        """
        Test: Renovar con token expirado retorna 401
        
        Verifica que un token expirado no puede ser renovado
        """
        # Arrange - Crear token expirado (expiró hace 1 minuto)
        token_data = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id,
            "nombre": usuario_test.nombre,
        }
        
        token_expirado = crear_token_acceso(
            datos=token_data,
            expiracion_minutos=-1  # Expirado
        )
        
        request_data = {
            "access_token": token_expirado
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expirado" in response.json()["detail"].lower()
    
    def test_refresh_token_sin_subject(self, client):
        """
        Test: Renovar token sin subject (email) retorna 401
        
        Verifica que un token sin el claim "sub" es rechazado
        """
        # Arrange - Crear token sin subject
        config = obtener_configuracion()
        token_data = {
            "user_id": 123,
            "nombre": "Test User"
            # Falta "sub"
        }
        
        token_sin_sub = jwt.encode(
            {
                **token_data,
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "iat": datetime.utcnow()
            },
            config.jwt_secret_key,
            algorithm=config.jwt_algorithm
        )
        
        request_data = {
            "access_token": token_sin_sub
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "subject" in response.json()["detail"].lower()
    
    def test_refresh_token_usuario_no_existe(self, client):
        """
        Test: Renovar token de usuario inexistente retorna 401
        
        Verifica que si el usuario del token no existe en la BD, retorna error
        """
        # Arrange - Crear token para usuario que no existe
        token_data = {
            "sub": "noexiste@test.com",
            "user_id": 99999,
            "nombre": "Usuario Inexistente"
        }
        
        token_usuario_inexistente = crear_token_acceso(datos=token_data)
        
        request_data = {
            "access_token": token_usuario_inexistente
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "no encontrado" in response.json()["detail"].lower()
    
    def test_refresh_token_usuario_desactivado(self, client, usuario_test, token_valido, db_session):
        """
        Test: Renovar token de usuario desactivado retorna 403
        
        Verifica que un usuario desactivado no puede renovar su token
        """
        # Arrange - Desactivar usuario
        usuario_test.desactivar()
        db_session.commit()
        
        request_data = {
            "access_token": token_valido
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "desactivada" in response.json()["detail"].lower()
    
    def test_refresh_token_en_blacklist(self, client, token_valido):
        """
        Test: Renovar token que está en blacklist retorna 401
        
        Verifica que un token invalidado por logout no puede ser renovado
        """
        # Arrange - Agregar token a blacklist
        agregar_token_a_blacklist(token_valido)
        
        request_data = {
            "access_token": token_valido
        }
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalidado" in response.json()["detail"].lower() or "blacklist" in response.json()["detail"].lower()
    
    def test_refresh_token_request_sin_token(self, client):
        """
        Test: Request sin access_token retorna 422
        
        Verifica que el campo access_token es requerido
        """
        # Arrange
        request_data = {}  # Sin access_token
        
        # Act
        response = client.post("/api/auth/refresh", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Tests de Logout ====================

class TestLogout:
    """Tests del endpoint POST /api/auth/logout"""
    
    def test_logout_happy_path(self, client, token_valido):
        """
        Test: Logout exitoso invalida el token (Happy Path)
        
        Verifica que el logout agrega el token a la blacklist
        y retorna un mensaje de confirmación
        """
        # Arrange
        request_data = {
            "access_token": token_valido
        }
        
        # Act
        response = client.post("/api/auth/logout", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert "message" in response_data
        assert "detail" in response_data
        assert "exitoso" in response_data["message"].lower()
        assert "invalidado" in response_data["detail"].lower()
    
    def test_logout_token_invalido(self):
        """
        Test: Logout con token inválido retorna 401
        
        Verifica que un token mal formado no puede ser invalidado
        """
        # Arrange
        request_data = {
            "access_token": "token_invalido_xyz123"
        }
        
        # Act
        response = client.post("/api/auth/logout", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
    
    def test_logout_token_expirado(self, client, usuario_test):
        """
        Test: Logout con token expirado retorna 401
        
        Verifica que un token expirado no puede ser invalidado
        """
        # Arrange - Crear token expirado
        token_data = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id,
            "nombre": usuario_test.nombre,
        }
        
        token_expirado = crear_token_acceso(
            datos=token_data,
            expiracion_minutos=-1  # Expirado
        )
        
        request_data = {
            "access_token": token_expirado
        }
        
        # Act
        response = client.post("/api/auth/logout", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expirado" in response.json()["detail"].lower()
    
    def test_logout_token_ya_invalidado(self, client, token_valido):
        """
        Test: Hacer logout dos veces con el mismo token retorna 401
        
        Verifica que un token ya invalidado no puede ser invalidado nuevamente
        """
        # Arrange - Hacer logout la primera vez
        request_data = {
            "access_token": token_valido
        }
        
        first_response = client.post("/api/auth/logout", json=request_data)
        assert first_response.status_code == status.HTTP_200_OK
        
        # Act - Intentar hacer logout nuevamente
        second_response = client.post("/api/auth/logout", json=request_data)
        
        # Assert
        assert second_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalidado" in second_response.json()["detail"].lower()
    
    def test_logout_request_sin_token(self):
        """
        Test: Request sin access_token retorna 422
        
        Verifica que el campo access_token es requerido
        """
        # Arrange
        request_data = {}  # Sin access_token
        
        # Act
        response = client.post("/api/auth/logout", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== Tests de Integración ====================

class TestIntegracion:
    """Tests de integración entre refresh token y logout"""
    
    def test_flujo_completo_login_refresh_logout(self, client, usuario_test):
        """
        Test: Flujo completo de login -> refresh -> logout
        
        Verifica el flujo completo de autenticación:
        1. Login exitoso
        2. Refresh token exitoso
        3. Logout exitoso
        4. No se puede usar el token después del logout
        """
        # 1. Login
        login_data = {
            "email": usuario_test.email,
            "password": "TestPassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token_original = login_response.json()["access_token"]
        
        # 2. Refresh token
        refresh_data = {
            "access_token": token_original
        }
        refresh_response = client.post("/api/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK
        
        nuevo_token = refresh_response.json()["access_token"]
        assert nuevo_token != token_original
        
        # 3. Logout con el nuevo token
        logout_data = {
            "access_token": nuevo_token
        }
        logout_response = client.post("/api/auth/logout", json=logout_data)
        assert logout_response.status_code == status.HTTP_200_OK
        
        # 4. Intentar usar el token después del logout (refresh)
        refresh_after_logout = client.post("/api/auth/refresh", json={"access_token": nuevo_token})
        assert refresh_after_logout.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_no_afecta_otros_tokens(self, client, usuario_test, token_valido):
        """
        Test: Logout de un token no afecta otros tokens del mismo usuario
        
        Verifica que el logout solo invalida el token específico
        """
        # Arrange - Crear dos tokens diferentes para el mismo usuario
        token_data = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id,
            "nombre": usuario_test.nombre,
        }
        
        token_1 = crear_token_acceso(datos=token_data)
        token_2 = crear_token_acceso(datos=token_data)
        
        # Act - Hacer logout solo del token_1
        logout_data = {
            "access_token": token_1
        }
        logout_response = client.post("/api/auth/logout", json=logout_data)
        assert logout_response.status_code == status.HTTP_200_OK
        
        # Assert - El token_2 sigue siendo válido
        refresh_data = {
            "access_token": token_2
        }
        refresh_response = client.post("/api/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK
    
    def test_refresh_multiple_veces(self, client, usuario_test, token_valido):
        """
        Test: Renovar token múltiples veces
        
        Verifica que un token puede ser renovado varias veces consecutivas
        """
        # Arrange
        token_actual = token_valido
        
        # Act - Renovar token 3 veces
        for i in range(3):
            refresh_data = {
                "access_token": token_actual
            }
            response = client.post("/api/auth/refresh", json=refresh_data)
            
            # Assert - Cada renovación es exitosa
            assert response.status_code == status.HTTP_200_OK
            
            # Obtener el nuevo token para la siguiente iteración
            token_actual = response.json()["access_token"]
            
            # Verificar que el nuevo token es diferente
            assert token_actual != token_valido


# ==================== Tests de Seguridad ====================

class TestSeguridad:
    """Tests de seguridad y edge cases"""
    
    def test_refresh_token_tiene_expiracion_extendida(self, client, usuario_test, token_valido):
        """
        Test: El refresh token tiene expiración extendida (7 días)
        
        Verifica que el nuevo token tiene una expiración mayor al token original
        """
        # Arrange
        payload_original = decodificar_token(token_valido)
        exp_original = datetime.fromtimestamp(payload_original["exp"])
        
        # Act - Refresh token
        refresh_data = {
            "access_token": token_valido
        }
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        nuevo_token = response.json()["access_token"]
        payload_nuevo = decodificar_token(nuevo_token)
        exp_nuevo = datetime.fromtimestamp(payload_nuevo["exp"])
        
        # Assert - El nuevo token expira mucho después
        diferencia = (exp_nuevo - exp_original).total_seconds()
        
        # Debe tener al menos 6 días más de expiración
        # (7 días del refresh - 30 min del original ≈ 6.9 días)
        assert diferencia > 6 * 24 * 60 * 60  # 6 días en segundos
    
    def test_refresh_token_mantiene_datos_usuario(self, client, usuario_test, token_valido):
        """
        Test: El refresh token mantiene los datos del usuario
        
        Verifica que el nuevo token contiene la misma información del usuario
        """
        # Arrange
        payload_original = decodificar_token(token_valido)
        
        # Act
        refresh_data = {
            "access_token": token_valido
        }
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        nuevo_token = response.json()["access_token"]
        payload_nuevo = decodificar_token(nuevo_token)
        
        # Assert - Los datos del usuario son los mismos
        assert payload_nuevo["sub"] == payload_original["sub"]
        assert payload_nuevo["user_id"] == payload_original["user_id"]
        assert payload_nuevo["nombre"] == payload_original["nombre"]
    
    def test_token_con_secret_key_incorrecta(self, client, usuario_test):
        """
        Test: Token firmado con secret key incorrecta es rechazado
        
        Verifica que un token firmado con otra clave no es válido
        """
        # Arrange - Crear token con secret key diferente
        token_data = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id,
            "nombre": usuario_test.nombre,
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        }
        
        token_falso = jwt.encode(
            token_data,
            "SECRET_KEY_INCORRECTA",
            algorithm="HS256"
        )
        
        # Act - Intentar refresh con token falso
        refresh_data = {
            "access_token": token_falso
        }
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_previene_uso_malicioso_token_robado(self, client, usuario_test, token_valido):
        """
        Test: Logout previene el uso de un token robado
        
        Simula el escenario donde un atacante roba un token,
        el usuario hace logout, y el atacante no puede usar el token
        """
        # Arrange - Simular que el atacante tiene el token
        token_robado = token_valido
        
        # Act 1 - Usuario hace logout
        logout_data = {
            "access_token": token_robado
        }
        logout_response = client.post("/api/auth/logout", json=logout_data)
        assert logout_response.status_code == status.HTTP_200_OK
        
        # Act 2 - Atacante intenta usar el token robado
        refresh_data = {
            "access_token": token_robado
        }
        refresh_response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Assert - El token robado no puede ser usado
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_response_no_expone_informacion_sensible(self, client, token_valido):
        """
        Test: Los responses no exponen información sensible
        
        Verifica que los errores no revelan información sobre usuarios,
        estructura de la BD, etc.
        """
        # Act - Intentar refresh con token inválido
        refresh_data = {
            "access_token": "token_invalido"
        }
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # Assert - El mensaje de error es genérico
        response_text = response.text.lower()
        
        # No debe contener información sensible
        assert "password" not in response_text
        assert "database" not in response_text
        assert "sql" not in response_text
        assert "traceback" not in response_text
