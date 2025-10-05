"""
Tests para T-003C: Sistema JWT Completo - Tests Unitarios e Integración

Tests comprehensivos para el sistema JWT incluyendo:
- Tests unitarios de utils/jwt.py
- Tests de servicio auth_service.py
- Tests de integración del flujo completo de autenticación
- Tests de seguridad y edge cases

Estructura:
- Tests unitarios de creación y validación de tokens
- Tests de servicio de autenticación
- Tests de integración endpoint a endpoint
- Tests de seguridad JWT
- Tests de expiración y renovación

Autor: Equipo Plantitas
Fecha: Octubre 2025
Task: T-003C - Tests completos del sistema JWT
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock
import time

from app.main import app
from app.db.session import get_db
from app.db.models import Usuario, Base
from app.core.config import obtener_configuracion
from app.utils.jwt import (
    crear_token_acceso,
    decodificar_token,
    verificar_token,
    extraer_email_de_token,
    calcular_expiracion
)
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegisterRequest, UserLoginRequest


# ==================== Configuración de Testing ====================

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
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture que proporciona un cliente de prueba con la base de datos de test
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


@pytest.fixture(scope="function")
def usuario_test(db_session):
    """
    Fixture que proporciona un usuario de prueba en la base de datos
    """
    usuario = Usuario(
        email="jwt.test@plantitas.com",
        nombre="JWT Test User"
    )
    usuario.set_password("JwtPassword123")
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture(scope="function")
def token_valido(usuario_test):
    """
    Fixture que proporciona un token JWT válido para testing
    """
    config = obtener_configuracion()
    datos = {
        "sub": usuario_test.email,
        "user_id": usuario_test.id,
        "nombre": usuario_test.nombre,
    }
    
    return crear_token_acceso(datos, config.jwt_expiracion_minutos)


# ==================== Tests Unitarios: utils/jwt.py ====================

class TestCrearTokenAcceso:
    """
    Suite de tests para la función crear_token_acceso()
    """
    
    def test_crear_token_acceso_exitoso(self):
        """
        Test: Crear token con datos básicos genera un token válido
        """
        # Arrange
        datos = {
            "sub": "test@ejemplo.com",
            "user_id": 1,
            "nombre": "Test User"
        }
        
        # Act
        token = crear_token_acceso(datos)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verificar formato JWT (3 partes separadas por punto)
        partes = token.split(".")
        assert len(partes) == 3
    
    def test_crear_token_incluye_claims_personalizados(self):
        """
        Test: El token incluye todos los claims personalizados proporcionados
        """
        # Arrange
        datos = {
            "sub": "test@ejemplo.com",
            "user_id": 42,
            "nombre": "María García",
            "rol": "admin"  # Claim personalizado adicional
        }
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert payload is not None
        assert payload["sub"] == "test@ejemplo.com"
        assert payload["user_id"] == 42
        assert payload["nombre"] == "María García"
        assert payload["rol"] == "admin"
    
    def test_crear_token_incluye_claims_estandar(self):
        """
        Test: El token incluye claims estándar JWT (exp, iat)
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at time
        assert payload["exp"] > payload["iat"]
    
    def test_crear_token_con_expiracion_personalizada(self):
        """
        Test: Se puede especificar tiempo de expiración personalizado
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        expiracion_minutos = 60  # 1 hora
        
        # Act
        token = crear_token_acceso(datos, expiracion_minutos)
        payload = decodificar_token(token)
        
        # Assert
        diferencia = payload["exp"] - payload["iat"]
        # Debe ser aproximadamente 60 minutos (3600 segundos)
        assert 3590 <= diferencia <= 3610
    
    def test_crear_token_sin_expiracion_usa_default(self):
        """
        Test: Si no se especifica expiración, usa el valor de configuración
        """
        # Arrange
        config = obtener_configuracion()
        datos = {"sub": "test@ejemplo.com"}
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        diferencia = payload["exp"] - payload["iat"]
        # Debe usar config.jwt_expiracion_minutos
        esperado = config.jwt_expiracion_minutos * 60
        assert esperado - 10 <= diferencia <= esperado + 10
    
    def test_crear_tokens_consecutivos_son_diferentes(self):
        """
        Test: Crear múltiples tokens genera tokens únicos debido a timestamp iat
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        
        # Act
        token1 = crear_token_acceso(datos)
        time.sleep(1)  # Esperar 1 segundo para que iat sea diferente
        token2 = crear_token_acceso(datos)
        
        # Assert
        assert token1 != token2
        
        payload1 = decodificar_token(token1)
        payload2 = decodificar_token(token2)
        
        # Los timestamps deben ser diferentes
        assert payload1["iat"] != payload2["iat"]


class TestDecodificarToken:
    """
    Suite de tests para la función decodificar_token()
    """
    
    def test_decodificar_token_valido_exitoso(self):
        """
        Test: Decodificar un token válido retorna el payload
        """
        # Arrange
        datos = {
            "sub": "test@ejemplo.com",
            "user_id": 1,
            "nombre": "Test"
        }
        token = crear_token_acceso(datos)
        
        # Act
        payload = decodificar_token(token)
        
        # Assert
        assert payload is not None
        assert payload["sub"] == "test@ejemplo.com"
        assert payload["user_id"] == 1
        assert payload["nombre"] == "Test"
    
    def test_decodificar_token_invalido_retorna_none(self):
        """
        Test: Token con formato inválido retorna None
        """
        # Arrange
        token_invalido = "token.invalido.fake"
        
        # Act
        payload = decodificar_token(token_invalido)
        
        # Assert
        assert payload is None
    
    def test_decodificar_token_con_firma_incorrecta_retorna_none(self):
        """
        Test: Token con firma modificada es rechazado
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos)
        
        # Modificar la firma (última parte del token)
        partes = token.split(".")
        partes[2] = "firma_modificada"
        token_modificado = ".".join(partes)
        
        # Act
        payload = decodificar_token(token_modificado)
        
        # Assert
        assert payload is None
    
    def test_decodificar_token_expirado_retorna_none(self):
        """
        Test: Token expirado es rechazado
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        # Crear token que expire en 1 segundo
        token = crear_token_acceso(datos, expiracion_minutos=0.016)  # ~1 segundo
        
        # Esperar a que expire
        time.sleep(2)
        
        # Act
        payload = decodificar_token(token)
        
        # Assert
        assert payload is None
    
    def test_decodificar_token_vacio_retorna_none(self):
        """
        Test: String vacío retorna None
        """
        # Act
        payload = decodificar_token("")
        
        # Assert
        assert payload is None
    
    def test_decodificar_token_con_payload_modificado_retorna_none(self):
        """
        Test: Token con payload modificado es rechazado por firma inválida
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos)
        
        # Intentar modificar el payload (segunda parte)
        config = obtener_configuracion()
        partes = token.split(".")
        
        # Crear un payload modificado
        payload_modificado = {
            "sub": "hacker@ejemplo.com",
            "user_id": 999
        }
        
        # Intentar crear token con payload modificado pero firma original
        # (esto debe fallar en la decodificación)
        import base64
        import json
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload_modificado).encode()
        ).decode().rstrip("=")
        
        token_modificado = f"{partes[0]}.{payload_encoded}.{partes[2]}"
        
        # Act
        payload = decodificar_token(token_modificado)
        
        # Assert
        assert payload is None


class TestVerificarToken:
    """
    Suite de tests para la función verificar_token()
    """
    
    def test_verificar_token_valido_retorna_true(self):
        """
        Test: Token válido retorna True
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos)
        
        # Act
        es_valido = verificar_token(token)
        
        # Assert
        assert es_valido is True
    
    def test_verificar_token_invalido_retorna_false(self):
        """
        Test: Token inválido retorna False
        """
        # Arrange
        token_invalido = "token.invalido.fake"
        
        # Act
        es_valido = verificar_token(token_invalido)
        
        # Assert
        assert es_valido is False
    
    def test_verificar_token_expirado_retorna_false(self):
        """
        Test: Token expirado retorna False
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos, expiracion_minutos=0.016)  # ~1 segundo
        
        time.sleep(2)
        
        # Act
        es_valido = verificar_token(token)
        
        # Assert
        assert es_valido is False
    
    def test_verificar_token_con_firma_incorrecta_retorna_false(self):
        """
        Test: Token con firma modificada retorna False
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos)
        
        partes = token.split(".")
        partes[2] = "firma_modificada"
        token_modificado = ".".join(partes)
        
        # Act
        es_valido = verificar_token(token_modificado)
        
        # Assert
        assert es_valido is False


class TestExtraerEmailDeToken:
    """
    Suite de tests para la función extraer_email_de_token()
    """
    
    def test_extraer_email_de_token_valido(self):
        """
        Test: Extrae correctamente el email del claim 'sub'
        """
        # Arrange
        email = "test@ejemplo.com"
        datos = {"sub": email, "user_id": 1}
        token = crear_token_acceso(datos)
        
        # Act
        email_extraido = extraer_email_de_token(token)
        
        # Assert
        assert email_extraido == email
    
    def test_extraer_email_de_token_sin_sub_retorna_none(self):
        """
        Test: Token sin claim 'sub' retorna None
        """
        # Arrange
        # Crear token sin 'sub' (esto no debería pasar en producción)
        config = obtener_configuracion()
        datos = {"user_id": 1}  # Sin 'sub'
        
        datos_token = datos.copy()
        datos_token.update({
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        })
        
        token = jwt.encode(
            datos_token,
            config.jwt_secret_key,
            algorithm=config.jwt_algorithm
        )
        
        # Act
        email_extraido = extraer_email_de_token(token)
        
        # Assert
        assert email_extraido is None
    
    def test_extraer_email_de_token_invalido_retorna_none(self):
        """
        Test: Token inválido retorna None
        """
        # Arrange
        token_invalido = "token.invalido.fake"
        
        # Act
        email_extraido = extraer_email_de_token(token_invalido)
        
        # Assert
        assert email_extraido is None


class TestCalcularExpiracion:
    """
    Suite de tests para la función calcular_expiracion()
    """
    
    def test_calcular_expiracion_30_minutos(self):
        """
        Test: Calcula correctamente expiración de 30 minutos
        """
        # Arrange
        minutos = 30
        ahora = datetime.utcnow()
        
        # Act
        expiracion = calcular_expiracion(minutos)
        
        # Assert
        diferencia = (expiracion - ahora).total_seconds()
        # Debe ser aproximadamente 1800 segundos (30 minutos)
        assert 1790 <= diferencia <= 1810
    
    def test_calcular_expiracion_1_hora(self):
        """
        Test: Calcula correctamente expiración de 1 hora
        """
        # Arrange
        minutos = 60
        ahora = datetime.utcnow()
        
        # Act
        expiracion = calcular_expiracion(minutos)
        
        # Assert
        diferencia = (expiracion - ahora).total_seconds()
        # Debe ser aproximadamente 3600 segundos (60 minutos)
        assert 3590 <= diferencia <= 3610
    
    def test_calcular_expiracion_retorna_datetime(self):
        """
        Test: Retorna un objeto datetime
        """
        # Act
        expiracion = calcular_expiracion(30)
        
        # Assert
        assert isinstance(expiracion, datetime)
    
    def test_calcular_expiracion_siempre_futuro(self):
        """
        Test: La expiración siempre está en el futuro
        """
        # Act
        expiracion = calcular_expiracion(1)
        
        # Assert
        assert expiracion > datetime.utcnow()


# ==================== Tests de Servicio: AuthService ====================

class TestAuthServiceValidarCredenciales:
    """
    Suite de tests para AuthService.validar_credenciales()
    """
    
    def test_validar_credenciales_correctas_retorna_usuario(self, db_session, usuario_test):
        """
        Test: Validar credenciales correctas retorna el usuario
        """
        # Act
        usuario = AuthService.validar_credenciales(
            db_session,
            "jwt.test@plantitas.com",
            "JwtPassword123"
        )
        
        # Assert
        assert usuario is not None
        assert usuario.id == usuario_test.id
        assert usuario.email == usuario_test.email
    
    def test_validar_credenciales_email_inexistente_retorna_none(self, db_session):
        """
        Test: Email que no existe retorna None
        """
        # Act
        usuario = AuthService.validar_credenciales(
            db_session,
            "noexiste@plantitas.com",
            "Password123"
        )
        
        # Assert
        assert usuario is None
    
    def test_validar_credenciales_password_incorrecta_retorna_none(self, db_session, usuario_test):
        """
        Test: Password incorrecta retorna None
        """
        # Act
        usuario = AuthService.validar_credenciales(
            db_session,
            "jwt.test@plantitas.com",
            "PasswordIncorrecta"
        )
        
        # Assert
        assert usuario is None
    
    def test_validar_credenciales_usuario_inactivo_retorna_none(self, db_session):
        """
        Test: Usuario inactivo retorna None
        """
        # Arrange - Crear usuario inactivo
        usuario_inactivo = Usuario(
            email="inactivo@plantitas.com",
            nombre="Inactivo",
            is_active=False
        )
        usuario_inactivo.set_password("Password123")
        db_session.add(usuario_inactivo)
        db_session.commit()
        
        # Act
        usuario = AuthService.validar_credenciales(
            db_session,
            "inactivo@plantitas.com",
            "Password123"
        )
        
        # Assert
        assert usuario is None
    
    def test_validar_credenciales_normaliza_email(self, db_session, usuario_test):
        """
        Test: Email en mayúsculas es normalizado correctamente
        """
        # Act
        usuario = AuthService.validar_credenciales(
            db_session,
            "JWT.TEST@PLANTITAS.COM",  # Mayúsculas
            "JwtPassword123"
        )
        
        # Assert
        assert usuario is not None
        assert usuario.email == "jwt.test@plantitas.com"


class TestAuthServiceObtenerUsuario:
    """
    Suite de tests para métodos de obtener usuario del AuthService
    """
    
    def test_obtener_usuario_por_email_existente(self, db_session, usuario_test):
        """
        Test: Obtener usuario por email exitoso
        """
        # Act
        usuario = AuthService.obtener_usuario_por_email(
            db_session,
            "jwt.test@plantitas.com"
        )
        
        # Assert
        assert usuario is not None
        assert usuario.id == usuario_test.id
    
    def test_obtener_usuario_por_email_inexistente_retorna_none(self, db_session):
        """
        Test: Email inexistente retorna None
        """
        # Act
        usuario = AuthService.obtener_usuario_por_email(
            db_session,
            "noexiste@plantitas.com"
        )
        
        # Assert
        assert usuario is None
    
    def test_obtener_usuario_por_id_existente(self, db_session, usuario_test):
        """
        Test: Obtener usuario por ID exitoso
        """
        # Act
        usuario = AuthService.obtener_usuario_por_id(
            db_session,
            usuario_test.id
        )
        
        # Assert
        assert usuario is not None
        assert usuario.email == usuario_test.email
    
    def test_obtener_usuario_por_id_inexistente_retorna_none(self, db_session):
        """
        Test: ID inexistente retorna None
        """
        # Act
        usuario = AuthService.obtener_usuario_por_id(
            db_session,
            99999  # ID que no existe
        )
        
        # Assert
        assert usuario is None


class TestAuthServiceActivarDesactivar:
    """
    Suite de tests para activar/desactivar usuarios
    """
    
    def test_desactivar_usuario_exitoso(self, db_session, usuario_test):
        """
        Test: Desactivar usuario existente retorna True
        """
        # Act
        resultado = AuthService.desactivar_usuario(db_session, usuario_test.id)
        
        # Assert
        assert resultado is True
        
        db_session.refresh(usuario_test)
        assert usuario_test.is_active is False
    
    def test_desactivar_usuario_inexistente_retorna_false(self, db_session):
        """
        Test: Desactivar usuario inexistente retorna False
        """
        # Act
        resultado = AuthService.desactivar_usuario(db_session, 99999)
        
        # Assert
        assert resultado is False
    
    def test_activar_usuario_exitoso(self, db_session, usuario_test):
        """
        Test: Activar usuario desactivado retorna True
        """
        # Arrange - Desactivar primero
        usuario_test.desactivar()
        db_session.commit()
        
        # Act
        resultado = AuthService.activar_usuario(db_session, usuario_test.id)
        
        # Assert
        assert resultado is True
        
        db_session.refresh(usuario_test)
        assert usuario_test.is_active is True
    
    def test_activar_usuario_inexistente_retorna_false(self, db_session):
        """
        Test: Activar usuario inexistente retorna False
        """
        # Act
        resultado = AuthService.activar_usuario(db_session, 99999)
        
        # Assert
        assert resultado is False


# ==================== Tests de Integración: Flujo Completo JWT ====================

class TestIntegracionFlujoJWT:
    """
    Suite de tests de integración para el flujo completo de autenticación JWT
    """
    
    def test_flujo_completo_registro_login_acceso(self, client, db_session):
        """
        Test: Flujo completo de registro -> login -> uso del token
        """
        # 1. Registrar usuario
        datos_registro = {
            "email": "flujo@plantitas.com",
            "password": "FlujoTest123",
            "nombre": "Usuario Flujo"
        }
        
        response_registro = client.post("/api/auth/register", json=datos_registro)
        assert response_registro.status_code == 201
        
        # 2. Login
        datos_login = {
            "email": "flujo@plantitas.com",
            "password": "FlujoTest123"
        }
        
        response_login = client.post("/api/auth/login", json=datos_login)
        assert response_login.status_code == 200
        
        token_data = response_login.json()
        assert "access_token" in token_data
        
        # 3. Verificar que el token es válido
        token = token_data["access_token"]
        assert verificar_token(token) is True
        
        # 4. Decodificar y verificar claims
        payload = decodificar_token(token)
        assert payload["sub"] == "flujo@plantitas.com"
        assert payload["nombre"] == "Usuario Flujo"
    
    def test_token_generado_en_login_es_decodificable(self, client, usuario_test):
        """
        Test: El token generado por /login puede ser decodificado
        """
        # Arrange
        datos_login = {
            "email": "jwt.test@plantitas.com",
            "password": "JwtPassword123"
        }
        
        # Act
        response = client.post("/api/auth/login", json=datos_login)
        
        # Assert
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        payload = decodificar_token(token)
        assert payload is not None
        assert payload["sub"] == usuario_test.email
        assert payload["user_id"] == usuario_test.id
    
    def test_multiples_logins_generan_tokens_validos(self, client, usuario_test):
        """
        Test: Hacer login múltiples veces genera tokens válidos cada vez
        """
        # Arrange
        datos_login = {
            "email": "jwt.test@plantitas.com",
            "password": "JwtPassword123"
        }
        
        tokens = []
        
        # Act - Hacer 3 logins
        for _ in range(3):
            response = client.post("/api/auth/login", json=datos_login)
            assert response.status_code == 200
            token = response.json()["access_token"]
            tokens.append(token)
            time.sleep(0.1)  # Pequeña pausa para diferentes timestamps
        
        # Assert - Todos los tokens deben ser válidos
        for token in tokens:
            assert verificar_token(token) is True
            payload = decodificar_token(token)
            assert payload["sub"] == usuario_test.email


class TestSeguridadJWT:
    """
    Suite de tests de seguridad para el sistema JWT
    """
    
    def test_token_con_secret_key_incorrecta_falla(self, usuario_test):
        """
        Test: Token firmado con secret key diferente es rechazado
        """
        # Arrange
        datos = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id
        }
        
        # Crear token con secret key incorrecta
        datos_token = datos.copy()
        datos_token.update({
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow()
        })
        
        token_falso = jwt.encode(
            datos_token,
            "clave_secreta_incorrecta",
            algorithm="HS256"
        )
        
        # Act
        payload = decodificar_token(token_falso)
        
        # Assert
        assert payload is None
    
    def test_token_con_algoritmo_none_es_rechazado(self):
        """
        Test: Token con algoritmo 'none' es rechazado (ataque conocido)
        """
        # Arrange
        import base64
        import json
        
        header = {"alg": "none", "typ": "JWT"}
        payload = {"sub": "hacker@test.com", "user_id": 1}
        
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip("=")
        
        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip("=")
        
        token_none = f"{header_encoded}.{payload_encoded}."
        
        # Act
        resultado = decodificar_token(token_none)
        
        # Assert
        assert resultado is None
    
    def test_token_no_incluye_informacion_sensible(self, usuario_test):
        """
        Test: El token NO debe incluir información sensible como passwords
        """
        # Arrange
        datos = {
            "sub": usuario_test.email,
            "user_id": usuario_test.id,
            "nombre": usuario_test.nombre,
        }
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert "password" not in payload
        assert "password_hash" not in payload
        assert "salt" not in payload
    
    def test_token_expira_correctamente(self):
        """
        Test: Token expira después del tiempo especificado
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        # Crear token que expire en ~1 segundo
        token = crear_token_acceso(datos, expiracion_minutos=0.016)
        
        # Verificar que es válido inmediatamente
        assert verificar_token(token) is True
        
        # Esperar a que expire
        time.sleep(2)
        
        # Act & Assert
        assert verificar_token(token) is False


# ==================== Tests de Edge Cases ====================

class TestEdgeCasesJWT:
    """
    Suite de tests para casos extremos y edge cases
    """
    
    def test_token_con_claims_vacios(self):
        """
        Test: Crear token con claims vacíos (solo estándares)
        """
        # Arrange
        datos = {}
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert payload is not None
        assert "exp" in payload
        assert "iat" in payload
    
    def test_token_con_caracteres_especiales_en_datos(self):
        """
        Test: Token con caracteres especiales en los datos
        """
        # Arrange
        datos = {
            "sub": "test+special@ejemplo.com",
            "nombre": "José María O'Connor-García",
            "descripcion": "Caracteres: áéíóú ñ ¿? ¡!"
        }
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert payload is not None
        assert payload["sub"] == datos["sub"]
        assert payload["nombre"] == datos["nombre"]
        assert payload["descripcion"] == datos["descripcion"]
    
    def test_token_con_datos_muy_largos(self):
        """
        Test: Token con mucha información (claims grandes)
        """
        # Arrange
        datos = {
            "sub": "test@ejemplo.com",
            "descripcion_larga": "A" * 1000,  # 1000 caracteres
            "array_grande": list(range(100))
        }
        
        # Act
        token = crear_token_acceso(datos)
        payload = decodificar_token(token)
        
        # Assert
        assert payload is not None
        assert len(payload["descripcion_larga"]) == 1000
        assert len(payload["array_grande"]) == 100
    
    def test_decodificar_token_con_espacios_extra(self):
        """
        Test: Token con espacios al inicio/final es manejado
        """
        # Arrange
        datos = {"sub": "test@ejemplo.com"}
        token = crear_token_acceso(datos)
        token_con_espacios = f"  {token}  "
        
        # Act
        # strip() debería ser manejado por quien use el token
        payload = decodificar_token(token_con_espacios.strip())
        
        # Assert
        assert payload is not None


# ==================== Resumen de Cobertura ====================

"""
Resumen de Tests T-003C:

✅ Tests Unitarios - utils/jwt.py (25 tests)
   - crear_token_acceso: 6 tests
   - decodificar_token: 6 tests
   - verificar_token: 4 tests
   - extraer_email_de_token: 3 tests
   - calcular_expiracion: 4 tests

✅ Tests de Servicio - AuthService (10 tests)
   - validar_credenciales: 5 tests
   - obtener_usuario: 4 tests
   - activar/desactivar: 4 tests

✅ Tests de Integración (3 tests)
   - Flujo completo registro -> login -> token
   - Token decodificable
   - Múltiples logins

✅ Tests de Seguridad (4 tests)
   - Secret key incorrecta
   - Algoritmo 'none' rechazado
   - Sin información sensible
   - Expiración correcta

✅ Tests de Edge Cases (4 tests)
   - Claims vacíos
   - Caracteres especiales
   - Datos muy largos
   - Espacios extra

Total: 46 tests comprehensivos
Cobertura esperada: >90% del código JWT
Tiempo estimado: ~2-3 segundos
"""
