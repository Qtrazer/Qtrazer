"""Tests unitarios para el modelo de actualización."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import psycopg2
from src.models.update_model import ModeloActualizacion
from src.config.settings import CONFIG_TABLAS, CAMPOS_API, API_URLS

class TestModeloActualizacion:
    """Clase de tests para ModeloActualizacion."""

    def test_init(self):
        """Prueba la inicialización del modelo de actualización."""
        modelo = ModeloActualizacion()
        assert modelo.MAX_RETRIES == 3
        assert modelo.RETRY_DELAY == 5
        assert modelo.PAGE_SIZE == 1000
        assert modelo.REQUEST_DELAY == 1
        assert 'LUNES' in modelo.DIAS
        assert modelo.DIAS['LUNES'] == 1

    def test_convertir_dia_a_numero(self):
        """Prueba la conversión de nombres de días a números."""
        modelo = ModeloActualizacion()
        
        # Casos válidos
        assert modelo.convertir_dia_a_numero('LUNES') == 1
        assert modelo.convertir_dia_a_numero('MARTES') == 2
        assert modelo.convertir_dia_a_numero('MIERCOLES') == 3
        assert modelo.convertir_dia_a_numero('JUEVES') == 4
        assert modelo.convertir_dia_a_numero('VIERNES') == 5
        assert modelo.convertir_dia_a_numero('SABADO') == 6
        assert modelo.convertir_dia_a_numero('DOMINGO') == 7
        
        # Casos inválidos
        assert modelo.convertir_dia_a_numero('INVALIDO') == 0
        assert modelo.convertir_dia_a_numero('') == 0
        assert modelo.convertir_dia_a_numero(None) == 0
        assert modelo.convertir_dia_a_numero(123) == 0

    def test_convertir_dia_a_numero_case_insensitive(self):
        """Prueba que la conversión sea insensible a mayúsculas/minúsculas."""
        modelo = ModeloActualizacion()
        
        assert modelo.convertir_dia_a_numero('lunes') == 1
        assert modelo.convertir_dia_a_numero('Lunes') == 1
        assert modelo.convertir_dia_a_numero('LUNES') == 1

    def test_formatear_fechas(self, sample_dataframe):
        """Prueba el formateo correcto de fechas."""
        modelo = ModeloActualizacion()
        
        # Crear DataFrame con fechas en milisegundos
        df = pd.DataFrame({
            'FECHA_OCURRENCIA_ACC': [1640995200000, 1641081600000],  # 2022-01-01, 2022-01-02
            'FECHA_HORA_ACC': [1640995200000, 1641081600000],
            'FECHA_POSTERIOR_MUERTE': [1640995200000, 1641081600000]
        })
        
        resultado = modelo.formatear_fechas(df)
        
        # Verificar formateo de fechas
        assert resultado['FECHA_OCURRENCIA_ACC'].iloc[0] == '2022-01-01'
        assert resultado['FECHA_OCURRENCIA_ACC'].iloc[1] == '2022-01-02'
        assert resultado['FECHA_HORA_ACC'].iloc[0] == '2022-01-01 00:00:00'
        assert resultado['FECHA_POSTERIOR_MUERTE'].iloc[0] == '2022-01-01'

    def test_formatear_fechas_con_nan(self):
        """Prueba el formateo de fechas con valores NaN."""
        modelo = ModeloActualizacion()
        
        df = pd.DataFrame({
            'FECHA_OCURRENCIA_ACC': [1640995200000, None, 1641081600000],
            'FECHA_HORA_ACC': [1640995200000, 1641081600000, None]
        })
        
        resultado = modelo.formatear_fechas(df)
        
        # Verificar que los NaN se convirtieron a None
        assert resultado['FECHA_OCURRENCIA_ACC'].iloc[1] is None
        assert resultado['FECHA_HORA_ACC'].iloc[2] is None

    def test_formatear_fechas_error_conversion(self):
        """Prueba el manejo de errores en la conversión de fechas."""
        modelo = ModeloActualizacion()
        
        # DataFrame con fechas inválidas
        df = pd.DataFrame({
            'FECHA_OCURRENCIA_ACC': ['fecha_invalida', 1640995200000],
            'FECHA_HORA_ACC': ['hora_invalida', 1641081600000]
        })
        
        # No debería generar error, solo advertencia
        resultado = modelo.formatear_fechas(df)
        assert resultado is not None

    @patch('psycopg2.connect')
    def test_insertar_registros_exitoso(self, mock_connect, sample_dataframe):
        """Prueba la inserción exitosa de registros."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simular inserción exitosa
        
        modelo = ModeloActualizacion()
        resultado = modelo.insertar_registros(
            sample_dataframe,
            'Accidente',
            lambda msg, pct: None  # Callback vacío
        )
        
        assert resultado is True
        mock_connection.commit.assert_called()

    @patch('psycopg2.connect')
    def test_insertar_registros_error_conexion(self, mock_connect):
        """Prueba el manejo de errores de conexión en inserción."""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        modelo = ModeloActualizacion()
        df = pd.DataFrame({'OBJECTID': [1, 2, 3]})
        
        resultado = modelo.insertar_registros(df, 'Accidente')
        
        assert resultado is False

    @patch('psycopg2.connect')
    def test_insertar_registros_error_insercion(self, mock_connect):
        """Prueba el manejo de errores en la inserción."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Insert error")
        
        modelo = ModeloActualizacion()
        df = pd.DataFrame({'OBJECTID': [1, 2, 3]})
        
        resultado = modelo.insertar_registros(df, 'Accidente')
        
        assert resultado is False

    @patch('psycopg2.connect')
    def test_insertar_registros_con_callback_progreso(self, mock_connect, sample_dataframe):
        """Prueba la inserción con callback de progreso."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        
        callback_calls = []
        def callback_progreso(mensaje, porcentaje):
            callback_calls.append((mensaje, porcentaje))
        
        modelo = ModeloActualizacion()
        resultado = modelo.insertar_registros(
            sample_dataframe,
            'Accidente',
            callback_progreso
        )
        
        # Verificar que se llamó el callback
        assert len(callback_calls) > 0
        assert resultado is True

    @patch('requests.get')
    def test_get_total_records_exitoso(self, mock_get):
        """Prueba la obtención exitosa del total de registros."""
        mock_response = Mock()
        mock_response.json.return_value = {'count': 1500}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        modelo = ModeloActualizacion()
        total = modelo.get_total_records('https://test.api.com/accidente')
        
        assert total == 1500

    @patch('requests.get')
    def test_get_total_records_error(self, mock_get):
        """Prueba el manejo de errores al obtener total de registros."""
        mock_get.side_effect = Exception("API error")
        
        modelo = ModeloActualizacion()
        total = modelo.get_total_records('https://test.api.com/accidente')
        
        assert total == 0

    @patch('psycopg2.connect')
    def test_get_latest_objectid_exitoso(self, mock_connect):
        """Prueba la obtención exitosa del ObjectID más reciente."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1000,)
        
        modelo = ModeloActualizacion()
        latest_id = modelo.get_latest_objectid('Accidente')
        
        assert latest_id == 1000

    @patch('psycopg2.connect')
    def test_get_latest_objectid_error(self, mock_connect):
        """Prueba el manejo de errores al obtener ObjectID más reciente."""
        mock_connect.side_effect = Exception("DB error")
        
        modelo = ModeloActualizacion()
        latest_id = modelo.get_latest_objectid('Accidente')
        
        assert latest_id is None

    @patch('psycopg2.connect')
    def test_get_latest_objectid_sin_registros(self, mock_connect):
        """Prueba la obtención de ObjectID cuando no hay registros."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (None,)
        
        modelo = ModeloActualizacion()
        latest_id = modelo.get_latest_objectid('Accidente')
        
        assert latest_id is None

    @patch('requests.get')
    def test_get_new_records_exitoso(self, mock_get):
        """Prueba la obtención exitosa de nuevos registros."""
        # Primera llamada para obtener total
        mock_response1 = Mock()
        mock_response1.json.return_value = {'count': 100}
        mock_response1.raise_for_status.return_value = None
        
        # Segunda llamada para obtener registros
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            'features': [
                {'attributes': {'OBJECTID': i, 'FORMULARIO': f'F{i:03d}'}} 
                for i in range(1, 101)
            ]
        }
        mock_response2.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        modelo = ModeloActualizacion()
        registros = modelo.get_new_records(
            'https://test.api.com/accidente',
            0,
            ['OBJECTID', 'FORMULARIO']
        )
        
        assert len(registros) == 100
        assert registros[0]['OBJECTID'] == 1
        assert registros[99]['OBJECTID'] == 100

    @patch('requests.get')
    def test_get_new_records_con_reintentos(self, mock_get):
        """Prueba el comportamiento de reintentos en caso de fallos."""
        # Simular fallo en primera llamada, éxito en segunda
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = Exception("Temporary error")
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {'count': 50}
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        modelo = ModeloActualizacion()
        registros = modelo.get_new_records(
            'https://test.api.com/accidente',
            0,
            ['OBJECTID']
        )
        
        # Verificar que se realizaron reintentos
        assert mock_get.call_count >= 2

    @patch('requests.get')
    def test_get_new_records_sin_nuevos(self, mock_get):
        """Prueba el caso cuando no hay nuevos registros."""
        mock_response = Mock()
        mock_response.json.return_value = {'count': 0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        modelo = ModeloActualizacion()
        registros = modelo.get_new_records(
            'https://test.api.com/accidente',
            1000,
            ['OBJECTID']
        )
        
        assert registros == []

    @patch('requests.get')
    def test_actualizar_datos_exitoso(self, mock_get):
        """Prueba la actualización exitosa de datos."""
        # Mock para get_total_records
        mock_response1 = Mock()
        mock_response1.json.return_value = {'count': 100}
        mock_response1.raise_for_status.return_value = None
        
        # Mock para get_new_records
        mock_response2 = Mock()
        mock_response2.json.return_value = {'count': 10}
        mock_response2.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        with patch.object(ModeloActualizacion, 'get_latest_objectid', return_value=1000), \
             patch.object(ModeloActualizacion, 'get_new_records', return_value=[{'OBJECTID': 1001}]), \
             patch.object(ModeloActualizacion, 'insertar_registros', return_value=True):
            
            modelo = ModeloActualizacion()
            resultado = modelo.actualizar_datos('Accidente')
            
            assert resultado is True

    @patch('requests.get')
    def test_actualizar_datos_sin_nuevos(self, mock_get):
        """Prueba la actualización cuando no hay nuevos datos."""
        mock_response = Mock()
        mock_response.json.return_value = {'count': 100}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(ModeloActualizacion, 'get_latest_objectid', return_value=1000), \
             patch.object(ModeloActualizacion, 'get_new_records', return_value=[]):
            
            modelo = ModeloActualizacion()
            resultado = modelo.actualizar_datos('Accidente')
            
            assert resultado is True

    @patch('requests.get')
    def test_actualizar_datos_error_insercion(self, mock_get):
        """Prueba el manejo de errores en la inserción durante actualización."""
        mock_response = Mock()
        mock_response.json.return_value = {'count': 100}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch.object(ModeloActualizacion, 'get_latest_objectid', return_value=1000), \
             patch.object(ModeloActualizacion, 'get_new_records', return_value=[{'OBJECTID': 1001}]), \
             patch.object(ModeloActualizacion, 'insertar_registros', return_value=False):
            
            modelo = ModeloActualizacion()
            resultado = modelo.actualizar_datos('Accidente')
            
            assert resultado is False

    def test_mapeo_columnas_tablas(self):
        """Prueba que el mapeo de columnas sea correcto para todas las tablas."""
        modelo = ModeloActualizacion()
        
        # Verificar que todas las tablas configuradas tienen mapeo
        tablas_configuradas = ['Accidente', 'Accidente_via', 'Causa', 'AccidenteVehiculo', 'ActorVial']
        
        for tabla in tablas_configuradas:
            # Crear DataFrame de prueba
            df = pd.DataFrame({'OBJECTID': [1]})
            
            # No debería generar error
            try:
                modelo.insertar_registros(df, tabla)
            except Exception as e:
                # Solo debería fallar por conexión, no por mapeo
                assert "connection" in str(e).lower() or "psycopg2" in str(e).lower()
