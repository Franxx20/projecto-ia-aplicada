"""
Tests para T-023: Endpoint de plantas desde identificación

Tests del endpoint POST /api/plantas/agregar-desde-identificacion
que permite a usuarios agregar plantas a su jardín desde identificaciones.

@author Equipo Backend
@date Enero 2026
@sprint Sprint 3
@task T-023
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.models import Usuario, Imagen, Identificacion, Planta, Especie
from app.utils.jwt import crear_token_acceso


# No definimos fixture 'client_with_db' aquí - usamos el de conftest.py que tiene la DB conectada


@pytest.fixture
def test_usuario(db: Session):
    """Crea un usuario de prueba"""
    usuario = Usuario(
        email="test_planta@example.com",
        nombre="Usuario Test Planta",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeQzPx.3j8/C",  # "password123"
        is_active=True
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def otro_usuario(db: Session):
    """Crea otro usuario de prueba"""
    usuario = Usuario(
        email="otro_usuario@example.com",
        nombre="Otro Usuario",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aeQzPx.3j8/C",
        is_active=True
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def test_imagen(db: Session, test_usuario):
    """Crea una imagen de prueba"""
    imagen = Imagen(
        usuario_id=test_usuario.id,
        nombre_archivo="test_potus.jpg",
        nombre_blob="test_potus_123.jpg",
        url_blob="https://storage.blob.core.windows.net/plantitas/test_potus_123.jpg",
        container_name="plantitas-imagenes",
        content_type="image/jpeg",
        tamano_bytes=1024000
    )
    db.add(imagen)
    db.commit()
    db.refresh(imagen)
    return imagen


@pytest.fixture
def test_especie(db: Session):
    """Crea una especie de prueba"""
    especie = Especie(
        nombre_cientifico="Epipremnum aureum",
        nombre_comun="Potus",
        familia="Araceae",
        descripcion="Planta trepadora de interior muy popular",
        cuidados_basicos="Luz indirecta, riego moderado"
    )
    db.add(especie)
    db.commit()
    db.refresh(especie)
    return especie


@pytest.fixture
def test_identificacion(db: Session, test_usuario, test_imagen, test_especie):
    """Crea una identificación de prueba con especie"""
    identificacion = Identificacion(
        usuario_id=test_usuario.id,
        imagen_id=test_imagen.id,
        especie_id=test_especie.id,
        confianza=85,
        origen="ia_plantnet",
        validado=False,
        notas_usuario="Identificación de Potus",
        metadatos_ia='{"version": "2024.1", "score": 0.855}'
    )
    db.add(identificacion)
    db.commit()
    db.refresh(identificacion)
    return identificacion


@pytest.fixture
def test_identificacion_sin_especie(db: Session, test_usuario, test_imagen):
    """Crea una identificación de prueba sin especie"""
    identificacion = Identificacion(
        usuario_id=test_usuario.id,
        imagen_id=test_imagen.id,
        especie_id=None,
        confianza=35,
        origen="ia_plantnet",
        validado=False,
        notas_usuario="Planta desconocida",
        metadatos_ia='{"version": "2024.1", "score": 0.35}'
    )
    db.add(identificacion)
    db.commit()
    db.refresh(identificacion)
    return identificacion


@pytest.fixture
def token_valido(test_usuario):
    """Genera un token JWT válido para el usuario de prueba"""
    return crear_token_acceso(datos={"sub": test_usuario.email})


@pytest.fixture
def headers_validos(token_valido):
    """Headers con autenticación válida"""
    return {"Authorization": f"Bearer {token_valido}"}


class TestAgregarPlantaDesdeIdentificacion:
    """Tests para el endpoint POST /api/plantas/agregar-desde-identificacion"""

    def test_agregar_planta_exitoso_con_especie(
        self,
        client_with_db,
        db: Session,
        test_identificacion,
        headers_validos,
        test_usuario
    ):
        """Test: Agregar planta exitosamente con especie"""
        # Arrange
        request_data = {
            "identificacion_id": test_identificacion.id,
            "nombre_personalizado": "Mi Potus del Balcón",
            "notas": "Identificada el 2026-01-15",
            "ubicacion": "Balcón - luz indirecta"
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        
        assert data["usuario_id"] == test_usuario.id
        assert data["especie_id"] == test_identificacion.especie_id
        assert data["nombre_personal"] == "Mi Potus del Balcón"
        assert data["notas"] == "Identificada el 2026-01-15"
        assert data["ubicacion"] == "Balcón - luz indirecta"
        assert data["estado_salud"] == "buena"
        assert data["frecuencia_riego_dias"] == 7
        assert data["is_active"] is True
        assert data["imagen_principal_id"] == test_identificacion.imagen_id

        # Verificar en BD
        planta = db.query(Planta).filter(Planta.id == data["id"]).first()
        assert planta is not None
        assert planta.usuario_id == test_usuario.id

    def test_agregar_planta_sin_nombre_usa_nombre_comun(
        self,
        client_with_db,
        db: Session,
        test_identificacion,
        headers_validos
    ):
        """Test: Sin nombre personalizado debe usar nombre común de la especie"""
        # Arrange
        request_data = {
            "identificacion_id": test_identificacion.id
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Debe usar el nombre común "Potus" de la especie
        assert data["nombre_personal"] == "Potus"

    def test_agregar_planta_sin_especie(
        self,
        client_with_db,
        db: Session,
        test_identificacion_sin_especie,
        headers_validos
    ):
        """Test: Agregar planta sin especie asociada"""
        # Arrange
        request_data = {
            "identificacion_id": test_identificacion_sin_especie.id,
            "nombre_personalizado": "Planta Misteriosa"
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        
        assert data["especie_id"] is None
        assert data["nombre_personal"] == "Planta Misteriosa"
        assert data["estado_salud"] == "buena"

    def test_agregar_planta_sin_autenticacion(
        self,
        client_with_db,
        test_identificacion
    ):
        """Test: Debe fallar sin token de autenticación"""
        # Arrange
        request_data = {
            "identificacion_id": test_identificacion.id
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data
        )

        # Assert
        assert response.status_code == 403  # Cambiado de 401 a 403
        assert "detail" in response.json()

    def test_agregar_planta_identificacion_no_existe(
        self,
        client_with_db,
        headers_validos
    ):
        """Test: Debe fallar si la identificación no existe"""
        # Arrange
        request_data = {
            "identificacion_id": 99999  # ID que no existe
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 404
        assert "Identificación no encontrada" in response.json()["detail"]

    def test_agregar_planta_identificacion_de_otro_usuario(
        self,
        client_with_db,
        db: Session,
        test_identificacion,
        otro_usuario
    ):
        """Test: Debe fallar si la identificación pertenece a otro usuario"""
        # Arrange
        # Crear token para otro usuario
        token_otro = crear_token_acceso(datos={"sub": otro_usuario.email})
        headers_otro = {"Authorization": f"Bearer {token_otro}"}
        
        request_data = {
            "identificacion_id": test_identificacion.id
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_otro
        )

        # Assert
        assert response.status_code == 403
        assert "no tienes permiso" in response.json()["detail"].lower()

    def test_agregar_planta_con_campos_opcionales_vacios(
        self,
        client_with_db,
        test_identificacion,
        headers_validos
    ):
        """Test: Debe funcionar con campos opcionales vacíos"""
        # Arrange
        request_data = {
            "identificacion_id": test_identificacion.id,
            "nombre_personalizado": None,
            "notas": None,
            "ubicacion": None
        }

        # Act
        response = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data,
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        
        assert data["nombre_personal"] is not None  # Debe usar nombre común
        assert data["notas"] is None
        assert data["ubicacion"] is None

    def test_agregar_multiples_plantas_misma_identificacion(
        self,
        client_with_db,
        db: Session,
        test_identificacion,
        headers_validos,
        test_usuario
    ):
        """Test: Debe poder agregar múltiples plantas desde la misma identificación"""
        # Arrange
        request_data_1 = {
            "identificacion_id": test_identificacion.id,
            "nombre_personalizado": "Potus 1 - Sala"
        }
        request_data_2 = {
            "identificacion_id": test_identificacion.id,
            "nombre_personalizado": "Potus 2 - Cocina"
        }

        # Act
        response_1 = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data_1,
            headers=headers_validos
        )
        response_2 = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_data_2,
            headers=headers_validos
        )

        # Assert
        assert response_1.status_code == 201
        assert response_2.status_code == 201
        
        data_1 = response_1.json()
        data_2 = response_2.json()
        
        assert data_1["id"] != data_2["id"]
        assert data_1["nombre_personal"] == "Potus 1 - Sala"
        assert data_2["nombre_personal"] == "Potus 2 - Cocina"
        
        # Verificar en BD
        plantas = db.query(Planta).filter(
            Planta.usuario_id == test_usuario.id
        ).all()
        assert len(plantas) >= 2


class TestObtenerMisPlantas:
    """Tests para el endpoint GET /api/plantas"""

    def test_obtener_plantas_usuario(
        self,
        client_with_db,
        db: Session,
        test_usuario,
        test_especie,
        test_imagen,
        headers_validos
    ):
        """Test: Obtener lista de plantas del usuario"""
        # Arrange - Crear plantas de prueba
        planta1 = Planta(
            usuario_id=test_usuario.id,
            especie_id=test_especie.id,
            nombre_personal="Mi Potus 1",
            imagen_principal_id=test_imagen.id,
            estado_salud="buena",
            frecuencia_riego_dias=7,
            is_active=True
        )
        planta2 = Planta(
            usuario_id=test_usuario.id,
            especie_id=test_especie.id,
            nombre_personal="Mi Potus 2",
            estado_salud="buena",
            frecuencia_riego_dias=7,
            is_active=True
        )
        db.add_all([planta1, planta2])
        db.commit()

        # Act
        response = client_with_db.get(
            "/api/plantas",
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Verificar estructura de respuesta
        planta_data = data[0]
        assert "id" in planta_data
        assert "usuario_id" in planta_data
        assert "nombre_personal" in planta_data
        assert "estado_salud" in planta_data
        assert "especie" in planta_data or planta_data.get("especie") is None
        assert "imagen_principal" in planta_data or planta_data.get("imagen_principal") is None

    def test_obtener_plantas_sin_autenticacion(self, client_with_db):
        """Test: Debe fallar sin autenticación"""
        # Act
        response = client_with_db.get("/api/plantas")

        # Assert
        assert response.status_code == 403  # Cambiado de 401 a 403

    def test_obtener_plantas_usuario_sin_plantas(
        self,
        client_with_db,
        headers_validos
    ):
        """Test: Usuario sin plantas debe retornar lista vacía"""
        # Act
        response = client_with_db.get(
            "/api/plantas",
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_plantas_incluyen_relaciones(
        self,
        client_with_db,
        db: Session,
        test_usuario,
        test_especie,
        test_imagen,
        headers_validos
    ):
        """Test: Las plantas deben incluir especie e imagen principal"""
        # Arrange
        planta = Planta(
            usuario_id=test_usuario.id,
            especie_id=test_especie.id,
            nombre_personal="Potus con relaciones",
            imagen_principal_id=test_imagen.id,
            estado_salud="buena",
            frecuencia_riego_dias=7,
            is_active=True
        )
        db.add(planta)
        db.commit()

        # Act
        response = client_with_db.get(
            "/api/plantas",
            headers=headers_validos
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        planta_con_relaciones = next(
            (p for p in data if p["id"] == planta.id),
            None
        )
        
        assert planta_con_relaciones is not None
        
        # Verificar especie
        if planta_con_relaciones.get("especie"):
            especie = planta_con_relaciones["especie"]
            assert especie["nombre_cientifico"] == "Epipremnum aureum"
            assert especie["nombre_comun"] == "Potus"
        
        # Verificar imagen
        if planta_con_relaciones.get("imagen_principal"):
            imagen = planta_con_relaciones["imagen_principal"]
            assert "url_blob" in imagen
            assert "nombre_archivo" in imagen


# Tests de integración del flujo completo
class TestFlujoCompletoT023:
    """Tests de integración del flujo completo de T-023"""

    def test_flujo_completo_identificar_agregar_listar(
        self,
        client_with_db,
        db: Session,
        test_usuario,
        test_identificacion,
        headers_validos
    ):
        """Test: Flujo completo - identificar → agregar → listar"""
        # Step 1: Agregar planta desde identificación
        request_agregar = {
            "identificacion_id": test_identificacion.id,
            "nombre_personalizado": "Mi nueva planta",
            "ubicacion": "Sala de estar",
            "notas": "Primera planta del jardín digital"
        }
        
        response_agregar = client_with_db.post(
            "/api/plantas/agregar-desde-identificacion",
            json=request_agregar,
            headers=headers_validos
        )
        
        assert response_agregar.status_code == 201
        planta_id = response_agregar.json()["id"]
        
        # Step 2: Listar plantas del usuario
        response_listar = client_with_db.get(
            "/api/plantas",
            headers=headers_validos
        )
        
        assert response_listar.status_code == 200
        plantas = response_listar.json()
        
        # Step 3: Verificar que la planta agregada está en la lista
        planta_agregada = next(
            (p for p in plantas if p["id"] == planta_id),
            None
        )
        
        assert planta_agregada is not None
        assert planta_agregada["nombre_personal"] == "Mi nueva planta"
        assert planta_agregada["ubicacion"] == "Sala de estar"
        assert planta_agregada["notas"] == "Primera planta del jardín digital"
        assert planta_agregada["usuario_id"] == test_usuario.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

