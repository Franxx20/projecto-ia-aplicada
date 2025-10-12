"""
Tests de integración para T-004: API de Gestión de Imágenes

Tests end-to-end para los endpoints de imágenes con mocks de Azure Blob Storage.
Prueba el flujo completo desde HTTP request hasta respuesta.

Autor: Equipo Plantitas
Fecha: Octubre 2025
Task: T-004 - Implementar API de subida de imágenes
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from io import BytesIO

from app.main import app
from app.db.session import get_db
from app.db.models import Usuario, Imagen, Base
from app.utils.jwt import crear_token_acceso


# ==================== Configuración de Testing ====================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de base de datos para testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup y teardown de la base de datos para cada test."""
    # Eliminar tablas existentes primero para evitar conflictos de índices
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def usuario_test():
    """Crea un usuario de prueba y devuelve sus datos."""
    db = TestingSessionLocal()
    usuario = Usuario(
        email="test@example.com",
        nombre="Usuario Test",
        is_active=True
    )
    usuario.set_password("Password123")
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    # Generar token JWT con 'sub' (estándar JWT para subject/email)
    token = crear_token_acceso({"sub": usuario.email, "user_id": usuario.id})
    
    db.close()
    return {"usuario": usuario, "token": token}


@pytest.fixture
def auth_headers(usuario_test):
    """Headers de autenticación para requests."""
    return {"Authorization": f"Bearer {usuario_test['token']}"}


@pytest.fixture
def mock_azure_blob():
    """Mock global del servicio de Azure Blob Storage."""
    with patch('app.services.imagen_service.AzureBlobService') as mock_azure:
        # Configurar mock del servicio Azure
        mock_instance = Mock()
        mock_instance.container_name = "plantitas-imagenes"
        mock_instance.generar_nombre_blob = Mock(return_value="test-uuid-123.jpg")
        mock_instance.subir_archivo = AsyncMock(return_value=("test-uuid-123.jpg", "https://storage.blob.core.windows.net/container/test-uuid-123.jpg"))
        mock_instance.eliminar_archivo = AsyncMock(return_value=True)
        mock_instance.obtener_url_blob = Mock(return_value="https://storage.blob.core.windows.net/container/test-uuid-123.jpg")
        
        mock_azure.return_value = mock_instance
        yield mock_instance

from app.main import app
from app.db.session import get_db
from app.db.models import Usuario, Imagen, Base
from app.utils.jwt import crear_token_acceso


# ==================== Configuración de Testing ====================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia de base de datos para testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup y teardown de la base de datos para cada test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def usuario_test():
    """Crea un usuario de prueba y devuelve sus datos."""
    db = TestingSessionLocal()
    usuario = Usuario(
        email="test@example.com",
        nombre="Usuario Test",
        is_active=True
    )
    usuario.set_password("Password123")
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    # Generar token JWT con 'sub' (estándar JWT para subject/email)
    token = crear_token_acceso({"sub": usuario.email, "user_id": usuario.id})
    
    db.close()
    return {"usuario": usuario, "token": token}


@pytest.fixture
def auth_headers(usuario_test):
    """Headers de autenticación para requests."""
    return {"Authorization": f"Bearer {usuario_test['token']}"}


@pytest.fixture
def mock_azure_blob():
    """Mock global del servicio de Azure Blob Storage."""
    with patch('app.services.imagen_service.BlobServiceClient') as mock:
        # Configurar mock del blob client
        mock_blob = Mock()
        mock_blob.url = "https://storage.blob.core.windows.net/container/test-uuid-123.jpg"
        mock_blob.upload_blob = Mock()
        mock_blob.delete_blob = Mock()
        
        mock_container = Mock()
        mock_container.exists = Mock(return_value=True)
        mock_container.create_container = Mock()
        
        mock_client = Mock()
        mock_client.get_blob_client = Mock(return_value=mock_blob)
        mock_client.get_container_client = Mock(return_value=mock_container)
        
        mock.from_connection_string = Mock(return_value=mock_client)
        
        yield mock_client


# ==================== Tests de Subida de Imágenes ====================

class TestSubirImagen:
    """Tests para POST /api/imagenes/subir"""
    
    @patch.dict('os.environ', {'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test==;'})
    def test_subir_imagen_exitosa(self, auth_headers, mock_azure_blob):
        """Test: Sube imagen exitosamente."""
        # Crear archivo de prueba
        contenido = b"fake image content"
        files = {
            "archivo": ("test_image.jpg", BytesIO(contenido), "image/jpeg")
        }
        
        response = client.post(
            "/api/imagenes/subir",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["nombre_archivo"] == "test_image.jpg"
        assert "url_blob" in data
        assert data["mensaje"] == "Imagen subida exitosamente"
    
    def test_subir_imagen_sin_autenticacion(self, mock_azure_blob):
        """Test: Falla si no está autenticado."""
        contenido = b"fake image content"
        files = {
            "archivo": ("test_image.jpg", BytesIO(contenido), "image/jpeg")
        }
        
        response = client.post("/api/imagenes/subir", files=files)
        
        assert response.status_code == 401
    
    @patch.dict('os.environ', {'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test==;'})
    def test_subir_imagen_con_descripcion(self, auth_headers, mock_azure_blob):
        """Test: Sube imagen con descripción."""
        contenido = b"fake image content"
        files = {
            "archivo": ("test_image.jpg", BytesIO(contenido), "image/jpeg")
        }
        data = {
            "descripcion": "Mi planta favorita"
        }
        
        response = client.post(
            "/api/imagenes/subir",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201


# ==================== Tests de Listado de Imágenes ====================

class TestListarImagenes:
    """Tests para GET /api/imagenes"""
    
    def test_listar_imagenes_sin_autenticacion(self):
        """Test: Falla si no está autenticado."""
        response = client.get("/api/imagenes")
        assert response.status_code == 401
    
    def test_listar_imagenes_usuario_sin_imagenes(self, auth_headers):
        """Test: Devuelve lista vacía si usuario no tiene imágenes."""
        response = client.get("/api/imagenes", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["imagenes"] == []
        assert data["total"] == 0
    
    def test_listar_imagenes_con_paginacion(self, auth_headers):
        """Test: Paginación funciona correctamente."""
        # Crear imágenes en BD
        db = TestingSessionLocal()
        usuario = db.query(Usuario).filter(Usuario.email == "test@example.com").first()
        
        for i in range(5):
            imagen = Imagen(
                usuario_id=usuario.id,
                nombre_archivo=f"test_{i}.jpg",
                nombre_blob=f"uuid-test-{i}.jpg",
                url_blob=f"https://storage.blob.core.windows.net/container/test-{i}.jpg",
                container_name="plantitas-imagenes",
                content_type="image/jpeg",
                tamano_bytes=1024
            )
            db.add(imagen)
        db.commit()
        db.close()
        
        # Listar con límite
        response = client.get("/api/imagenes?limit=3", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["imagenes"]) == 3
        assert data["total"] == 5


# ==================== Tests de Obtener Imagen ====================

class TestObtenerImagen:
    """Tests para GET /api/imagenes/{id}"""
    
    def test_obtener_imagen_exitosa(self, auth_headers):
        """Test: Obtiene imagen por ID correctamente."""
        # Crear imagen en BD
        db = TestingSessionLocal()
        usuario = db.query(Usuario).filter(Usuario.email == "test@example.com").first()
        
        imagen = Imagen(
            usuario_id=usuario.id,
            nombre_archivo="test.jpg",
            nombre_blob="uuid-test.jpg",
            url_blob="https://storage.blob.core.windows.net/container/test.jpg",
            container_name="plantitas-imagenes",
            content_type="image/jpeg",
            tamano_bytes=1024
        )
        db.add(imagen)
        db.commit()
        db.refresh(imagen)
        imagen_id = imagen.id
        db.close()
        
        response = client.get(f"/api/imagenes/{imagen_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == imagen_id
        assert data["nombre_archivo"] == "test.jpg"
    
    def test_obtener_imagen_no_existe(self, auth_headers):
        """Test: Falla si imagen no existe."""
        response = client.get("/api/imagenes/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_obtener_imagen_sin_autenticacion(self):
        """Test: Falla si no está autenticado."""
        response = client.get("/api/imagenes/1")
        assert response.status_code == 401


# ==================== Tests de Actualizar Imagen ====================

class TestActualizarImagen:
    """Tests para PATCH /api/imagenes/{id}"""
    
    def test_actualizar_descripcion_exitosa(self, auth_headers):
        """Test: Actualiza descripción correctamente."""
        # Crear imagen
        db = TestingSessionLocal()
        usuario = db.query(Usuario).filter(Usuario.email == "test@example.com").first()
        
        imagen = Imagen(
            usuario_id=usuario.id,
            nombre_archivo="test.jpg",
            nombre_blob="uuid-test.jpg",
            url_blob="https://storage.blob.core.windows.net/container/test.jpg",
            container_name="plantitas-imagenes",
            content_type="image/jpeg",
            tamano_bytes=1024,
            descripcion="Descripción original"
        )
        db.add(imagen)
        db.commit()
        db.refresh(imagen)
        imagen_id = imagen.id
        db.close()
        
        # Actualizar descripción
        response = client.patch(
            f"/api/imagenes/{imagen_id}",
            json={"descripcion": "Nueva descripción"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["descripcion"] == "Nueva descripción"


# ==================== Tests de Eliminar Imagen ====================

class TestEliminarImagen:
    """Tests para DELETE /api/imagenes/{id}"""
    
    @patch.dict('os.environ', {'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test==;'})
    def test_eliminar_imagen_exitosa(self, auth_headers, mock_azure_blob):
        """Test: Elimina imagen correctamente."""
        # Crear imagen
        db = TestingSessionLocal()
        usuario = db.query(Usuario).filter(Usuario.email == "test@example.com").first()
        
        imagen = Imagen(
            usuario_id=usuario.id,
            nombre_archivo="test.jpg",
            nombre_blob="uuid-test.jpg",
            url_blob="https://storage.blob.core.windows.net/container/test.jpg",
            container_name="plantitas-imagenes",
            content_type="image/jpeg",
            tamano_bytes=1024
        )
        db.add(imagen)
        db.commit()
        db.refresh(imagen)
        imagen_id = imagen.id
        db.close()
        
        # Eliminar imagen
        response = client.delete(f"/api/imagenes/{imagen_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == imagen_id
        assert data["mensaje"] == "Imagen eliminada exitosamente"
        
        # Verificar que está marcada como eliminada
        db = TestingSessionLocal()
        imagen_eliminada = db.query(Imagen).filter(Imagen.id == imagen_id).first()
        assert imagen_eliminada.is_deleted is True
        db.close()
    
    def test_eliminar_imagen_sin_autenticacion(self):
        """Test: Falla si no está autenticado."""
        response = client.delete("/api/imagenes/1")
        assert response.status_code == 401
    
    @patch.dict('os.environ', {'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test==;'})
    def test_eliminar_imagen_no_existe(self, auth_headers, mock_azure_blob):
        """Test: Falla si imagen no existe."""
        response = client.delete("/api/imagenes/999", headers=auth_headers)
        assert response.status_code == 404
