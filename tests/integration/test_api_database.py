"""Tests de integración para la interacción entre API y base de datos."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.models.api_client import ClienteAPI
from src.models.database import GestorBaseDatos
from src.models.update_model import ModeloActualizacion
from src.config.settings import CONFIG_TABLAS

@pytest.mark.integration
class TestIntegracionAPIDatabase:
    """Clase de tests de integración para API y base de datos."""

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_flujo_completo_actualizacion_accidente(self, mock_connect, mock_get):
        """Prueba el flujo completo de actualización desde API hasta BD para tabla Accidente."""
        # Configurar mock de API
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'total': 2,
                'records': [
                    {
                        'OBJECTID': 1001,
                        'FORMULARIO': 'F1001',
                        'CODIGO_ACCIDENTE': 12345,
                        'FECHA_OCURRENCIA_ACC': 1640995200000,
                        'HORA_OCURRENCIA_ACC': '08:00',
                        'ANO_OCURRENCIA_ACC': 2024,
                        'MES_OCURRENCIA_ACC': 'ENERO',
                        'DIA_OCURRENCIA_ACC': 'LUNES',
                        'DIRECCION': 'Calle Test 123',
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
                        'OBJECTID': 1002,
                        'FORMULARIO': 'F1002',
                        'CODIGO_ACCIDENTE': 12346,
                        'FECHA_OCURRENCIA_ACC': 1641081600000,
                        'HORA_OCURRENCIA_ACC': '09:00',
                        'ANO_OCURRENCIA_ACC': 2024,
                        'MES_OCURRENCIA_ACC': 'ENERO',
                        'DIA_OCURRENCIA_ACC': 'MARTES',
                        'DIRECCION': 'Calle Test 456',
                        'GRAVEDAD': 'ILESO',
                        'CLASE_ACC': 'ATROPELLO',
                        'LOCALIDAD': 'USAQUEN',
                        'MUNICIPIO': 'BOGOTA',
                        'FECHA_HORA_ACC': 1641081600000,
                        'LATITUD': '4.6811',
                        'LONGITUD': '-74.0667',
                        'CIV': 456,
                        'PK_CALZADA': 78
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular conteo de registros existentes
        mock_cursor.fetchone.return_value = (1000,)
        mock_cursor.rowcount = 1  # Simular inserción exitosa
        
        # Ejecutar flujo completo
        modelo = ModeloActualizacion()
        resultado = modelo.actualizar_datos('Accidente')
        
        # Verificar resultado
        assert resultado is True
        
        # Verificar que se llamaron los métodos de la API
        assert mock_get.call_count >= 1
        
        # Verificar que se intentó conectar a la base de datos
        mock_connect.assert_called()

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_consulta_y_actualizacion(self, mock_connect, mock_get):
        """Prueba la integración entre consulta y actualización de datos."""
        # Configurar mock de base de datos para consulta
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular datos existentes en la BD
        mock_cursor.fetchall.return_value = [
            (1, 'F001', '2024-01-15', '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO')
        ]
        
        # Ejecutar consulta
        gestor = GestorBaseDatos()
        resultado_consulta = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        
        # Verificar consulta
        assert resultado_consulta is not None
        assert len(resultado_consulta) == 1
        
        # Configurar mock para actualización
        mock_cursor.fetchone.return_value = (1,)  # ObjectID más reciente
        mock_cursor.rowcount = 1
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        resultado_actualizacion = modelo.actualizar_datos('Accidente')
        
        # Verificar que ambos procesos funcionaron
        assert resultado_consulta is not None
        assert resultado_actualizacion is True

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_multiple_tablas(self, mock_connect, mock_get):
        """Prueba la integración entre múltiples tablas durante la actualización."""
        # Configurar mocks para diferentes tablas
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular ObjectID más reciente para cada tabla
        mock_cursor.fetchone.side_effect = [(1000,), (500,), (200,), (300,), (150,)]
        mock_cursor.rowcount = 1
        
        # Configurar respuestas de API para diferentes tablas
        mock_responses = [
            # Accidente
            {'result': {'total': 100, 'count': 10}},
            # Accidente_via
            {'result': {'total': 50, 'count': 5}},
            # Causa
            {'result': {'total': 20, 'count': 2}},
            # AccidenteVehiculo
            {'result': {'total': 30, 'count': 3}},
            # ActorVial
            {'result': {'total': 15, 'count': 1}}
        ]
        
        mock_response = Mock()
        mock_response.json.side_effect = mock_responses
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Ejecutar actualización para todas las tablas
        modelo = ModeloActualizacion()
        
        tablas = ['Accidente', 'Accidente_via', 'Causa', 'AccidenteVehiculo', 'ActorVial']
        resultados = {}
        
        for tabla in tablas:
            resultados[tabla] = modelo.actualizar_datos(tabla)
        
        # Verificar que todas las actualizaciones fueron exitosas
        for tabla, resultado in resultados.items():
            assert resultado is True, f"Fallo en tabla {tabla}"

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_manejo_errores_cascada(self, mock_connect, mock_get):
        """Prueba el manejo de errores en cascada durante la integración."""
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular error en la segunda tabla
        mock_cursor.fetchone.side_effect = [(1000,), Exception("DB error")]
        mock_cursor.rowcount = 1
        
        # Configurar respuestas de API
        mock_response = Mock()
        mock_response.json.return_value = {'result': {'total': 100, 'count': 10}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        
        # Primera tabla debería funcionar
        resultado1 = modelo.actualizar_datos('Accidente')
        assert resultado1 is True
        
        # Segunda tabla debería fallar
        resultado2 = modelo.actualizar_datos('Accidente_via')
        assert resultado2 is False

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_datos_consistencia(self, mock_connect, mock_get):
        """Prueba la consistencia de datos entre API y base de datos."""
        # Configurar mock de API con datos específicos
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'total': 1,
                'count': 1,
                'features': [{
                    'attributes': {
                        'OBJECTID': 9999,
                        'FORMULARIO': 'F9999',
                        'CODIGO_ACCIDENTE': 99999,
                        'FECHA_OCURRENCIA_ACC': 1640995200000,
                        'LOCALIDAD': 'TEST_LOCALIDAD'
                    }
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (9998,)  # ObjectID anterior
        mock_cursor.rowcount = 1
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        resultado = modelo.actualizar_datos('Accidente')
        
        # Verificar que se procesó correctamente
        assert resultado is True
        
        # Verificar que se llamó la inserción con los datos correctos
        mock_cursor.execute.assert_called()
        
        # Obtener los argumentos de la llamada
        args, kwargs = mock_cursor.execute.call_args
        sql_query = args[0]
        values = args[1]
        
        # Verificar que la consulta SQL es correcta
        assert 'INSERT INTO' in sql_query
        assert 'accidente' in sql_query.lower()
        
        # Verificar que los valores coinciden con los datos de la API
        assert values[0] == 9999  # OBJECTID
        assert values[1] == 'F9999'  # FORMULARIO

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_transacciones_atomicas(self, mock_connect, mock_get):
        """Prueba que las transacciones sean atómicas durante la integración."""
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular error después de algunas inserciones
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.execute.side_effect = [None, None, Exception("Insert error")]
        mock_cursor.rowcount = 1
        
        # Configurar respuesta de API
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'total': 3,
                'count': 3,
                'features': [
                    {'attributes': {'OBJECTID': i}} for i in range(1, 4)
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        resultado = modelo.actualizar_datos('Accidente')
        
        # Verificar que falló
        assert resultado is False
        
        # Verificar que se hizo rollback
        mock_connection.rollback.assert_called()

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_concurrencia_consultas(self, mock_connect, mock_get):
        """Prueba la concurrencia de consultas durante la integración."""
        import threading
        import time
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular datos de consulta
        mock_cursor.fetchall.return_value = [
            (1, 'F001', '2024-01-15', '08:00', 'CHAPINERO')
        ]
        
        # Función para ejecutar consultas concurrentes
        def ejecutar_consulta():
            gestor = GestorBaseDatos()
            return gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        
        # Ejecutar múltiples consultas en paralelo
        threads = []
        resultados = []
        
        for i in range(5):
            thread = threading.Thread(target=lambda: resultados.append(ejecutar_consulta()))
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()
        
        # Verificar que todas las consultas se ejecutaron correctamente
        assert len(resultados) == 5
        for resultado in resultados:
            assert resultado is not None
            assert len(resultado) == 1

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_manejo_timeout_api(self, mock_connect, mock_get):
        """Prueba el manejo de timeouts de la API durante la integración."""
        import requests
        
        # Simular timeout en la API
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1000,)
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        resultado = modelo.actualizar_datos('Accidente')
        
        # Verificar que falló por timeout
        assert resultado is False

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_integracion_validacion_datos_cruzada(self, mock_connect, mock_get):
        """Prueba la validación cruzada de datos entre API y base de datos."""
        # Configurar mock de API
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'total': 1,
                'count': 1,
                'features': [{
                    'attributes': {
                        'OBJECTID': 8888,
                        'FORMULARIO': 'F8888',
                        'CODIGO_ACCIDENTE': 88888,
                        'FECHA_OCURRENCIA_ACC': 1640995200000,
                        'LOCALIDAD': 'TEST_LOCALIDAD'
                    }
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (8887,)  # ObjectID anterior
        mock_cursor.rowcount = 1
        
        # Ejecutar actualización
        modelo = ModeloActualizacion()
        resultado = modelo.actualizar_datos('Accidente')
        
        # Verificar que se procesó correctamente
        assert resultado is True
        
        # Simular consulta posterior para verificar consistencia
        mock_cursor.fetchall.return_value = [
            (8888, 'F8888', '2022-01-01', '08:00', 'TEST_LOCALIDAD')
        ]
        
        gestor = GestorBaseDatos()
        resultado_consulta = gestor.obtener_siniestros_por_fecha('2022-01-01', '2022-01-01')
        
        # Verificar que los datos consultados coinciden con los insertados
        assert resultado_consulta is not None
        assert len(resultado_consulta) == 1
        assert resultado_consulta[0][0] == 8888  # OBJECTID
        assert resultado_consulta[0][1] == 'F8888'  # FORMULARIO
        assert resultado_consulta[0][4] == 'TEST_LOCALIDAD'  # LOCALIDAD
