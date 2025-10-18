"""Controlador principal de la aplicación."""

from src.models.database import GestorBaseDatos
from src.models.api_client import ClienteAPI
from src.config.settings import CONFIG_TABLAS
import threading
import queue

class ControladorPrincipal:
    def __init__(self):
        self.gestor_bd = GestorBaseDatos()
        self.cliente_api = ClienteAPI()
        self.cola_resultados = queue.Queue()
        self.consulta_en_progreso = False
        self._conexion_pool = None  # Para reutilizar conexiones

    def actualizar_datos(self, nombre_tabla, callback_progreso=None):
        """Actualiza los datos de una tabla específica."""
        try:
            # Obtener registros de la API
            registros = self.cliente_api.obtener_registros(nombre_tabla, callback_progreso)
            if not registros:
                return None

            # Procesar y guardar en la base de datos
            config = CONFIG_TABLAS[nombre_tabla]
            resultado = self.gestor_bd.procesar_datos_api(
                nombre_tabla,
                registros,
                config['columnas'],
                callback_progreso
            )

            return resultado

        except Exception as e:
            # Capturar específicamente errores de conexión
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                print(f"Error en actualización de datos: {str(e)}")
                return None

    def consultar_siniestros(self, fecha_inicio, fecha_fin, callback_progreso=None):
        """Consulta siniestros en un rango de fechas en un hilo separado - OPTIMIZADO."""
        if self.consulta_en_progreso:
            return None

        self.consulta_en_progreso = True
        self.cola_resultados = queue.Queue()

        def ejecutar_consulta():
            try:
                # Usar método optimizado con límite para consultas grandes
                # Calcular diferencia de días para determinar si usar límite
                from datetime import datetime
                if isinstance(fecha_inicio, str):
                    fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                else:
                    fecha_inicio_obj = fecha_inicio
                    
                if isinstance(fecha_fin, str):
                    fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d')
                else:
                    fecha_fin_obj = fecha_fin
                
                diferencia_dias = (fecha_fin_obj - fecha_inicio_obj).days
                
                # Si el rango es muy grande (> 1 año), usar límite
                limite = None
                if diferencia_dias > 365:
                    limite = 50000  # Límite para rangos muy grandes
                    if callback_progreso:
                        callback_progreso(f"Rango grande detectado ({diferencia_dias} días). Aplicando límite de {limite} registros.", 0)
                
                resultados = self.gestor_bd.obtener_siniestros_por_fecha_optimizado(fecha_inicio, fecha_fin, limite)
                if resultados is None:
                    # Si no hay resultados, verificar si fue por error de conexión
                    raise Exception("No fue posible establecer conexión con la base de datos")
                self.cola_resultados.put(resultados)
            except Exception as e:
                # Capturar específicamente errores de conexión
                if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                    error_msg = "No fue posible establecer conexión con la base de datos"
                else:
                    error_msg = str(e)
                self.cola_resultados.put(Exception(error_msg))
            finally:
                self.consulta_en_progreso = False

        # Iniciar consulta en hilo separado
        threading.Thread(target=ejecutar_consulta, daemon=True).start()
        return self.cola_resultados

    def obtener_resultados_consulta(self):
        """Obtiene los resultados de la consulta si están disponibles."""
        try:
            return self.cola_resultados.get_nowait()
        except queue.Empty:
            return None 