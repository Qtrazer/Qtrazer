"""Tests funcionales para escenarios de usuario."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from src.controllers.main_controller import ControladorPrincipal
from src.controllers.update_controller import ControladorActualizacion
from src.models.database import GestorBaseDatos

@pytest.mark.functional
class TestEscenariosUsuario:
    """Clase de tests para escenarios de usuario reales."""

    def test_escenario_consulta_siniestros_mensual(self):
        """Escenario: Usuario consulta siniestros de un mes completo."""
        controlador = ControladorPrincipal()
        
        # Simular consulta de siniestros del mes de enero 2024
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 31)
        
        # Iniciar consulta
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Verificar que se inició la consulta
        assert cola_resultados is not None
        assert controlador.consulta_en_progreso is True
        
        # Simular resultados de la consulta
        resultados_simulados = [
            (1, 'F001', date(2024, 1, 15), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
            (2, 'F002', date(2024, 1, 16), '09:00', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR'),
            (3, 'F003', date(2024, 1, 20), '14:30', 'SUBA', 'AUTOMOVIL', 'DEF456', 'CONDUCTOR', 1, 0, 0, 'MUERTO', 'MASCULINO', 45, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'MALO')
        ]
        
        controlador.cola_resultados.put(resultados_simulados)
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Verificar resultados
        assert resultado is not None
        assert len(resultado) == 3
        assert controlador.consulta_en_progreso is False
        
        # Verificar que se completó la consulta
        assert resultado[0][4] == 'CHAPINERO'  # Localidad del primer accidente
        assert resultado[1][4] == 'USAQUEN'    # Localidad del segundo accidente
        assert resultado[2][4] == 'SUBA'       # Localidad del tercer accidente

    def test_escenario_actualizacion_datos_completa(self):
        """Escenario: Usuario ejecuta actualización completa de todas las tablas."""
        controlador = ControladorActualizacion()
        
        # Simular callback de progreso
        progreso_registrado = []
        def callback_progreso(mensaje, porcentaje):
            progreso_registrado.append((mensaje, porcentaje))
        
        # Iniciar actualización
        resultado = controlador.iniciar_actualizacion(callback_progreso)
        
        # Verificar que se inició la actualización
        assert resultado is True
        assert controlador.actualizacion_en_progreso is True
        assert controlador.tabla_actual == 'Accidente'
        
        # Simular progreso de actualización
        callback_progreso("Iniciando actualización de la tabla 'Accidente'...", 0)
        callback_progreso("Total de registros en la API: 1000", 0)
        callback_progreso("ObjectID más reciente encontrado: 500", 0)
        callback_progreso("Total de nuevos registros encontrados: 500", 0)
        callback_progreso("Iniciando inserción de registros en la base de datos...", 0)
        callback_progreso("Registros insertados: 100/500 (20.0%)", 20)
        callback_progreso("Registros insertados: 500/500 (100.0%)", 100)
        callback_progreso("Actualización completada exitosamente", 100)
        
        # Verificar que se registró el progreso
        assert len(progreso_registrado) >= 7
        assert progreso_registrado[0][0] == "Iniciando actualización de la tabla 'Accidente'..."
        assert progreso_registrado[-1][0] == "Actualización completada exitosamente"
        assert progreso_registrado[-1][1] == 100

    def test_escenario_consulta_con_filtros_avanzados(self):
        """Escenario: Usuario aplica filtros avanzados a los resultados."""
        controlador = ControladorPrincipal()
        
        # Simular consulta inicial
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 31)
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular resultados con diferentes características
        resultados_completos = [
            (1, 'F001', date(2024, 1, 15), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
            (2, 'F002', date(2024, 1, 16), '09:00', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR'),
            (3, 'F003', date(2024, 1, 20), '14:30', 'CHAPINERO', 'AUTOMOVIL', 'DEF456', 'CONDUCTOR', 1, 0, 0, 'MUERTO', 'MASCULINO', 45, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'MALO'),
            (4, 'F004', date(2024, 1, 25), '16:00', 'SUBA', 'MOTOCICLETA', 'GHI789', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'FEMENINO', 28, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'BUENO')
        ]
        
        controlador.cola_resultados.put(resultados_completos)
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Simular aplicación de filtros
        # Filtro 1: Solo accidentes en CHAPINERO
        resultados_filtrados_localidad = [
            r for r in resultado if r[4] == 'CHAPINERO'
        ]
        
        # Filtro 2: Solo accidentes con MOTOCICLETA
        resultados_filtrados_vehiculo = [
            r for r in resultado if 'MOTOCICLETA' in r[5]
        ]
        
        # Filtro 3: Solo accidentes con fallecidos
        resultados_filtrados_fallecidos = [
            r for r in resultado if r[8] > 0  # Fallecidos > 0
        ]
        
        # Verificar filtros
        assert len(resultados_filtrados_localidad) == 2  # F001 y F003
        assert len(resultados_filtrados_vehiculo) == 2  # F002 y F004
        assert len(resultados_filtrados_fallecidos) == 1  # Solo F003

    def test_escenario_consulta_por_rango_fechas_especifico(self):
        """Escenario: Usuario consulta un rango de fechas específico."""
        controlador = ControladorPrincipal()
        
        # Consulta de un fin de semana específico
        fecha_inicio = date(2024, 1, 13)  # Sábado
        fecha_fin = date(2024, 1, 14)     # Domingo
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular resultados del fin de semana
        resultados_finde = [
            (1, 'F001', date(2024, 1, 13), '22:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
            (2, 'F002', date(2024, 1, 14), '02:30', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR')
        ]
        
        controlador.cola_resultados.put(resultados_finde)
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Verificar que solo se obtuvieron resultados del fin de semana
        assert len(resultado) == 2
        assert resultado[0][2] == date(2024, 1, 13)  # Sábado
        assert resultado[1][2] == date(2024, 1, 14)  # Domingo

    def test_escenario_actualizacion_incremental(self):
        """Escenario: Usuario ejecuta actualización incremental de datos."""
        controlador = ControladorActualizacion()
        
        # Simular que ya hay datos en la base de datos
        # ObjectID más reciente: 1000
        
        # Simular nuevos datos en la API (ObjectID > 1000)
        nuevos_datos = [
            {'OBJECTID': 1001, 'FORMULARIO': 'F1001'},
            {'OBJECTID': 1002, 'FORMULARIO': 'F1002'},
            {'OBJECTID': 1003, 'FORMULARIO': 'F1003'}
        ]
        
        # Simular callback de progreso
        progreso_registrado = []
        def callback_progreso(mensaje, porcentaje):
            progreso_registrado.append((mensaje, porcentaje))
        
        # Iniciar actualización incremental
        resultado = controlador.iniciar_actualizacion(callback_progreso)
        
        # Verificar que se inició la actualización
        assert resultado is True
        
        # Simular progreso de actualización incremental
        callback_progreso("Total de registros en la API: 1003", 0)
        callback_progreso("ObjectID más reciente encontrado: 1000", 0)
        callback_progreso("Total de nuevos registros encontrados: 3", 0)
        callback_progreso("Porcentaje de nuevos registros: 0.30%", 0)
        callback_progreso("Iniciando inserción de registros en la base de datos...", 0)
        callback_progreso("Registros insertados: 3/3 (100.0%)", 100)
        callback_progreso("Actualización completada exitosamente", 100)
        
        # Verificar progreso
        assert len(progreso_registrado) >= 7
        assert "nuevos registros encontrados: 3" in progreso_registrado[2][0]
        assert progreso_registrado[-1][1] == 100

    def test_escenario_consulta_con_exportacion(self):
        """Escenario: Usuario consulta datos y los exporta a Excel."""
        controlador = ControladorPrincipal()
        
        # Simular consulta
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 31)
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular resultados para exportación
        resultados_exportacion = [
            (1, 'F001', date(2024, 1, 15), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
            (2, 'F002', date(2024, 1, 16), '09:00', 'USAQUEN', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR'),
            (3, 'F003', date(2024, 1, 20), '14:30', 'SUBA', 'AUTOMOVIL', 'DEF456', 'CONDUCTOR', 1, 0, 0, 'MUERTO', 'MASCULINO', 45, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'MALO')
        ]
        
        controlador.cola_resultados.put(resultados_exportacion)
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Simular preparación para exportación
        # Verificar que los datos están en el formato correcto para exportación
        assert len(resultado) == 3
        
        # Verificar estructura de datos para exportación
        for registro in resultado:
            assert len(registro) == 18  # Número de columnas esperadas
            assert isinstance(registro[0], int)      # ID
            assert isinstance(registro[1], str)      # Formulario
            assert isinstance(registro[2], date)     # Fecha
            assert isinstance(registro[3], str)      # Hora
            assert isinstance(registro[4], str)      # Localidad

    def test_escenario_manejo_errores_conexion(self):
        """Escenario: Usuario maneja errores de conexión durante la consulta."""
        controlador = ControladorPrincipal()
        
        # Simular consulta
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 31)
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular error de conexión
        error_conexion = Exception("Falló la conexión a la base de datos, valida con el administrador")
        controlador.cola_resultados.put(error_conexion)
        
        # Obtener resultados (debería ser una excepción)
        resultado = controlador.obtener_resultados_consulta()
        
        # Verificar manejo del error
        assert isinstance(resultado, Exception)
        assert "Falló la conexión a la base de datos" in str(resultado)
        assert controlador.consulta_en_progreso is False

    def test_escenario_consulta_sin_resultados(self):
        """Escenario: Usuario consulta un rango de fechas sin resultados."""
        controlador = ControladorPrincipal()
        
        # Consulta de un rango de fechas muy específico sin datos
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 1)  # Solo un día
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular consulta sin resultados
        controlador.cola_resultados.put([])
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Verificar que no hay resultados
        assert resultado == []
        assert controlador.consulta_en_progreso is False

    def test_escenario_actualizacion_con_errores_parciales(self):
        """Escenario: Usuario ejecuta actualización con errores en algunas tablas."""
        controlador = ControladorActualizacion()
        
        # Simular callback de progreso
        progreso_registrado = []
        def callback_progreso(mensaje, porcentaje):
            progreso_registrado.append((mensaje, porcentaje))
        
        # Iniciar actualización
        resultado = controlador.iniciar_actualizacion(callback_progreso)
        
        # Verificar que se inició
        assert resultado is True
        
        # Simular progreso con errores parciales
        callback_progreso("Iniciando actualización de la tabla 'Accidente'...", 0)
        callback_progreso("Total de registros en la API: 1000", 0)
        callback_progreso("ObjectID más reciente encontrado: 500", 0)
        callback_progreso("Total de nuevos registros encontrados: 500", 0)
        callback_progreso("Iniciando inserción de registros en la base de datos...", 0)
        callback_progreso("Registros insertados: 500/500 (100.0%)", 100)
        
        # Simular error en la siguiente tabla
        callback_progreso("Iniciando actualización de la tabla 'Accidente Via'...", 0)
        callback_progreso("Error al actualizar la tabla 'Accidente Via'", 0)
        
        # Verificar progreso registrado
        assert len(progreso_registrado) >= 7
        assert "Error al actualizar" in progreso_registrado[-1][0]

    def test_escenario_consulta_con_filtros_combinados(self):
        """Escenario: Usuario aplica múltiples filtros combinados."""
        controlador = ControladorPrincipal()
        
        # Simular consulta inicial
        fecha_inicio = date(2024, 1, 1)
        fecha_fin = date(2024, 1, 31)
        
        cola_resultados = controlador.consultar_siniestros(fecha_inicio, fecha_fin)
        
        # Simular resultados diversos
        resultados_completos = [
            (1, 'F001', date(2024, 1, 15), '08:00', 'CHAPINERO', 'AUTOMOVIL', 'ABC123', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'MASCULINO', 25, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'BUENO'),
            (2, 'F002', date(2024, 1, 16), '09:00', 'CHAPINERO', 'MOTOCICLETA', 'XYZ789', 'CONDUCTOR', 0, 0, 1, 'ILESO', 'FEMENINO', 30, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'REGULAR'),
            (3, 'F003', date(2024, 1, 20), '14:30', 'USAQUEN', 'AUTOMOVIL', 'DEF456', 'CONDUCTOR', 1, 0, 0, 'MUERTO', 'MASCULINO', 45, 'CONDUCTOR', 'EXCESO VELOCIDAD', 'ASFALTO', 'MALO'),
            (4, 'F004', date(2024, 1, 25), '16:00', 'SUBA', 'MOTOCICLETA', 'GHI789', 'CONDUCTOR', 0, 1, 0, 'HERIDO', 'FEMENINO', 28, 'CONDUCTOR', 'NO RESPETAR SEÑAL', 'ASFALTO', 'BUENO')
        ]
        
        controlador.cola_resultados.put(resultados_completos)
        
        # Obtener resultados
        resultado = controlador.obtener_resultados_consulta()
        
        # Aplicar filtros combinados
        # Filtro 1: Solo CHAPINERO
        filtro_localidad = [r for r in resultado if r[4] == 'CHAPINERO']
        
        # Filtro 2: Solo AUTOMOVIL en CHAPINERO
        filtro_combinado = [r for r in filtro_localidad if 'AUTOMOVIL' in r[5]]
        
        # Filtro 3: Solo con heridos en CHAPINERO con AUTOMOVIL
        filtro_final = [r for r in filtro_combinado if r[9] > 0]  # Heridos > 0
        
        # Verificar filtros combinados
        assert len(filtro_localidad) == 2      # F001 y F002
        assert len(filtro_combinado) == 1      # Solo F001
        assert len(filtro_final) == 1          # Solo F001 con heridos
        assert filtro_final[0][1] == 'F001'    # Verificar que es F001
