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
                # Primera actualización: Accidente
                if callback_progreso:
                    callback_progreso("Iniciando actualización de la tabla 'Accidente'...", 0)
                
                resultado_accidente = self.modelo.actualizar_datos('Accidente', callback_progreso, self)
                
                if resultado_accidente:
                    # Verificar cancelación antes de continuar
                    if not self.actualizacion_en_progreso:
                        print("DEBUG: Actualización cancelada después de tabla Accidente")
                        return False
                        
                    # Segunda actualización: Accidente Via
                    if callback_progreso:
                        callback_progreso("Iniciando actualización de la tabla 'Accidente Via'...", 0)
                    
                    resultado_accidente_via = self.modelo.actualizar_datos('Accidente_via', callback_progreso, self)
                    
                    if resultado_accidente_via:
                        # Verificar cancelación antes de continuar
                        if not self.actualizacion_en_progreso:
                            print("DEBUG: Actualización cancelada después de tabla Accidente_via")
                            return False
                            
                        # Tercera actualización: Accidente Causa
                        if callback_progreso:
                            callback_progreso("Iniciando actualización de la tabla 'Accidente Causa'...", 0)
                        
                        resultado_accidente_causa = self.modelo.actualizar_datos('Causa', callback_progreso, self)
                        
                        if resultado_accidente_causa:
                            # Cuarta actualización: Accidente Vehiculo
                            if callback_progreso:
                                callback_progreso("Iniciando actualización de la tabla 'Accidente Vehiculo'...", 0)
                            
                            resultado_accidente_vehiculo = self.modelo.actualizar_datos('AccidenteVehiculo', callback_progreso, self)
                            
                            if resultado_accidente_vehiculo:
                                # Quinta actualización: Actor Vial
                                if callback_progreso:
                                    callback_progreso("Iniciando actualización de la tabla 'Actor Vial'...", 0)
                                
                                resultado_actor_vial = self.modelo.actualizar_datos('ActorVial', callback_progreso, self)
                                
                                if resultado_actor_vial:
                                    if callback_progreso:
                                        callback_progreso("Actualización completada exitosamente", 100)
                                    return True
                                else:
                                    if callback_progreso:
                                        callback_progreso("Error al actualizar la tabla 'Actor Vial'", 0)
                                    return False
                            else:
                                if callback_progreso:
                                    callback_progreso("Error al actualizar la tabla 'Accidente Vehiculo'", 0)
                                return False
                        else:
                            if callback_progreso:
                                callback_progreso("Error al actualizar la tabla 'Accidente Causa'", 0)
                            return False
                    else:
                        if callback_progreso:
                            callback_progreso("Error al actualizar la tabla 'Accidente Via'", 0)
                        return False
                else:
                    if callback_progreso:
                        callback_progreso("Error al actualizar la tabla 'Accidente'", 0)
                    return False
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