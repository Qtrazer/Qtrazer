"""Tests unitarios para el cliente API."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from src.models.api_client import ClienteAPI
from src.config.settings import CONFIG_TABLAS

class TestClienteAPI:
    """Clase de tests para ClienteAPI."""

    def test_init(self):
        """Prueba la inicialización del cliente API."""
        cliente = ClienteAPI()
        assert cliente.url_base == "https://datosabiertos.bogota.gov.co/api/3/action/datastore_search"
        assert cliente.recurso_id == "b64ba3c4-9e41-41b8-b3fd-2da21d627558"

    @patch('requests.get')
    def test_obtener_registros_exitoso(self, mock_get, mock_api_response):
        """Prueba la obtención exitosa de registros de la API."""
        # Configurar mock
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        # Verificar resultado
        assert resultado is not None
        assert len(resultado) == 2
        assert resultado[0]['OBJECTID'] == 1
        assert resultado[0]['FORMULARIO'] == 'F001'
        assert resultado[1]['OBJECTID'] == 2
        assert resultado[1]['FORMULARIO'] == 'F002'

    @patch('requests.get')
    def test_obtener_registros_con_paginacion(self, mock_get):
        """Prueba la obtención de registros con paginación."""
        # Primera llamada para obtener total
        mock_response1 = Mock()
        mock_response1.json.return_value = {'result': {'total': 250}}
        mock_response1.raise_for_status.return_value = None
        
        # Segunda llamada para obtener registros
        mock_response2 = Mock()
        mock_response2.json.return_value = {
            'result': {
                'records': [{'id': i} for i in range(100)]
            }
        }
        mock_response2.raise_for_status.return_value = None
        
        # Tercera llamada para obtener más registros
        mock_response3 = Mock()
        mock_response3.json.return_value = {
            'result': {
                'records': [{'id': i} for i in range(100, 200)]
            }
        }
        mock_response3.raise_for_status.return_value = None
        
        # Cuarta llamada para obtener registros restantes
        mock_response4 = Mock()
        mock_response4.json.return_value = {
            'result': {
                'records': [{'id': i} for i in range(200, 250)]
            }
        }
        mock_response4.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_response1, mock_response2, mock_response3, mock_response4]
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        # Verificar que se obtuvieron todos los registros
        assert resultado is not None
        assert len(resultado) == 250
        assert mock_get.call_count == 4

    @patch('requests.get')
    def test_obtener_registros_error_conexion(self, mock_get):
        """Prueba el manejo de errores de conexión."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        assert resultado is None

    @patch('requests.get')
    def test_obtener_registros_error_timeout(self, mock_get):
        """Prueba el manejo de errores de timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout error")
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        assert resultado is None

    @patch('requests.get')
    def test_obtener_registros_error_http(self, mock_get):
        """Prueba el manejo de errores HTTP."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP 500")
        mock_get.return_value = mock_response
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        assert resultado is None

    @patch('requests.get')
    def test_obtener_registros_con_callback_progreso(self, mock_get, mock_api_response):
        """Prueba la obtención de registros con callback de progreso."""
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_get.return_value = mock_response
        
        callback_calls = []
        def callback_progreso(tipo, actual, total):
            callback_calls.append((tipo, actual, total))
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente', callback_progreso)
        
        # Verificar que se llamó el callback
        assert len(callback_calls) > 0
        assert callback_calls[0][0] == 'api'
        assert resultado is not None

    def test_obtener_registros_tabla_invalida(self):
        """Prueba el manejo de tablas inválidas."""
        cliente = ClienteAPI()
        
        with pytest.raises(KeyError):
            cliente.obtener_registros('TablaInexistente')

    @patch('requests.get')
    def test_obtener_registros_respuesta_vacia(self, mock_get):
        """Prueba el manejo de respuestas vacías de la API."""
        mock_response = Mock()
        mock_response.json.return_value = {'result': {'total': 0, 'records': []}}
        mock_get.return_value = mock_response
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        assert resultado == []

    @patch('requests.get')
    def test_obtener_registros_estructura_respuesta_invalida(self, mock_get):
        """Prueba el manejo de estructuras de respuesta inválidas."""
        mock_response = Mock()
        mock_response.json.return_value = {'invalid': 'structure'}
        mock_get.return_value = mock_response
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        assert resultado is None

    @patch('requests.get')
    def test_obtener_registros_con_retry(self, mock_get):
        """Prueba el comportamiento de reintento en caso de fallos temporales."""
        # Simular fallo en la primera llamada, éxito en la segunda
        mock_response_fail = Mock()
        mock_response_fail.json.side_effect = Exception("Temporary error")
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {'result': {'total': 100, 'records': []}}
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        cliente = ClienteAPI()
        resultado = cliente.obtener_registros('Accidente')
        
        # Verificar que se realizaron múltiples intentos
        assert mock_get.call_count >= 2
