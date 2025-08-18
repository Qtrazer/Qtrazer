"""Fixtures con datos de prueba específicos para Qtrazer."""

import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import Mock

@pytest.fixture
def datos_accidentes_completos():
    """Fixture con datos completos de accidentes para testing."""
    return [
        {
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTE': 12345,
            'FECHA_OCURRENCIA_ACC': 1640995200000,  # 2022-01-01
            'HORA_OCURRENCIA_ACC': '08:00',
            'ANO_OCURRENCIA_ACC': 2022,
            'MES_OCURRENCIA_ACC': 'ENERO',
            'DIA_OCURRENCIA_ACC': 'SABADO',
            'DIRECCION': 'Calle 123 #45-67',
            'GRAVEDAD': 'HERIDO',
            'CLASE_ACC': 'CHOQUE',
            'LOCALIDAD': 'CHAPINERO',
            'MUNICIPIO': 'BOGOTA',
            'FECHA_HORA_ACC': 1640995200000,
            'LATITUD': '4.6711',
            'LONGITUD': '-74.0567',
            'CIV': 123,
            'PK_CALZADA': 45
        },
        {
            'OBJECTID': 2,
            'FORMULARIO': 'F002',
            'CODIGO_ACCIDENTE': 12346,
            'FECHA_OCURRENCIA_ACC': 1641081600000,  # 2022-01-02
            'HORA_OCURRENCIA_ACC': '09:00',
            'ANO_OCURRENCIA_ACC': 2022,
            'MES_OCURRENCIA_ACC': 'ENERO',
            'DIA_OCURRENCIA_ACC': 'DOMINGO',
            'DIRECCION': 'Carrera 78 #90-12',
            'GRAVEDAD': 'ILESO',
            'CLASE_ACC': 'ATROPELLO',
            'LOCALIDAD': 'USAQUEN',
            'MUNICIPIO': 'BOGOTA',
            'FECHA_HORA_ACC': 1641081600000,
            'LATITUD': '4.6811',
            'LONGITUD': '-74.0667',
            'CIV': 456,
            'PK_CALZADA': 78
        },
        {
            'OBJECTID': 3,
            'FORMULARIO': 'F003',
            'CODIGO_ACCIDENTE': 12347,
            'FECHA_OCURRENCIA_ACC': 1641168000000,  # 2022-01-03
            'HORA_OCURRENCIA_ACC': '14:30',
            'ANO_OCURRENCIA_ACC': 2022,
            'MES_OCURRENCIA_ACC': 'ENERO',
            'DIA_OCURRENCIA_ACC': 'LUNES',
            'DIRECCION': 'Avenida 15 #23-45',
            'GRAVEDAD': 'MUERTO',
            'CLASE_ACC': 'VOLCAMIENTO',
            'LOCALIDAD': 'SUBA',
            'MUNICIPIO': 'BOGOTA',
            'FECHA_HORA_ACC': 1641168000000,
            'LATITUD': '4.6911',
            'LONGITUD': '-74.0767',
            'CIV': 789,
            'PK_CALZADA': 123
        }
    ]

@pytest.fixture
def datos_actor_vial():
    """Fixture con datos de actores viales para testing."""
    return [
        {
            'CONDICION_A': 'CONDUCTOR',
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTADO': 1001,
            'CODIGO_VICTIMA': 2001,
            'CODIGO_VEHICULO': 3001,
            'CONDICION': 'CONDUCTOR',
            'ESTADO': 'HERIDO',
            'MUERTE_POSTERIOR': 'NO',
            'FECHA_POSTERIOR_MUERTE': None,
            'GENERO': 'MASCULINO',
            'FECHA_NACIMIENTO': 1640995200000,  # 2022-01-01
            'EDAD': 25,
            'CODIGO': 1
        },
        {
            'CONDICION_A': 'PEATON',
            'OBJECTID': 2,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTADO': 1002,
            'CODIGO_VICTIMA': 2002,
            'CODIGO_VEHICULO': 0,
            'CONDICION': 'PEATON',
            'ESTADO': 'ILESO',
            'MUERTE_POSTERIOR': 'NO',
            'FECHA_POSTERIOR_MUERTE': None,
            'GENERO': 'FEMENINO',
            'FECHA_NACIMIENTO': 1641081600000,  # 2022-01-02
            'EDAD': 30,
            'CODIGO': 2
        }
    ]

@pytest.fixture
def datos_vehiculos():
    """Fixture con datos de vehículos para testing."""
    return [
        {
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'PLACA': 'ABC123',
            'CODIGO_VEHICULO': 3001,
            'CLASE': 'AUTOMOVIL',
            'SERVICIO': 'PARTICULAR',
            'MODALIDAD': 'PRIVADO',
            'ENFUGA': 'NO',
            'CODIGO': 1
        },
        {
            'OBJECTID': 2,
            'FORMULARIO': 'F002',
            'PLACA': 'XYZ789',
            'CODIGO_VEHICULO': 3002,
            'CLASE': 'MOTOCICLETA',
            'SERVICIO': 'PARTICULAR',
            'MODALIDAD': 'PRIVADO',
            'ENFUGA': 'NO',
            'CODIGO': 2
        }
    ]

@pytest.fixture
def datos_causas():
    """Fixture con datos de causas de accidentes para testing."""
    return [
        {
            'CODIGO_AC_VH': 4001,
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTE': 12345,
            'CODIGO_VEHICULO': 3001,
            'CODIGO_CAUSA': 5001,
            'NOMBRE': 'EXCESO VELOCIDAD',
            'TIPO': 'CONDUCTOR',
            'DESCRIPCION2': 'Velocidad superior a la permitida',
            'TIPO_CAUSA': 'HUMANO',
            'CODIGO': 1
        },
        {
            'CODIGO_AC_VH': 4002,
            'OBJECTID': 2,
            'FORMULARIO': 'F002',
            'CODIGO_ACCIDENTE': 12346,
            'CODIGO_VEHICULO': 3002,
            'CODIGO_CAUSA': 5002,
            'NOMBRE': 'NO RESPETAR SEÑAL',
            'TIPO': 'CONDUCTOR',
            'DESCRIPCION2': 'No respetar señal de tránsito',
            'TIPO_CAUSA': 'HUMANO',
            'CODIGO': 2
        }
    ]

@pytest.fixture
def datos_vias():
    """Fixture con datos de vías para testing."""
    return [
        {
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTE': 12345,
            'CODIGO_VIA': 6001,
            'GEOMETRICA_A': 'RECTA',
            'GEOMETRICA_B': 'PLANA',
            'GEOMETRICA_C': 'SECA',
            'UTILIZACION': 'URBANA',
            'CALZADAS': 2,
            'CARRILES': 4,
            'MATERIAL': 'ASFALTO',
            'ESTADO': 'BUENO',
            'CONDICIONES': 'SECA',
            'ILUMINACION_A': 'SI',
            'ILUMINACION_B': 'FUNCIONANDO',
            'AGENTE_TRANSITO': 'NO',
            'SEMAFORO': 'SI',
            'VISUAL': 'BUENA',
            'CODIGO': 1
        }
    ]

@pytest.fixture
def datos_consulta_completa():
    """Fixture con datos de consulta completa para testing."""
    return [
        (1, 'F001', date(2022, 1, 1), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
        (2, 'F002', date(2022, 1, 2), '09:00', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR'),
        (3, 'F003', date(2022, 1, 3), '14:30', 'SUBA', 'AUTOMOVIL', 'DEF456', 'CONDUCTOR', 1, 0, 0, 'MUERTO', 'MASCULINO', 45, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'MALO')
    ]

@pytest.fixture
def mock_database_connection():
    """Fixture para simular una conexión a base de datos."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.fixture
def mock_api_response():
    """Fixture para simular respuestas de API."""
    return {
        'result': {
            'total': 100,
            'records': [
                {
                    'OBJECTID': 1,
                    'FORMULARIO': 'F001',
                    'CODIGO_ACCIDENTE': 12345,
                    'FECHA_OCURRENCIA_ACC': 1640995200000,
                    'HORA_OCURRENCIA_ACC': '08:00',
                    'LOCALIDAD': 'CHAPINERO',
                    'DIRECCION': 'Calle 123 #45-67'
                },
                {
                    'OBJECTID': 2,
                    'FORMULARIO': 'F002',
                    'CODIGO_ACCIDENTE': 12346,
                    'FECHA_OCURRENCIA_ACC': 1641081600000,
                    'HORA_OCURRENCIA_ACC': '09:00',
                    'LOCALIDAD': 'USAQUEN',
                    'DIRECCION': 'Carrera 78 #90-12'
                }
            ]
        }
    }

@pytest.fixture
def sample_dataframe():
    """Fixture con un DataFrame de pandas de muestra."""
    return pd.DataFrame({
        'OBJECTID': [1, 2, 3],
        'FORMULARIO': ['F001', 'F002', 'F003'],
        'FECHA_OCURRENCIA_ACC': [1640995200000, 1641081600000, 1641168000000],
        'LOCALIDAD': ['CHAPINERO', 'USAQUEN', 'SUBA']
    })

@pytest.fixture
def mock_settings():
    """Fixture para simular la configuración de la aplicación."""
    return {
        'PARAMETROS_BD': {
            'dbname': 'test_siniestros',
            'user': 'test_user',
            'password': 'test_password',
            'host': 'localhost',
            'port': '5432'
        },
        'CONFIG_TABLAS': {
            'Accidente': {
                'nombre_tabla': 'accidente',
                'columnas': [
                    'objectid', 'formulario', 'codigo_accidente', 'fecha_ocurrencia_acc',
                    'hora_ocurrencia_acc', 'ano_ocurrencia_acc', 'mes_ocurrencia_acc',
                    'dia_ocurrencia_acc', 'direccion', 'gravedad', 'clase_acc',
                    'localidad', 'municipio', 'fecha_hora_acc', 'latitud', 'longitud',
                    'civ', 'pk_calzada'
                ]
            }
        },
        'API_URLS': {
            'Accidente': 'https://test.api.com/accidente'
        }
    }

@pytest.fixture
def mock_requests_response():
    """Fixture para simular respuestas de requests."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'result': {
            'total': 100,
            'records': []
        }
    }
    mock_response.raise_for_status.return_value = None
    return mock_response

@pytest.fixture
def mock_tkinter_root():
    """Fixture para simular la ventana raíz de Tkinter."""
    mock_root = Mock()
    mock_root.title = Mock()
    mock_root.geometry = Mock()
    mock_root.minsize = Mock()
    mock_root.protocol = Mock()
    mock_root.after = Mock()
    mock_root.update_idletasks = Mock()
    return mock_root

@pytest.fixture
def mock_controlador():
    """Fixture para simular el controlador principal."""
    mock_controlador = Mock()
    mock_controlador.consultar_siniestros = Mock()
    mock_controlador.actualizar_datos = Mock()
    mock_controlador.obtener_resultados_consulta = Mock()
    return mock_controlador

@pytest.fixture
def datos_fechas_variadas():
    """Fixture con fechas variadas para testing de filtros temporales."""
    return [
        date(2022, 1, 1),   # Año nuevo
        date(2022, 1, 15),  # Mitad de mes
        date(2022, 2, 14),  # San Valentín
        date(2022, 6, 15),  # Mitad de año
        date(2022, 12, 25), # Navidad
        date(2022, 12, 31)  # Fin de año
    ]

@pytest.fixture
def datos_localidades_bogota():
    """Fixture con localidades de Bogotá para testing."""
    return [
        'CHAPINERO',
        'USAQUEN',
        'SUBA',
        'ENGATIVA',
        'KENNEDY',
        'PUENTE ARANDA',
        'CANDELARIA',
        'SANTA FE',
        'TEUSAQUILLO',
        'BARRIOS UNIDOS',
        'FONTIBON',
        'BOSA',
        'CIUDAD BOLIVAR',
        'TUNJUELITO',
        'RAFAEL URIBE URIBE',
        'ANTONIO NARIÑO',
        'PUENTE ARANDA',
        'LOS MARTIRES',
        'SAN CRISTOBAL',
        'SUMAPAZ'
    ]

@pytest.fixture
def datos_tipos_vehiculos():
    """Fixture con tipos de vehículos para testing."""
    return [
        'AMBULACIA',
        'AUTOMOVIL',
        'BICICLETA',
        'BICITAXI',
        'BUS',
        'BUS ALIMENTADOR',
        'BUS ARTICULADO',
        'BUSETA',
        'CAMION, FURGON',
        'CAMIONETA',
        'CAMPERO',
        'CUATRIMOTO',
        'M. AGRICOLA',
        'M. INDUSTRIAL',
        'METRO',
        'MICROBUS',
        'MOTOCARRO',
        'MOTOCICLETA',
        'MOTOCICLO',
        'MOTOTRICICLO',
        'NO IDENTIFICADO',
        'OTRO',
        'REMOLQUE',
        'SEMI-REMOLQUE',
        'TRACCION ANIMAL',
        'TRACTOCAMION',
        'TREN',
        'VOLQUETA'
    ]

@pytest.fixture
def datos_estados_victimas():
    """Fixture con estados de víctimas para testing."""
    return [
        'HERIDO',
        'ILESO',
        'MUERTO'
    ]

@pytest.fixture
def datos_causantes_accidentes():
    """Fixture con causantes de accidentes para testing."""
    return [
        'CONDUCTOR',
        'PASAJERO',
        'PEATON',
        'VEHICULO',
        'VIA'
    ]
