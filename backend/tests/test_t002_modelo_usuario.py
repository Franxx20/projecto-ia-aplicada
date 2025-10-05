"""
Tests unitarios para el modelo de Usuario - T-002

Este módulo contiene tests completos para verificar el modelo Usuario
y sus funcionalidades de hashing de contraseñas, validación y métodos auxiliares.

Sprint: Sprint 1 - Épica 1: Fundación de la Aplicación
Task: T-002 - Implementar modelos de usuario con SQLAlchemy (8pts)
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Usuario


# Fixture para crear engine de base de datos en memoria
@pytest.fixture(scope="function")
def engine():
    """
    Crea un engine SQLAlchemy con base de datos SQLite en memoria.
    
    Yields:
        Engine: Motor SQLAlchemy para tests
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """
    Crea una sesión de base de datos para tests.
    
    Args:
        engine: Fixture del motor SQLAlchemy
        
    Yields:
        Session: Sesión SQLAlchemy para operaciones de BD
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


class TestModeloUsuario:
    """Tests para el modelo de Usuario y sus campos básicos"""
    
    def test_crear_usuario_basico(self, session):
        """
        Test: Crear un usuario con campos básicos.
        
        Verifica que se puede crear un usuario con email y contraseña,
        y que los campos por defecto se asignan correctamente.
        """
        # Arrange & Act
        usuario = Usuario(
            email="test@example.com",
            nombre="Usuario Test"
        )
        usuario.set_password("contraseña_segura_123")
        session.add(usuario)
        session.commit()
        
        # Assert
        assert usuario.id is not None
        assert usuario.email == "test@example.com"
        assert usuario.nombre == "Usuario Test"
        assert usuario.is_active is True
        assert usuario.is_superuser is False
        assert usuario.created_at is not None
        assert usuario.updated_at is not None
        assert usuario.password_hash is not None
        assert usuario.password_hash != "contraseña_segura_123"
    
    def test_email_unico(self, session):
        """
        Test: El email debe ser único en la base de datos.
        
        Verifica que no se pueden crear dos usuarios con el mismo email.
        """
        # Arrange
        usuario1 = Usuario(email="duplicado@example.com")
        usuario1.set_password("pass123")
        session.add(usuario1)
        session.commit()
        
        # Act & Assert
        usuario2 = Usuario(email="duplicado@example.com")
        usuario2.set_password("pass456")
        session.add(usuario2)
        
        with pytest.raises(Exception):  # IntegrityError o similar
            session.commit()
    
    def test_email_requerido(self):
        """
        Test: El email es un campo obligatorio.
        
        Verifica que no se puede crear un usuario sin email.
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):
            usuario = Usuario(nombre="Sin Email")
    
    def test_timestamps_automaticos(self, session):
        """
        Test: Los timestamps se asignan automáticamente.
        
        Verifica que created_at y updated_at se establecen automáticamente
        al crear un usuario.
        """
        # Arrange & Act
        antes = datetime.utcnow()
        usuario = Usuario(email="timestamps@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        despues = datetime.utcnow()
        
        # Assert
        assert usuario.created_at is not None
        assert usuario.updated_at is not None
        assert antes <= usuario.created_at <= despues
        assert antes <= usuario.updated_at <= despues
    
    def test_valores_por_defecto(self, session):
        """
        Test: Los valores por defecto se asignan correctamente.
        
        Verifica que is_active=True e is_superuser=False por defecto.
        """
        # Arrange & Act
        usuario = Usuario(email="defaults@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Assert
        assert usuario.is_active is True
        assert usuario.is_superuser is False
    
    def test_nombre_opcional(self, session):
        """
        Test: El campo nombre es opcional.
        
        Verifica que se puede crear un usuario sin nombre.
        """
        # Arrange & Act
        usuario = Usuario(email="sin_nombre@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Assert
        assert usuario.nombre is None


class TestHashingPasswords:
    """Tests para funcionalidades de hashing y verificación de contraseñas"""
    
    def test_hash_password_estatico(self):
        """
        Test: El método estático hash_password genera un hash válido.
        
        Verifica que el hash generado es diferente de la contraseña original
        y que comienza con el prefijo de bcrypt.
        """
        # Arrange
        password = "mi_contraseña_super_segura"
        
        # Act
        hashed = Usuario.hash_password(password)
        
        # Assert
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # Prefijo de bcrypt
        assert len(hashed) >= 60  # Longitud típica de hash bcrypt
    
    def test_set_password(self, session):
        """
        Test: El método set_password hashea correctamente la contraseña.
        
        Verifica que set_password almacena un hash y no la contraseña plana.
        """
        # Arrange
        usuario = Usuario(email="test_set@example.com")
        password = "contraseña_original"
        
        # Act
        usuario.set_password(password)
        
        # Assert
        assert usuario.password_hash is not None
        assert usuario.password_hash != password
        assert usuario.password_hash.startswith("$2b$")
    
    def test_verify_password_correcta(self, session):
        """
        Test: verify_password retorna True con contraseña correcta.
        
        Verifica que se puede validar una contraseña correcta.
        """
        # Arrange
        usuario = Usuario(email="verify@example.com")
        password = "mi_password_123"
        usuario.set_password(password)
        session.add(usuario)
        session.commit()
        
        # Act
        resultado = usuario.verify_password(password)
        
        # Assert
        assert resultado is True
    
    def test_verify_password_incorrecta(self, session):
        """
        Test: verify_password retorna False con contraseña incorrecta.
        
        Verifica que se rechaza una contraseña incorrecta.
        """
        # Arrange
        usuario = Usuario(email="verify2@example.com")
        usuario.set_password("password_correcto")
        session.add(usuario)
        session.commit()
        
        # Act
        resultado = usuario.verify_password("password_incorrecto")
        
        # Assert
        assert resultado is False
    
    def test_hash_diferente_cada_vez(self):
        """
        Test: El mismo password genera diferentes hashes (salt único).
        
        Verifica que bcrypt genera un salt único para cada hash,
        aunque la contraseña sea la misma.
        """
        # Arrange
        password = "misma_contraseña"
        
        # Act
        hash1 = Usuario.hash_password(password)
        hash2 = Usuario.hash_password(password)
        
        # Assert
        assert hash1 != hash2  # Diferentes hashes
        # Pero ambos deben validar con la misma contraseña
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        assert pwd_context.verify(password, hash1)
        assert pwd_context.verify(password, hash2)


class TestMetodosUtilidad:
    """Tests para métodos auxiliares del modelo Usuario"""
    
    def test_to_dict_sin_password(self, session):
        """
        Test: to_dict no incluye password_hash por defecto.
        
        Verifica que la representación en diccionario es segura
        y no expone el hash de contraseña.
        """
        # Arrange
        usuario = Usuario(
            email="dict@example.com",
            nombre="Usuario Dict"
        )
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Act
        data = usuario.to_dict()
        
        # Assert
        assert 'id' in data
        assert 'email' in data
        assert 'nombre' in data
        assert 'is_active' in data
        assert 'is_superuser' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'password_hash' not in data
    
    def test_to_dict_con_password(self, session):
        """
        Test: to_dict puede incluir password_hash si se solicita.
        
        Verifica que se puede obtener el hash si es necesario
        (por ejemplo, para migraciones).
        """
        # Arrange
        usuario = Usuario(email="dict2@example.com")
        usuario.set_password("pass456")
        session.add(usuario)
        session.commit()
        
        # Act
        data = usuario.to_dict(include_password=True)
        
        # Assert
        assert 'password_hash' in data
        assert data['password_hash'] == usuario.password_hash
    
    def test_activate(self, session):
        """
        Test: El método activate activa un usuario desactivado.
        
        Verifica que se puede activar un usuario.
        """
        # Arrange
        usuario = Usuario(email="activate@example.com")
        usuario.set_password("pass123")
        usuario.is_active = False
        session.add(usuario)
        session.commit()
        updated_at_antes = usuario.updated_at
        
        # Act
        usuario.activate()
        session.commit()
        
        # Assert
        assert usuario.is_active is True
        assert usuario.updated_at > updated_at_antes
    
    def test_deactivate(self, session):
        """
        Test: El método deactivate desactiva un usuario activo.
        
        Verifica que se puede desactivar un usuario.
        """
        # Arrange
        usuario = Usuario(email="deactivate@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        updated_at_antes = usuario.updated_at
        
        # Act
        usuario.deactivate()
        session.commit()
        
        # Assert
        assert usuario.is_active is False
        assert usuario.updated_at > updated_at_antes
    
    def test_update_info_nombre(self, session):
        """
        Test: update_info actualiza el nombre del usuario.
        
        Verifica que se puede actualizar el nombre.
        """
        # Arrange
        usuario = Usuario(email="update@example.com", nombre="Nombre Viejo")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        updated_at_antes = usuario.updated_at
        
        # Act
        usuario.update_info(nombre="Nombre Nuevo")
        session.commit()
        
        # Assert
        assert usuario.nombre == "Nombre Nuevo"
        assert usuario.updated_at > updated_at_antes
    
    def test_update_info_email(self, session):
        """
        Test: update_info actualiza el email del usuario.
        
        Verifica que se puede actualizar el email.
        """
        # Arrange
        usuario = Usuario(email="old@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Act
        usuario.update_info(email="new@example.com")
        session.commit()
        
        # Assert
        assert usuario.email == "new@example.com"
    
    def test_repr(self, session):
        """
        Test: La representación __repr__ es legible.
        
        Verifica que __repr__ muestra información útil del usuario.
        """
        # Arrange
        usuario = Usuario(email="repr@example.com", nombre="Test Repr")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Act
        repr_str = repr(usuario)
        
        # Assert
        assert "Usuario" in repr_str
        assert "repr@example.com" in repr_str
        assert "Test Repr" in repr_str
        assert str(usuario.id) in repr_str
    
    def test_str(self, session):
        """
        Test: La representación __str__ retorna el email.
        
        Verifica que __str__ muestra el email del usuario.
        """
        # Arrange
        usuario = Usuario(email="str@example.com")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Act
        str_representation = str(usuario)
        
        # Assert
        assert str_representation == "str@example.com"


class TestIndicesYOptimizacion:
    """Tests relacionados con índices y optimización de queries"""
    
    def test_buscar_por_email(self, session):
        """
        Test: Búsqueda por email es eficiente (usa índice).
        
        Verifica que se puede buscar usuarios por email.
        """
        # Arrange
        usuario = Usuario(email="search@example.com", nombre="Usuario Search")
        usuario.set_password("pass123")
        session.add(usuario)
        session.commit()
        
        # Act
        encontrado = session.query(Usuario).filter_by(email="search@example.com").first()
        
        # Assert
        assert encontrado is not None
        assert encontrado.email == "search@example.com"
        assert encontrado.nombre == "Usuario Search"
    
    def test_buscar_por_email_y_estado(self, session):
        """
        Test: Búsqueda por email y estado (índice compuesto).
        
        Verifica que se puede buscar usuarios activos por email.
        """
        # Arrange
        usuario_activo = Usuario(email="active@example.com")
        usuario_activo.set_password("pass123")
        usuario_activo.is_active = True
        
        usuario_inactivo = Usuario(email="inactive@example.com")
        usuario_inactivo.set_password("pass456")
        usuario_inactivo.is_active = False
        
        session.add(usuario_activo)
        session.add(usuario_inactivo)
        session.commit()
        
        # Act
        usuarios_activos = session.query(Usuario).filter_by(is_active=True).all()
        
        # Assert
        assert len(usuarios_activos) == 1
        assert usuarios_activos[0].email == "active@example.com"


# Marcar todos los tests de este archivo como tests de base de datos
pytestmark = pytest.mark.database
