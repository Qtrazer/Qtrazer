"""Tests unitarios para los controladores."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import queue
import threading
from src.controllers.main_controller import ControladorPrincipal
from src.controllers.update_controller import ControladorActualizacion

class TestControladorPrincipal:
    """Clase de tests para ControladorPrincipal."""

    def test_init(self):
        """Prueba la inicialización del controlador principal."""
        controlador = ControladorPrincipal()
        assert controlador.gestor_bd is not None
        assert controlador.cliente_api is not None
        assert isinstance(controlador.cola_resultados, queue.Queue)
        assert controlador.consulta_en_progreso is False

    @patch('src.models.api_client.ClienteAPI')
    @patch('src.models.database.GestorBaseDatos')
    def test_actualizar_datos_exitoso(self, mock_gestor_bd, mock_cliente_api):
        """Prueba la actualización exitosa de datos."""
        # Configurar mocks
        mock_cliente = Mock()
        mock_cliente.obtener_registros.return_value = [{'id': 1}, {'id': 2}]
        mock_cliente_api.return_value = mock_cliente
        
        mock_gestor = Mock()
        mock_gestor.procesar_datos_api.return_value = {
            'total_registros': 2,
            'nuevos_registros': 2,
            'total_en_bd': 102
        }
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        resultado = controlador.actualizar_datos('Accidente')
        
        # Verificar resultado
        assert resultado is not None
        assert resultado['total_registros'] == 2
        assert resultado['nuevos_registros'] == 2
        
        # Verificar que se llamaron los métodos correctos
        mock_cliente.obtener_registros.assert_called_once_with('Accidente', None)
        mock_gestor.procesar_datos_api.assert_called_once()

    @patch('src.models.api_client.ClienteAPI')
    @patch('src.models.database.GestorBaseDatos')
    def test_actualizar_datos_sin_registros(self, mock_gestor_bd, mock_cliente_api):
        """Prueba la actualización cuando no hay registros de la API."""
        mock_cliente = Mock()
        mock_cliente.obtener_registros.return_value = None
        mock_cliente_api.return_value = mock_cliente
        
        mock_gestor = Mock()
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        resultado = controlador.actualizar_datos('Accidente')
        
        assert resultado is None
        mock_gestor.procesar_datos_api.assert_not_called()

    @patch('src.models.api_client.ClienteAPI')
    @patch('src.models.database.GestorBaseDatos')
    def test_actualizar_datos_error_conexion(self, mock_gestor_bd, mock_cliente_api):
        """Prueba el manejo de errores de conexión en actualización."""
        mock_cliente = Mock()
        mock_cliente.obtener_registros.side_effect = Exception("connection failed")
        mock_cliente_api.return_value = mock_cliente
        
        mock_gestor = Mock()
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        
        with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
            controlador.actualizar_datos('Accidente')

    @patch('src.models.api_client.ClienteAPI')
    @patch('src.models.database.GestorBaseDatos')
    def test_actualizar_datos_error_generico(self, mock_gestor_bd, mock_cliente_api):
        """Prueba el manejo de errores genéricos en actualización."""
        mock_cliente = Mock()
        mock_cliente.obtener_registros.side_effect = Exception("Generic error")
        mock_cliente_api.return_value = mock_cliente
        
        mock_gestor = Mock()
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        resultado = controlador.actualizar_datos('Accidente')
        
        assert resultado is None

    def test_consultar_siniestros_primera_vez(self):
        """Prueba la primera consulta de siniestros."""
        controlador = ControladorPrincipal()
        
        cola_resultados = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        # Verificar que se inició la consulta
        assert controlador.consulta_en_progreso is True
        assert cola_resultados is not None
        assert isinstance(cola_resultados, queue.Queue)

    def test_consultar_siniestros_ya_en_progreso(self):
        """Prueba que no se pueda iniciar una consulta si ya hay una en progreso."""
        controlador = ControladorPrincipal()
        controlador.consulta_en_progreso = True
        
        cola_resultados = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        assert cola_resultados is None

    @patch('src.models.database.GestorBaseDatos')
    def test_consultar_siniestros_ejecucion_hilo(self, mock_gestor_bd):
        """Prueba la ejecución de consulta en hilo separado."""
        mock_gestor = Mock()
        mock_gestor.obtener_siniestros_por_fecha.return_value = [('1', 'F001', '2024-01-15')]
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        cola_resultados = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        # Esperar a que el hilo termine
        import time
        time.sleep(0.1)
        
        # Verificar que se completó la consulta
        assert controlador.consulta_en_progreso is False
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        assert resultado is not None
        assert len(resultado) == 1

    @patch('src.models.database.GestorBaseDatos')
    def test_consultar_siniestros_error_conexion(self, mock_gestor_bd):
        """Prueba el manejo de errores de conexión en consulta."""
        mock_gestor = Mock()
        mock_gestor.obtener_siniestros_por_fecha.side_effect = Exception("connection failed")
        mock_gestor_bd.return_value = mock_gestor
        
        controlador = ControladorPrincipal()
        cola_resultados = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        # Esperar a que el hilo termine
        import time
        time.sleep(0.1)
        
        # Verificar que se completó la consulta
        assert controlador.consulta_en_progreso is False
        
        # Obtener resultados (debería ser una excepción)
        resultado = controlador.obtener_resultados_consulta()
        assert isinstance(resultado, Exception)
        assert "Falló la conexión a la base de datos" in str(resultado)

    def test_obtener_resultados_consulta_disponibles(self):
        """Prueba la obtención de resultados cuando están disponibles."""
        controlador = ControladorPrincipal()
        controlador.cola_resultados.put([('1', 'F001', '2024-01-15')])
        
        resultado = controlador.obtener_resultados_consulta()
        
        assert resultado is not None
        assert len(resultado) == 1

    def test_obtener_resultados_consulta_no_disponibles(self):
        """Prueba la obtención de resultados cuando no están disponibles."""
        controlador = ControladorPrincipal()
        
        resultado = controlador.obtener_resultados_consulta()
        
        assert resultado is None

    def test_obtener_resultados_consulta_cola_vacia(self):
        """Prueba la obtención de resultados de una cola vacía."""
        controlador = ControladorPrincipal()
        controlador.cola_resultados = queue.Queue()
        
        resultado = controlador.obtener_resultados_consulta()
        
        assert resultado is None

    def test_estado_consulta_en_progreso(self):
        """Prueba el estado de consulta en progreso."""
        controlador = ControladorPrincipal()
        
        # Inicialmente no hay consulta en progreso
        assert controlador.consulta_en_progreso is False
        
        # Simular inicio de consulta
        controlador.consulta_en_progreso = True
        assert controlador.consulta_en_progreso is True
        
        # Simular fin de consulta
        controlador.consulta_en_progreso = False
        assert controlador.consulta_en_progreso is False

    def test_reinicializacion_cola_resultados(self):
        """Prueba la reinicialización de la cola de resultados."""
        controlador = ControladorPrincipal()
        
        # Agregar algunos resultados
        controlador.cola_resultados.put("resultado1")
        controlador.cola_resultados.put("resultado2")
        
        # Verificar que hay resultados
        assert not controlador.cola_resultados.empty()
        
        # Iniciar nueva consulta (debería reinicializar la cola)
        controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        # La cola debería estar vacía para la nueva consulta
        assert controlador.cola_resultados.empty()

class TestControladorActualizacion:
    """Clase de tests para ControladorActualizacion."""

    def test_init(self):
        """Prueba la inicialización del controlador de actualización."""
        controlador = ControladorActualizacion()
        assert controlador.modelo is not None
        assert controlador.actualizacion_en_progreso is False
        assert controlador.thread_actualizacion is None
        assert controlador.tabla_actual is None

    def test_esta_actualizando_false(self):
        """Prueba el estado cuando no hay actualización en progreso."""
        controlador = ControladorActualizacion()
        
        assert controlador.esta_actualizando() is False

    def test_esta_actualizando_true(self):
        """Prueba el estado cuando hay actualización en progreso."""
        controlador = ControladorActualizacion()
        controlador.actualizacion_en_progreso = True
        
        assert controlador.esta_actualizando() is True

    @patch('src.models.update_model.ModeloActualizacion')
    def test_iniciar_actualizacion_exitoso(self, mock_modelo):
        """Prueba el inicio exitoso de actualización."""
        mock_modelo_instance = Mock()
        mock_modelo_instance.actualizar_datos.return_value = True
        mock_modelo.return_value = mock_modelo_instance
        
        controlador = ControladorActualizacion()
        
        # Simular callback
        callback_calls = []
        def callback_progreso(mensaje, porcentaje):
            callback_calls.append((mensaje, porcentaje))
        
        resultado = controlador.iniciar_actualizacion(callback_progreso)
        
        # Verificar que se inició la actualización
        assert resultado is True
        assert controlador.actualizacion_en_progreso is True
        assert controlador.tabla_actual == 'Accidente'
        assert controlador.thread_actualizacion is not None

    def test_iniciar_actualizacion_ya_en_progreso(self):
        """Prueba que no se pueda iniciar una actualización si ya hay una en progreso."""
        controlador = ControladorActualizacion()
        controlador.actualizacion_en_progreso = True
        
        resultado = controlador.iniciar_actualizacion()
        
        assert resultado is False

    @patch('src.models.update_model.ModeloActualizacion')
    def test_iniciar_actualizacion_error_primera_tabla(self, mock_modelo):
        """Prueba el manejo de errores en la primera tabla."""
        mock_modelo_instance = Mock()
        mock_modelo_instance.actualizar_datos.return_value = False
        mock_modelo.return_value = mock_modelo_instance
        
        controlador = ControladorActualizacion()
        
        callback_calls = []
        def callback_progreso(mensaje, porcentaje):
            callback_calls.append((mensaje, porcentaje))
        
        resultado = controlador.iniciar_actualizacion(callback_progreso)
        
        # Verificar que se inició pero falló
        assert resultado is True
        
        # Esperar a que el hilo termine
        import time
        time.sleep(0.1)
        
        # Verificar que se completó la actualización
        assert controlador.actualizacion_en_progreso is False

    def test_cancelar_actualizacion_exitoso(self):
        """Prueba la cancelación exitosa de actualización."""
        controlador = ControladorActualizacion()
        controlador.actualizacion_en_progreso = True
        controlador.thread_actualizacion = Mock()
        
        resultado = controlador.cancelar_actualizacion()
        
        assert resultado is True
        assert controlador.actualizacion_en_progreso is False

    def test_cancelar_actualizacion_no_en_progreso(self):
        """Prueba la cancelación cuando no hay actualización en progreso."""
        controlador = ControladorActualizacion()
        
        resultado = controlador.cancelar_actualizacion()
        
        assert resultado is False

    def test_cancelar_actualizacion_con_hilo(self):
        """Prueba la cancelación con hilo activo."""
        controlador = ControladorActualizacion()
        controlador.actualizacion_en_progreso = True
        
        # Crear un hilo mock
        mock_thread = Mock()
        mock_thread.join.return_value = None
        controlador.thread_actualizacion = mock_thread
        
        resultado = controlador.cancelar_actualizacion()
        
        assert resultado is True
        mock_thread.join.assert_called_once()

    def test_estado_tabla_actual(self):
        """Prueba el estado de la tabla actual."""
        controlador = ControladorActualizacion()
        
        # Inicialmente no hay tabla actual
        assert controlador.tabla_actual is None
        
        # Simular inicio de actualización
        controlador.tabla_actual = 'Accidente'
        assert controlador.tabla_actual == 'Accidente'
        
        # Simular fin de actualización
        controlador.tabla_actual = None
        assert controlador.tabla_actual is None

    def test_limpieza_recursos_actualizacion(self):
        """Prueba la limpieza de recursos después de la actualización."""
        controlador = ControladorActualizacion()
        controlador.actualizacion_en_progreso = True
        controlador.tabla_actual = 'Accidente'
        controlador.thread_actualizacion = Mock()
        
        # Simular fin de actualización
        controlador.actualizacion_en_progreso = False
        controlador.tabla_actual = None
        controlador.thread_actualizacion = None
        
        assert controlador.actualizacion_en_progreso is False
        assert controlador.tabla_actual is None
        assert controlador.thread_actualizacion is None
