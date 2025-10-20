"""Controlador para la actualización de datos de siniestros viales."""

import threading
from src.models.update_model import ModeloActualizacion

class ControladorActualizacion:
    def __init__(self):
        self.modelo = ModeloActualizacion()
        self.actualizacion_en_progreso = False
        self.thread_actualizacion = None
        self.tabla_actual = None

    def iniciar_actualizacion(self, callback_progreso=None):
        """Inicia el proceso de actualización en un hilo separado."""
        if self.actualizacion_en_progreso:
            return False

        self.actualizacion_en_progreso = True
        self.tabla_actual = 'Accidente'

        def ejecutar_actualizacion():
            try:
                # Lista de tablas a procesar en orden
                tablas = [
                    ('Accidente', 'Accidente'),
                    ('Accidente_via', 'Accidente Via'),
                    ('Causa', 'Accidente Causa'),
                    ('AccidenteVehiculo', 'Accidente Vehiculo'),
                    ('ActorVial', 'Actor Vial')
                ]
                
                for tabla_key, tabla_nombre in tablas:
                    # Verificar cancelación antes de procesar cada tabla
                    if not self.actualizacion_en_progreso:
                        print(f"DEBUG: Actualización cancelada antes de procesar tabla {tabla_nombre}")
                        return False
                    
                    # Mostrar mensaje de inicio para la tabla actual
                    if callback_progreso:
                        callback_progreso(f"[INICIO] Iniciando actualización de la tabla '{tabla_nombre}'...", 0)
                    
                    # Procesar la tabla actual
                    resultado = self.modelo.actualizar_datos(tabla_key, callback_progreso, self)
                    
                    if not resultado:
                        if callback_progreso:
                            callback_progreso(f"[ERROR] Error al actualizar la tabla '{tabla_nombre}'", 0)
                        return False
                    
                    # Verificar cancelación después de procesar cada tabla
                    if not self.actualizacion_en_progreso:
                        print(f"DEBUG: Actualización cancelada después de tabla {tabla_nombre}")
                        return False
                
                # Si llegamos aquí, todas las tablas se procesaron exitosamente
                if callback_progreso:
                    callback_progreso("[ÉXITO] Actualización completada", 100)
                return True
            except Exception as e:
                if callback_progreso:
                    callback_progreso(f"Error inesperado: {str(e)}", 0)
                return False
            finally:
                self.actualizacion_en_progreso = False
                self.tabla_actual = None

        self.thread_actualizacion = threading.Thread(target=ejecutar_actualizacion)
        self.thread_actualizacion.start()
        return True

    def esta_actualizando(self):
        """Verifica si hay una actualización en progreso."""
        return self.actualizacion_en_progreso

    def cancelar_actualizacion(self):
        """Cancela la actualización en curso."""
        if self.actualizacion_en_progreso:
            print("DEBUG: Cancelando actualización...")
            self.actualizacion_en_progreso = False
            self.tabla_actual = None
            
            # No hacer join() aquí porque puede bloquear la interfaz
            # El hilo se detendrá naturalmente cuando vea que actualizacion_en_progreso es False
            if self.thread_actualizacion and self.thread_actualizacion.is_alive():
                print("DEBUG: Hilo de actualización marcado para cancelación")
            
            return True
        return False

    def iniciar_actualizacion_individual(self, tabla, callback_progreso=None):
        """Inicia el proceso de actualización de una tabla específica."""
        if self.actualizacion_en_progreso:
            return False

        self.actualizacion_en_progreso = True
        self.tabla_actual = tabla

        def ejecutar_actualizacion_individual():
            try:
                # Actualizar solo la tabla seleccionada
                if callback_progreso:
                    callback_progreso(f"[INICIO] Iniciando actualización de la tabla '{tabla}'...", 0)
                
                resultado = self.modelo.actualizar_datos(tabla, callback_progreso, self)
                
                if resultado:
                    if callback_progreso:
                        callback_progreso("Actualización completada exitosamente", 100)
                    return True
                else:
                    if callback_progreso:
                        callback_progreso(f"Error al actualizar la tabla '{tabla}'", 0)
                    return False
                    
            except Exception as e:
                if callback_progreso:
                    callback_progreso(f"Error: {str(e)}", 0)
                return False
            finally:
                self.actualizacion_en_progreso = False
                self.tabla_actual = None

        # Iniciar actualización en un hilo separado
        self.thread_actualizacion = threading.Thread(target=ejecutar_actualizacion_individual, daemon=True)
        self.thread_actualizacion.start()
        return True 