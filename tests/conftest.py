"""Configuración y fixtures comunes para pytest."""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
import pandas as pd
from datetime import datetime, date

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
def sample_accident_data():
    """Fixture con datos de muestra de accidentes."""
    return [
        (1, 'F001', date(2024, 1, 15), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
        (2, 'F002', date(2024, 1, 16), '09:00', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR')
    ]

@pytest.fixture
def sample_api_data():
    """Fixture con datos de muestra de la API."""
    return [
        {
            'OBJECTID': 1,
            'FORMULARIO': 'F001',
            'CODIGO_ACCIDENTE': 12345,
            'FECHA_OCURRENCIA_ACC': 1640995200000,
            'HORA_OCURRENCIA_ACC': '08:00',
            'ANO_OCURRENCIA_ACC': 2024,
            'MES_OCURRENCIA_ACC': 'ENERO',
            'DIA_OCURRENCIA_ACC': 'LUNES',
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
        }
    ]

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
def sample_dataframe():
    """Fixture con un DataFrame de pandas de muestra."""
    return pd.DataFrame({
        'OBJECTID': [1, 2, 3],
        'FORMULARIO': ['F001', 'F002', 'F003'],
        'FECHA_OCURRENCIA_ACC': [1640995200000, 1641081600000, 1641168000000],
        'LOCALIDAD': ['CHAPINERO', 'USAQUEN', 'SUBA']
    })

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
