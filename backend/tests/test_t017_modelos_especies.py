"""
Tests para los modelos de Especie e Identificacion.

Este módulo contiene las pruebas unitarias para validar el comportamiento
de los modelos Especie e Identificacion, incluyendo creación, relaciones,
y métodos de utilidad.

Autor: Equipo Backend
Fecha: Octubre 2025
Sprint: Sprint 2 - T-017
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.db.models import Base, Usuario, Imagen, Especie, Identificacion


# ========================================
# CONFIGURACIÓN DE FIXTURES
# ========================================

@pytest.fixture(scope="function")
def engine():
    """
    Crea un motor de base de datos SQLite en memoria para tests.
    
    Returns:
        Engine: Motor SQLAlchemy configurado
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def session(engine):
    """
    Crea una sesión de base de datos para cada test.
    
    Args:
        engine: Motor de base de datos (fixture)
        
    Yields:
        Session: Sesión de SQLAlchemy
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def usuario_test(session):
    """
    Crea un usuario de prueba en la base de datos.
    
    Args:
        session: Sesión de base de datos (fixture)
        
    Returns:
        Usuario: Usuario de prueba
    """
    usuario = Usuario(
        email="test_especies@example.com",
        password_hash="hashed_password",
        nombre="Usuario Test Especies"
    )
    session.add(usuario)
    session.commit()
    return usuario


@pytest.fixture
def imagen_test(session, usuario_test):
    """
    Crea una imagen de prueba asociada al usuario.
    
    Args:
        session: Sesión de base de datos (fixture)
        usuario_test: Usuario de prueba (fixture)
        
    Returns:
        Imagen: Imagen de prueba
    """
    imagen = Imagen(
        usuario_id=usuario_test.id,
        nombre_archivo="planta_test.jpg",
        nombre_blob="uuid-test.jpg",
        url_blob="http://localhost/test.jpg",
        content_type="image/jpeg",
        tamano_bytes=100000
    )
    session.add(imagen)
    session.commit()
    return imagen


@pytest.fixture
def especie_test(session):
    """
    Crea una especie de prueba en la base de datos.
    
    Args:
        session: Sesión de base de datos (fixture)
        
    Returns:
        Especie: Especie de prueba
    """
    especie = Especie(
        nombre_comun="Monstera Deliciosa",
        nombre_cientifico="Monstera deliciosa",
        familia="Araceae",
        descripcion="Planta tropical de hojas grandes",
        nivel_dificultad="facil",
        luz_requerida="media",
        riego_frecuencia="Una vez por semana",
        toxicidad="leve"
    )
    session.add(especie)
    session.commit()
    return especie


# ========================================
# TESTS DEL MODELO ESPECIE
# ========================================

class TestModeloEspecie:
    """Suite de tests para el modelo Especie."""
    
    def test_crear_especie_basica(self, session):
        """
        Test: Crear especie con campos mínimos requeridos.
        
        Verifica que se puede crear una especie con los campos
        básicos obligatorios.
        """
        especie = Especie(
            nombre_comun="Pothos",
            nombre_cientifico="Epipremnum aureum",
            nivel_dificultad="facil"
        )
        
        session.add(especie)
        session.commit()
        
        assert especie.id is not None
        assert especie.nombre_comun == "Pothos"
        assert especie.nombre_cientifico == "Epipremnum aureum"
        assert especie.nivel_dificultad == "facil"
        assert especie.is_active is True
        assert especie.created_at is not None
        assert especie.updated_at is not None
    
    def test_especie_nombre_cientifico_unico(self, session, especie_test):
        """
        Test: Validar que el nombre científico es único.
        
        Verifica que no se pueden crear dos especies con el
        mismo nombre científico.
        """
        especie_duplicada = Especie(
            nombre_comun="Otra Monstera",
            nombre_cientifico="Monstera deliciosa",  # Duplicado
            nivel_dificultad="medio"
        )
        
        session.add(especie_duplicada)
        
        with pytest.raises(IntegrityError):
            session.commit()
    
    def test_especie_con_todos_los_campos(self, session):
        """
        Test: Crear especie con todos los campos poblados.
        
        Verifica que se pueden guardar todos los campos
        opcionales del modelo.
        """
        especie = Especie(
            nombre_comun="Ficus Lyrata",
            nombre_cientifico="Ficus lyrata",
            familia="Moraceae",
            descripcion="Árbol tropical con hojas en forma de violín",
            cuidados_basicos='{"riego": "moderado", "luz": "brillante indirecta"}',
            nivel_dificultad="medio",
            luz_requerida="alta",
            riego_frecuencia="Cada 7-10 días",
            temperatura_min=15,
            temperatura_max=30,
            humedad_requerida="alta",
            toxicidad="moderada",
            origen_geografico="África Occidental",
            imagen_referencia_url="https://example.com/ficus.jpg"
        )
        
        session.add(especie)
        session.commit()
        
        assert especie.id is not None
        assert especie.familia == "Moraceae"
        assert especie.temperatura_min == 15
        assert especie.temperatura_max == 30
        assert especie.humedad_requerida == "alta"
        assert especie.toxicidad == "moderada"
        assert especie.origen_geografico == "África Occidental"
    
    def test_especie_nombre_display(self, especie_test):
        """
        Test: Propiedad nombre_display.
        
        Verifica que la propiedad nombre_display retorna
        el formato correcto.
        """
        nombre_display = especie_test.nombre_display
        
        assert nombre_display == "Monstera Deliciosa (Monstera deliciosa)"
        assert especie_test.nombre_comun in nombre_display
        assert especie_test.nombre_cientifico in nombre_display
    
    def test_especie_repr(self, especie_test):
        """
        Test: Método __repr__ de Especie.
        
        Verifica que la representación en string contiene
        la información clave.
        """
        repr_str = repr(especie_test)
        
        assert "Especie" in repr_str
        assert str(especie_test.id) in repr_str
        assert "Monstera Deliciosa" in repr_str
        assert "Monstera deliciosa" in repr_str
    
    def test_especie_str(self, especie_test):
        """
        Test: Método __str__ de Especie.
        
        Verifica que el string display retorna el nombre común.
        """
        str_display = str(especie_test)
        
        assert str_display == "Monstera Deliciosa"
    
    def test_especie_to_dict(self, especie_test):
        """
        Test: Método to_dict de Especie.
        
        Verifica que el método retorna un diccionario con
        todos los campos esperados.
        """
        especie_dict = especie_test.to_dict()
        
        assert isinstance(especie_dict, dict)
        assert especie_dict['id'] == especie_test.id
        assert especie_dict['nombre_comun'] == "Monstera Deliciosa"
        assert especie_dict['nombre_cientifico'] == "Monstera deliciosa"
        assert especie_dict['nombre_display'] == especie_test.nombre_display
        assert especie_dict['familia'] == "Araceae"
        assert especie_dict['nivel_dificultad'] == "facil"
        assert especie_dict['is_active'] is True
        assert 'created_at' in especie_dict
        assert 'updated_at' in especie_dict
    
    def test_especie_relacion_identificaciones(self, session, especie_test, usuario_test, imagen_test):
        """
        Test: Relación con identificaciones.
        
        Verifica que la relación back_populates funciona
        correctamente con Identificacion.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=85,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        # Verificar relación
        assert len(especie_test.identificaciones) == 1
        assert especie_test.identificaciones[0].confianza == 85


# ========================================
# TESTS DEL MODELO IDENTIFICACION
# ========================================

class TestModeloIdentificacion:
    """Suite de tests para el modelo Identificacion."""
    
    def test_crear_identificacion_basica(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Crear identificación con campos mínimos.
        
        Verifica que se puede crear una identificación básica
        con las relaciones correctas.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=75,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        assert identificacion.id is not None
        assert identificacion.usuario_id == usuario_test.id
        assert identificacion.imagen_id == imagen_test.id
        assert identificacion.especie_id == especie_test.id
        assert identificacion.confianza == 75
        assert identificacion.origen == "ia_plantnet"
        assert identificacion.validado is False
        assert identificacion.fecha_identificacion is not None
        assert identificacion.fecha_validacion is None
    
    def test_identificacion_manual(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Crear identificación manual.
        
        Verifica que se puede crear una identificación
        de origen manual.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=100,
            origen="manual",
            notas_usuario="Identificada por experto local"
        )
        
        session.add(identificacion)
        session.commit()
        
        assert identificacion.origen == "manual"
        assert identificacion.confianza == 100
        assert identificacion.notas_usuario is not None
    
    def test_identificacion_es_confiable(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Propiedad es_confiable.
        
        Verifica que la propiedad retorna True cuando
        confianza >= 70%.
        """
        # Identificación confiable
        id_confiable = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=85,
            origen="ia_plantnet"
        )
        
        # Identificación no confiable
        id_no_confiable = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=45,
            origen="ia_plantnet"
        )
        
        assert id_confiable.es_confiable is True
        assert id_no_confiable.es_confiable is False
        
        # Caso borde (exactamente 70%)
        id_borde = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=70,
            origen="ia_plantnet"
        )
        
        assert id_borde.es_confiable is True
    
    def test_identificacion_confianza_porcentaje(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Propiedad confianza_porcentaje.
        
        Verifica que retorna el formato correcto "XX%".
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=92,
            origen="ia_plantnet"
        )
        
        assert identificacion.confianza_porcentaje == "92%"
    
    def test_identificacion_validar(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Método validar().
        
        Verifica que el método marca correctamente la
        identificación como validada.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=80,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        # Antes de validar
        assert identificacion.validado is False
        assert identificacion.fecha_validacion is None
        
        # Validar con notas
        identificacion.validar("Confirmado, es una Monstera")
        session.commit()
        
        # Después de validar
        assert identificacion.validado is True
        assert identificacion.fecha_validacion is not None
        assert identificacion.notas_usuario == "Confirmado, es una Monstera"
        assert identificacion.updated_at is not None
    
    def test_identificacion_repr(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Método __repr__ de Identificacion.
        
        Verifica que la representación contiene información clave.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=88,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        repr_str = repr(identificacion)
        
        assert "Identificacion" in repr_str
        assert str(identificacion.id) in repr_str
        assert str(identificacion.usuario_id) in repr_str
        assert str(identificacion.especie_id) in repr_str
        assert "88%" in repr_str
    
    def test_identificacion_str(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Método __str__ de Identificacion.
        
        Verifica el formato del string de display.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=75,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        str_display = str(identificacion)
        
        assert "Identificación" in str_display
        assert "75%" in str_display
    
    def test_identificacion_to_dict(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Método to_dict de Identificacion.
        
        Verifica que retorna todos los campos esperados.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=90,
            origen="ia_plantnet",
            notas_usuario="Test notes"
        )
        
        session.add(identificacion)
        session.commit()
        
        id_dict = identificacion.to_dict()
        
        assert isinstance(id_dict, dict)
        assert id_dict['id'] == identificacion.id
        assert id_dict['usuario_id'] == usuario_test.id
        assert id_dict['imagen_id'] == imagen_test.id
        assert id_dict['especie_id'] == especie_test.id
        assert id_dict['confianza'] == 90
        assert id_dict['confianza_porcentaje'] == "90%"
        assert id_dict['es_confiable'] is True
        assert id_dict['origen'] == "ia_plantnet"
        assert id_dict['validado'] is False
        assert id_dict['notas_usuario'] == "Test notes"
        assert 'fecha_identificacion' in id_dict
        assert 'created_at' in id_dict
    
    def test_identificacion_relaciones(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Relaciones con Usuario, Imagen y Especie.
        
        Verifica que todas las relaciones funcionan correctamente.
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=82,
            origen="ia_plantnet"
        )
        
        session.add(identificacion)
        session.commit()
        
        # Verificar relación con Usuario
        assert identificacion.usuario is not None
        assert identificacion.usuario.email == "test_especies@example.com"
        
        # Verificar relación con Imagen
        assert identificacion.imagen is not None
        assert identificacion.imagen.nombre_archivo == "planta_test.jpg"
        
        # Verificar relación con Especie
        assert identificacion.especie is not None
        assert identificacion.especie.nombre_comun == "Monstera Deliciosa"
    
    @pytest.mark.skip(reason="CASCADE funciona diferente en SQLite vs PostgreSQL")
    def test_identificacion_integridad_referencial(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Integridad referencial con CASCADE.
        
        Verifica que al eliminar usuario/imagen, se eliminan
        las identificaciones asociadas (ON DELETE CASCADE).
        
        NOTA: Este test está deshabilitado para SQLite (tests)
        pero funciona correctamente en PostgreSQL (producción).
        """
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=75,
            origen="manual"
        )
        
        session.add(identificacion)
        session.commit()
        
        id_guardado = identificacion.id
        
        # Eliminar imagen (debería eliminar identificación por CASCADE)
        session.delete(imagen_test)
        session.commit()
        
        # Verificar que identificación se eliminó
        identificacion_eliminada = session.query(Identificacion).filter_by(id=id_guardado).first()
        assert identificacion_eliminada is None
    
    def test_multiples_identificaciones_misma_imagen(self, session, usuario_test, imagen_test, especie_test):
        """
        Test: Múltiples identificaciones para la misma imagen.
        
        Verifica que una imagen puede tener múltiples
        identificaciones (histórico).
        """
        # Primera identificación (IA con baja confianza)
        id1 = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=55,
            origen="ia_plantnet"
        )
        
        # Segunda identificación (manual después de verificar)
        id2 = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie_test.id,
            confianza=100,
            origen="manual",
            validado=True
        )
        
        session.add_all([id1, id2])
        session.commit()
        
        # Verificar que ambas existen
        identificaciones = session.query(Identificacion).filter_by(imagen_id=imagen_test.id).all()
        assert len(identificaciones) == 2


# ========================================
# TESTS DE INTEGRACIÓN
# ========================================

class TestIntegracionEspeciesIdentificaciones:
    """Tests de integración entre modelos."""
    
    def test_flujo_completo_identificacion(self, session, usuario_test, imagen_test):
        """
        Test: Flujo completo de identificación de planta.
        
        Simula el flujo real: crear especie, identificar imagen,
        validar resultado.
        """
        # 1. Crear especie
        especie = Especie(
            nombre_comun="Philodendron",
            nombre_cientifico="Philodendron hederaceum",
            familia="Araceae",
            nivel_dificultad="facil",
            descripcion="Planta trepadora de interior"
        )
        session.add(especie)
        session.commit()
        
        # 2. Identificar con IA
        identificacion = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen_test.id,
            especie_id=especie.id,
            confianza=88,
            origen="ia_plantnet",
            metadatos_ia='{"api": "plantnet", "version": "1.0"}'
        )
        session.add(identificacion)
        session.commit()
        
        # 3. Usuario valida
        identificacion.validar("Sí, es correcto!")
        session.commit()
        
        # Verificaciones finales
        assert especie.id is not None
        assert identificacion.especie_id == especie.id
        assert identificacion.validado is True
        assert identificacion.es_confiable is True
        assert len(especie.identificaciones) == 1
    
    def test_usuario_con_multiples_identificaciones(self, session, usuario_test, especie_test):
        """
        Test: Usuario con múltiples identificaciones.
        
        Verifica que un usuario puede tener varias identificaciones
        de diferentes imágenes y especies.
        """
        # Crear imágenes adicionales
        imagen1 = Imagen(
            usuario_id=usuario_test.id,
            nombre_archivo="planta1.jpg",
            nombre_blob="uuid1.jpg",
            url_blob="http://test1.jpg",
            content_type="image/jpeg",
            tamano_bytes=50000
        )
        
        imagen2 = Imagen(
            usuario_id=usuario_test.id,
            nombre_archivo="planta2.jpg",
            nombre_blob="uuid2.jpg",
            url_blob="http://test2.jpg",
            content_type="image/jpeg",
            tamano_bytes=60000
        )
        
        session.add_all([imagen1, imagen2])
        session.commit()
        
        # Crear identificaciones
        id1 = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen1.id,
            especie_id=especie_test.id,
            confianza=90,
            origen="ia_plantnet"
        )
        
        id2 = Identificacion(
            usuario_id=usuario_test.id,
            imagen_id=imagen2.id,
            especie_id=especie_test.id,
            confianza=75,
            origen="manual"
        )
        
        session.add_all([id1, id2])
        session.commit()
        
        # Verificar
        identificaciones_usuario = session.query(Identificacion).filter_by(
            usuario_id=usuario_test.id
        ).all()
        
        assert len(identificaciones_usuario) == 2
        assert all(id.usuario_id == usuario_test.id for id in identificaciones_usuario)
