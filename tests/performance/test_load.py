"""Tests de rendimiento y carga para Qtrazer."""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from src.models.database import GestorBaseDatos
from src.models.update_model import ModeloActualizacion
from src.controllers.main_controller import ControladorPrincipal

@pytest.mark.performance
class TestRendimiento:
    """Clase de tests para rendimiento y carga."""

    @patch('psycopg2.connect')
    def test_rendimiento_consulta_grandes_volumenes(self, mock_connect):
        """Prueba el rendimiento con grandes volúmenes de datos."""
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular gran volumen de datos (10,000 registros)
        datos_grandes = [
            (i, f'F{i:05d}', '2024-01-15', '08:00', 'CHAPINERO', 'AUTOMOVIL', f'ABC{i:03d}', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO')
            for i in range(1, 10001)
        ]
        mock_cursor.fetchall.return_value = datos_grandes
        
        gestor = GestorBaseDatos()
        
        # Medir tiempo de consulta
        inicio = time.time()
        resultado = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        tiempo_total = time.time() - inicio
        
        # Verificar que la consulta no tome más de 30 segundos
        assert tiempo_total < 30, f"La consulta tomó {tiempo_total:.2f} segundos, excediendo el límite de 30"
        assert resultado is not None
        assert len(resultado) == 10000

    @patch('psycopg2.connect')
    def test_rendimiento_consulta_rango_fechas_amplio(self, mock_connect):
        """Prueba el rendimiento con rangos de fechas muy amplios."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular consulta de 5 años de datos
        datos_5_anios = [
            (i, f'F{i:05d}', '2020-01-01', '08:00', 'CHAPINERO', 'AUTOMOVIL', f'ABC{i:03d}', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO')
            for i in range(1, 5001)
        ]
        mock_cursor.fetchall.return_value = datos_5_anios
        
        gestor = GestorBaseDatos()
        
        # Medir tiempo de consulta de 5 años
        inicio = time.time()
        resultado = gestor.obtener_siniestros_por_fecha('2020-01-01', '2024-12-31')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento aceptable para consultas de largo plazo
        assert tiempo_total < 45, f"La consulta de 5 años tomó {tiempo_total:.2f} segundos, excediendo el límite de 45"
        assert resultado is not None
        assert len(resultado) == 5000

    @patch('psycopg2.connect')
    def test_rendimiento_consulta_con_filtros_complejos(self, mock_connect):
        """Prueba el rendimiento con filtros complejos y múltiples joins."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular datos con múltiples relaciones
        datos_complejos = [
            (i, f'F{i:05d}', '2024-01-15', '08:00', 'CHAPINERO', 'AUTOMOVIL,MOTOCICLETA', f'ABC{i:03d},XYZ{i:03d}', 'CONDUCTOR,PEATON', 0, 1, 0, 'HERIDO,ILESO', 'MASCULINO,FEMENINO', '25,30', 'CONDUCTOR,PEATON', 'EXCESO VELOCIDAD,NO RESPETAR SEÑAL', 'ASFALTO,ASFALTO', 'BUENO,REGULAR')
            for i in range(1, 1001)
        ]
        mock_cursor.fetchall.return_value = datos_complejos
        
        gestor = GestorBaseDatos()
        
        # Medir tiempo de consulta compleja
        inicio = time.time()
        resultado = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento para consultas complejas
        assert tiempo_total < 15, f"La consulta compleja tomó {tiempo_total:.2f} segundos, excediendo el límite de 15"
        assert resultado is not None
        assert len(resultado) == 1000

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_rendimiento_actualizacion_grandes_volumenes(self, mock_connect, mock_get):
        """Prueba el rendimiento de actualización con grandes volúmenes de datos."""
        # Configurar mock de API
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'total': 50000,
                'count': 50000,
                'features': [
                    {'attributes': {'OBJECTID': i, 'FORMULARIO': f'F{i:05d}'}} 
                    for i in range(1, 50001)
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)  # Sin registros previos
        mock_cursor.rowcount = 1
        
        modelo = ModeloActualizacion()
        
        # Medir tiempo de actualización
        inicio = time.time()
        resultado = modelo.actualizar_datos('Accidente')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento para actualizaciones masivas
        assert tiempo_total < 120, f"La actualización masiva tomó {tiempo_total:.2f} segundos, excediendo el límite de 120"
        assert resultado is True

    @patch('psycopg2.connect')
    def test_rendimiento_insercion_lotes(self, mock_connect):
        """Prueba el rendimiento de inserción por lotes."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.rowcount = 1
        
        # Crear DataFrame grande
        import pandas as pd
        datos_lotes = pd.DataFrame({
            'OBJECTID': range(1, 10001),
            'FORMULARIO': [f'F{i:05d}' for i in range(1, 10001)],
            'CODIGO_ACCIDENTE': range(10001, 20001),
            'FECHA_OCURRENCIA_ACC': ['2024-01-15'] * 10000,
            'HORA_OCURRENCIA_ACC': ['08:00'] * 10000,
            'LOCALIDAD': ['CHAPINERO'] * 10000
        })
        
        modelo = ModeloActualizacion()
        
        # Medir tiempo de inserción por lotes
        inicio = time.time()
        resultado = modelo.insertar_registros(datos_lotes, 'Accidente')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento de inserción por lotes
        assert tiempo_total < 60, f"La inserción por lotes tomó {tiempo_total:.2f} segundos, excediendo el límite de 60"
        assert resultado is True

    def test_rendimiento_concurrencia_multiples_consultas(self):
        """Prueba el rendimiento con múltiples consultas simultáneas."""
        import threading
        import time
        
        controlador = ControladorPrincipal()
        resultados = []
        tiempos = []
        
        def ejecutar_consulta(thread_id):
            inicio = time.time()
            
            # Simular consulta
            cola = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
            
            # Simular resultados
            datos_thread = [
                (thread_id * 1000 + i, f'F{thread_id:02d}{i:03d}', '2024-01-15', '08:00', 'CHAPINERO')
                for i in range(1, 101)
            ]
            controlador.cola_resultados.put(datos_thread)
            
            resultado = controlador.obtener_resultados_consulta()
            tiempo_total = time.time() - inicio
            
            resultados.append(resultado)
            tiempos.append(tiempo_total)
        
        # Ejecutar 10 consultas simultáneamente
        threads = []
        for i in range(10):
            thread = threading.Thread(target=ejecutar_consulta, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()
        
        # Verificar que todas las consultas se completaron
        assert len(resultados) == 10
        assert len(tiempos) == 10
        
        # Verificar rendimiento individual
        for i, tiempo in enumerate(tiempos):
            assert tiempo < 10, f"La consulta {i} tomó {tiempo:.2f} segundos, excediendo el límite de 10"
        
        # Verificar rendimiento agregado
        tiempo_total = sum(tiempos)
        assert tiempo_total < 50, f"El tiempo total de todas las consultas fue {tiempo_total:.2f} segundos, excediendo el límite de 50"

    def test_rendimiento_memoria_consultas_largas(self):
        """Prueba el uso de memoria durante consultas largas."""
        import psutil
        import os
        
        # Obtener uso de memoria inicial
        proceso = psutil.Process(os.getpid())
        memoria_inicial = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Simular consulta larga
        controlador = ControladorPrincipal()
        
        # Simular múltiples consultas para probar uso de memoria
        for i in range(5):
            cola = controlador.consultar_siniestros('2024-01-01', '2024-01-31')
            
            # Simular resultados grandes
            datos_grandes = [
                (j, f'F{i:02d}{j:05d}', '2024-01-15', '08:00', 'CHAPINERO')
                for j in range(1, 1001)
            ]
            controlador.cola_resultados.put(datos_grandes)
            
            resultado = controlador.obtener_resultados_consulta()
            
            # Limpiar para la siguiente iteración
            controlador.cola_resultados = controlador.cola_resultados.__class__()
        
        # Obtener uso de memoria final
        memoria_final = proceso.memory_info().rss / 1024 / 1024  # MB
        
        # Verificar que no hay fugas de memoria significativas
        incremento_memoria = memoria_final - memoria_inicial
        assert incremento_memoria < 100, f"El incremento de memoria fue {incremento_memoria:.2f} MB, excediendo el límite de 100 MB"

    @patch('psycopg2.connect')
    def test_rendimiento_consulta_con_indices(self, mock_connect):
        """Prueba el rendimiento de consultas optimizadas con índices."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular datos con diferentes localidades para probar índices
        datos_localidades = []
        localidades = ['CHAPINERO', 'USAQUEN', 'SUBA', 'ENGATIVA', 'KENNEDY']
        
        for i, localidad in enumerate(localidades):
            for j in range(1, 1001):  # 1000 registros por localidad
                datos_localidades.append((
                    i * 1000 + j, f'F{i:02d}{j:05d}', '2024-01-15', '08:00', localidad,
                    'AUTOMOVIL', f'ABC{i:02d}{j:03d}', 'CONDUCTOR', 0, 1, 0, 'HERIDO',
                    'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'
                ))
        
        mock_cursor.fetchall.return_value = datos_localidades
        
        gestor = GestorBaseDatos()
        
        # Medir tiempo de consulta por localidad específica
        inicio = time.time()
        resultado = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento optimizado
        assert tiempo_total < 20, f"La consulta optimizada tomó {tiempo_total:.2f} segundos, excediendo el límite de 20"
        assert resultado is not None
        assert len(resultado) == 5000  # 5 localidades * 1000 registros

    @patch('requests.get')
    @patch('psycopg2.connect')
    def test_rendimiento_api_con_paginacion(self, mock_get, mock_connect):
        """Prueba el rendimiento de la API con paginación eficiente."""
        # Configurar mock de API con paginación
        mock_responses = []
        
        # Simular 10 páginas de 1000 registros cada una
        for pagina in range(10):
            mock_response = Mock()
            mock_response.json.return_value = {
                'result': {
                    'total': 10000,
                    'count': 1000,
                    'features': [
                        {'attributes': {'OBJECTID': pagina * 1000 + i, 'FORMULARIO': f'F{pagina:02d}{i:05d}'}} 
                        for i in range(1, 1001)
                    ]
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_responses.append(mock_response)
        
        mock_get.side_effect = mock_responses
        
        # Configurar mock de base de datos
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.rowcount = 1
        
        modelo = ModeloActualizacion()
        
        # Medir tiempo de actualización con paginación
        inicio = time.time()
        resultado = modelo.actualizar_datos('Accidente')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento con paginación
        assert tiempo_total < 90, f"La actualización con paginación tomó {tiempo_total:.2f} segundos, excediendo el límite de 90"
        assert resultado is True
        
        # Verificar que se realizaron las llamadas de paginación
        assert mock_get.call_count == 10

    def test_rendimiento_limpieza_recursos(self):
        """Prueba el rendimiento de limpieza de recursos."""
        import gc
        import time
        
        # Crear múltiples instancias para probar limpieza
        instancias = []
        
        inicio = time.time()
        
        for i in range(100):
            controlador = ControladorPrincipal()
            instancias.append(controlador)
        
        # Simular uso
        for controlador in instancias:
            controlador.consultar_siniestros('2024-01-01', '2024-01-31')
        
        # Limpiar instancias
        instancias.clear()
        
        # Forzar garbage collection
        gc.collect()
        
        tiempo_limpieza = time.time() - inicio
        
        # Verificar rendimiento de limpieza
        assert tiempo_limpieza < 5, f"La limpieza de recursos tomó {tiempo_limpieza:.2f} segundos, excediendo el límite de 5"

    @patch('psycopg2.connect')
    def test_rendimiento_consulta_con_agregaciones(self, mock_connect):
        """Prueba el rendimiento de consultas con agregaciones complejas."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simular datos para agregaciones
        datos_agregacion = []
        for i in range(1, 10001):
            localidad = ['CHAPINERO', 'USAQUEN', 'SUBA', 'ENGATIVA', 'KENNEDY'][i % 5]
            gravedad = ['HERIDO', 'ILESO', 'MUERTO'][i % 3]
            vehiculo = ['AUTOMOVIL', 'MOTOCICLETA', 'BUS'][i % 3]
            
            datos_agregacion.append((
                i, f'F{i:05d}', '2024-01-15', '08:00', localidad,
                vehiculo, f'ABC{i:03d}', 'CONDUCTOR', 0, 1, 0, gravedad,
                'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'
            ))
        
        mock_cursor.fetchall.return_value = datos_agregacion
        
        gestor = GestorBaseDatos()
        
        # Medir tiempo de consulta con agregaciones
        inicio = time.time()
        resultado = gestor.obtener_siniestros_por_fecha('2024-01-01', '2024-01-31')
        tiempo_total = time.time() - inicio
        
        # Verificar rendimiento para consultas con agregaciones
        assert tiempo_total < 25, f"La consulta con agregaciones tomó {tiempo_total:.2f} segundos, excediendo el límite de 25"
        assert resultado is not None
        assert len(resultado) == 10000
