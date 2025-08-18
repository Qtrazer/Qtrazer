"""Tests unitarios para el gestor de base de datos."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from src.models.database import GestorBaseDatos
from src.config.settings import PARAMETROS_BD, CONFIG_TABLAS

class TestGestorBaseDatos:
    """Clase de tests para GestorBaseDatos."""

    def test_init(self):
        """Prueba la inicialización del gestor de base de datos."""
        gestor = GestorBaseDatos()
        assert gestor.conexion is None
        assert gestor.cursor is None

    @patch('psycopg2.connect')
    def test_conectar_exitoso(self, mock_connect):
        """Prueba la conexión exitosa a la base de datos."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        gestor = GestorBaseDatos()
        resultado = gestor.conectar()
        
        # Verificar conexión
        assert resultado is True
        assert gestor.conexion == mock_connection
        assert gestor.cursor == mock_cursor
        
        # Verificar que se llamó psycopg2.connect con los parámetros correctos
        mock_connect.assert_called_once_with(
            dbname=PARAMETROS_BD['dbname'],
            user=PARAMETROS_BD['user'],
            password=PARAMETROS_BD['password'],
            host=PARAMETROS_BD['host'],
            port=PARAMETROS_BD['port']
        )

    @patch('psycopg2.connect')
    def test_conectar_error_operacional(self, mock_connect):
        """Prueba el manejo de errores operacionales de conexión."""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        gestor = GestorBaseDatos()
        with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
            gestor.conectar()

    @patch('psycopg2.connect')
    def test_conectar_error_generico(self, mock_connect):
        """Prueba el manejo de errores genéricos de conexión."""
        mock_connect.side_effect = Exception("Generic error")
        
        gestor = GestorBaseDatos()
        with pytest.raises(Exception, match="Error al conectar a la base de datos"):
            gestor.conectar()

    @patch('psycopg2.connect')
    def test_conectar_error_timeout(self, mock_connect):
        """Prueba el manejo de errores de timeout."""
        mock_connect.side_effect = psycopg2.OperationalError("timeout expired")
        
        gestor = GestorBaseDatos()
        with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
            gestor.conectar()

    def test_desconectar_con_conexion(self):
        """Prueba la desconexión cuando hay una conexión activa."""
        gestor = GestorBaseDatos()
        gestor.conexion = Mock()
        gestor.cursor = Mock()
        
        gestor.desconectar()
        
        # Verificar que se cerraron cursor y conexión
        gestor.cursor.close.assert_called_once()
        gestor.conexion.close.assert_called_once()

    def test_desconectar_sin_conexion(self):
        """Prueba la desconexión cuando no hay conexión activa."""
        gestor = GestorBaseDatos()
        
        # No debería generar error
        gestor.desconectar()

    @patch('psycopg2.connect')
    def test_obtener_siniestros_por_fecha_exitoso(self, mock_connect, sample_accident_data):
        """Prueba la consulta exitosa de siniestros por fecha."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = sample_accident_data
        
        gestor = GestorBaseDatos()
        resultado = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        
        # Verificar resultado
        assert resultado == sample_accident_data
        assert len(resultado) == 2
        
        # Verificar que se ejecutó la consulta SQL
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert 'SELECT' in args[0]
        assert args[1] == ('2024-01-01', '2024-01-31')

    @patch('psycopg2.connect')
    def test_obtener_siniestros_por_fecha_error_conexion(self, mock_connect):
        """Prueba el manejo de errores de conexión en consulta por fecha."""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        gestor = GestorBaseDatos()
        with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
            gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')

    @patch('psycopg2.connect')
    def test_obtener_siniestros_por_fecha_error_generico(self, mock_connect):
        """Prueba el manejo de errores genéricos en consulta por fecha."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Generic error")
        
        gestor = GestorBaseDatos()
        with pytest.raises(Exception, match="Error al obtener siniestros"):
            gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')

    @patch('psycopg2.connect')
    def test_procesar_datos_api_exitoso(self, mock_connect, sample_api_data):
        """Prueba el procesamiento exitoso de datos de la API."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular conteo de registros existentes
        mock_cursor.fetchone.return_value = (100,)
        mock_cursor.rowcount = 1  # Simular inserción exitosa
        
        gestor = GestorBaseDatos()
        resultado = gestor.procesar_datos_api(
            'Accidente',
            sample_api_data,
            CONFIG_TABLAS['Accidente']['columnas']
        )
        
        # Verificar resultado
        assert resultado is not None
        assert resultado['total_registros'] == 1
        assert resultado['nuevos_registros'] == 1
        assert resultado['total_en_bd'] == 101

    @patch('psycopg2.connect')
    def test_procesar_datos_api_error_conexion(self, mock_connect):
        """Prueba el manejo de errores de conexión en procesamiento de datos."""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
        
        gestor = GestorBaseDatos()
        resultado = gestor.procesar_datos_api(
            'Accidente',
            [{'OBJECTID': 1}],
            ['objectid']
        )
        
        assert resultado is None

    @patch('psycopg2.connect')
    def test_procesar_datos_api_error_insercion(self, mock_connect):
        """Prueba el manejo de errores en la inserción de datos."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular error en inserción
        mock_cursor.execute.side_effect = Exception("Insert error")
        
        gestor = GestorBaseDatos()
        resultado = gestor.procesar_datos_api(
            'Accidente',
            [{'OBJECTID': 1}],
            ['objectid']
        )
        
        assert resultado is None

    @patch('psycopg2.connect')
    def test_procesar_datos_api_con_callback_progreso(self, mock_connect, sample_api_data):
        """Prueba el procesamiento de datos con callback de progreso."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.rowcount = 1
        
        callback_calls = []
        def callback_progreso(tipo, actual, total):
            callback_calls.append((tipo, actual, total))
        
        gestor = GestorBaseDatos()
        resultado = gestor.procesar_datos_api(
            'Accidente',
            sample_api_data,
            CONFIG_TABLAS['Accidente']['columnas'],
            callback_progreso
        )
        
        # Verificar que se llamó el callback
        assert len(callback_calls) > 0
        assert callback_calls[0][0] == 'db'
        assert resultado is not None

    @patch('psycopg2.connect')
    def test_procesar_datos_api_rollback_error(self, mock_connect):
        """Prueba el rollback en caso de error durante la inserción."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular error después de algunas inserciones
        mock_cursor.execute.side_effect = [None, Exception("Insert error")]
        mock_cursor.fetchone.return_value = (0,)
        
        gestor = GestorBaseDatos()
        resultado = gestor.procesar_datos_api(
            'Accidente',
            [{'OBJECTID': 1}, {'OBJECTID': 2}],
            ['objectid']
        )
        
        # Verificar que se hizo rollback
        mock_connection.rollback.assert_called_once()
        assert resultado is None

    def test_procesar_datos_api_tabla_invalida(self):
        """Prueba el manejo de tablas inválidas en procesamiento de datos."""
        gestor = GestorBaseDatos()
        
        with pytest.raises(KeyError):
            gestor.procesar_datos_api(
                'TablaInexistente',
                [{'OBJECTID': 1}],
                ['objectid']
            )

    @patch('psycopg2.connect')
    def test_consultar_siniestros_exitoso(self, mock_connect, sample_accident_data):
        """Prueba la consulta exitosa de siniestros."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = sample_accident_data
        
        gestor = GestorBaseDatos()
        gestor.conexion = mock_connection
        
        resultado = gestor.consultar_siniestros('2024-01-01', '2024-01-31')
        
        assert resultado == sample_accident_data

    @patch('psycopg2.connect')
    def test_consultar_siniestros_error_conexion(self, mock_connect):
        """Prueba el manejo de errores de conexión en consulta de siniestros."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.OperationalError("Connection failed")
        
        gestor = GestorBaseDatos()
        gestor.conexion = mock_connection
        
        with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
            gestor.consultar_siniestros('2024-01-01', '2024-01-31')

    def test_limpieza_recursos(self):
        """Prueba que los recursos se limpien correctamente."""
        gestor = GestorBaseDatos()
        gestor.conexion = Mock()
        gestor.cursor = Mock()
        
        # Simular desconexión
        gestor.desconectar()
        
        # Verificar que se limpiaron las referencias
        assert gestor.conexion is None
        assert gestor.cursor is None
