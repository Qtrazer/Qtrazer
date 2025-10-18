"""Modelo para operaciones con la base de datos."""

import psycopg2
from src.config.settings import get_database_params, CONFIG_TABLAS

class GestorBaseDatos:
    def __init__(self):
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Establece conexión con la base de datos."""
        try:
            # Obtener configuración actual en tiempo real
            config = get_database_params()
            
            if config is None:
                raise Exception("No hay configuración de base de datos. Por favor, configure la base de datos primero.")
            
            self.conexion = psycopg2.connect(
                dbname=config['dbname'],
                user=config['user'],
                password=config['password'],
                host=config['host'],
                port=config['port']
            )
            self.cursor = self.conexion.cursor()
            return True
        except psycopg2.OperationalError as e:
            # Error específico de conexión
            raise Exception("No fue posible establecer conexión con la base de datos")
        except Exception as e:
            # Otros errores
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                raise Exception(f"Error al conectar a la base de datos: {str(e)}")

    def desconectar(self):
        """Cierra la conexión con la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()

    def obtener_siniestros_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtiene los siniestros en un rango de fechas con información detallada - OPTIMIZADO SIN LÍMITES."""
        try:
            if not self.conectar():
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")

            # Consulta optimizada: Primero obtener los accidentes básicos con índice
            consulta_principal = """
                SELECT  
                    a.objectid, 
                    a.formulario, 
                    a.fecha_ocurrencia_acc, 
                    a.hora_ocurrencia_acc, 
                    a.localidad
                FROM accidente a
                WHERE a.fecha_ocurrencia_acc BETWEEN %s AND %s
                ORDER BY a.fecha_ocurrencia_acc
            """

            self.cursor.execute(consulta_principal, (fecha_inicio, fecha_fin))
            accidentes_basicos = self.cursor.fetchall()
            
            if not accidentes_basicos:
                return []

            # Procesar en lotes para manejar grandes volúmenes de datos
            BATCH_SIZE = 2000  # Tamaño de lote optimizado
            resultados = []
            
            for i in range(0, len(accidentes_basicos), BATCH_SIZE):
                lote = accidentes_basicos[i:i + BATCH_SIZE]
                formularios_lote = [acc[1] for acc in lote]
                
                if not formularios_lote:
                    continue
                    
                placeholders = ','.join(['%s'] * len(formularios_lote))
                
                # Consultas optimizadas para el lote actual
                consultas_lote = {
                    'vehiculos': f"""
                        SELECT formulario, STRING_AGG(DISTINCT clase, ', ') AS clases,
                               STRING_AGG(DISTINCT placa, ', ') AS placas
                        FROM vm_acc_vehiculo
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'actores': f"""
                        SELECT formulario, STRING_AGG(DISTINCT condicion_a, ', ') AS condiciones_a,
                               COUNT(DISTINCT CASE WHEN estado = 'MUERTO' THEN objectid END) AS fallecidos,
                               COUNT(DISTINCT CASE WHEN estado = 'HERIDO' THEN objectid END) AS heridos,
                               COUNT(DISTINCT CASE WHEN estado = 'ILESO' THEN objectid END) AS ilesos,
                               STRING_AGG(DISTINCT estado, ', ') AS estados,
                               STRING_AGG(DISTINCT genero, ', ') AS generos,
                               STRING_AGG(DISTINCT edad::text, ', ') AS edades
                        FROM vm_acc_actor_vial
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'causas': f"""
                        SELECT formulario, STRING_AGG(DISTINCT tipo_causa::text, ', ') AS Causante,
                               STRING_AGG(DISTINCT nombre::text, ', ') AS Causa
                        FROM vm_acc_causa
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'vias': f"""
                        SELECT formulario, STRING_AGG(DISTINCT material::text, ', ') AS Terreno_via,
                               STRING_AGG(DISTINCT estado::text, ', ') AS Estado_via
                        FROM vm_acc_vial
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """
                }
                
                # Ejecutar consultas del lote
                datos_lote = {}
                for tipo, consulta in consultas_lote.items():
                    self.cursor.execute(consulta, formularios_lote)
                    if tipo == 'vehiculos':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                    elif tipo == 'actores':
                        datos_lote[tipo] = {row[0]: (row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in self.cursor.fetchall()}
                    elif tipo == 'causas':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                    elif tipo == 'vias':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                
                # Combinar datos del lote
                for acc in lote:
                    formulario = acc[1]
                    
                    vehiculo_info = datos_lote['vehiculos'].get(formulario, (None, None))
                    actor_info = datos_lote['actores'].get(formulario, (None, None, None, None, None, None, None))
                    causa_info = datos_lote['causas'].get(formulario, (None, None))
                    via_info = datos_lote['vias'].get(formulario, (None, None))
                    
                    resultado = list(acc) + [
                        vehiculo_info[0], vehiculo_info[1],
                        actor_info[0], actor_info[1], actor_info[2], actor_info[3], 
                        actor_info[4], actor_info[5], actor_info[6],
                        causa_info[0], causa_info[1],
                        via_info[0], via_info[1]
                    ]
                    
                    resultados.append(tuple(resultado))
            
            return resultados

        except psycopg2.OperationalError as e:
            # Error específico de conexión
            raise Exception("No fue posible establecer conexión con la base de datos")
        except Exception as e:
            # Otros errores
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                raise Exception(f"Error al obtener siniestros: {str(e)}")
        finally:
            self.desconectar()

    def obtener_siniestros_por_fecha_optimizado(self, fecha_inicio, fecha_fin, limite=None):
        """Versión optimizada con límite opcional para consultas grandes."""
        try:
            if not self.conectar():
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")

            # Consulta optimizada con límite si se especifica
            consulta_principal = """
                SELECT  
                    a.objectid, 
                    a.formulario, 
                    a.fecha_ocurrencia_acc, 
                    a.hora_ocurrencia_acc, 
                    a.localidad
                FROM accidente a
                WHERE a.fecha_ocurrencia_acc BETWEEN %s AND %s
                ORDER BY a.fecha_ocurrencia_acc
            """
            
            if limite:
                consulta_principal += f" LIMIT {limite}"

            self.cursor.execute(consulta_principal, (fecha_inicio, fecha_fin))
            accidentes_basicos = self.cursor.fetchall()
            
            if not accidentes_basicos:
                return []

            # Procesar en lotes para evitar consultas muy grandes
            BATCH_SIZE = 1000
            resultados = []
            
            for i in range(0, len(accidentes_basicos), BATCH_SIZE):
                lote = accidentes_basicos[i:i + BATCH_SIZE]
                formularios_lote = [acc[1] for acc in lote]
                
                if not formularios_lote:
                    continue
                    
                placeholders = ','.join(['%s'] * len(formularios_lote))
                
                # Consultas optimizadas para el lote actual
                consultas_lote = {
                    'vehiculos': f"""
                        SELECT formulario, STRING_AGG(DISTINCT clase, ', ') AS clases,
                               STRING_AGG(DISTINCT placa, ', ') AS placas
                        FROM vm_acc_vehiculo
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'actores': f"""
                        SELECT formulario, STRING_AGG(DISTINCT condicion_a, ', ') AS condiciones_a,
                               COUNT(DISTINCT CASE WHEN estado = 'MUERTO' THEN objectid END) AS fallecidos,
                               COUNT(DISTINCT CASE WHEN estado = 'HERIDO' THEN objectid END) AS heridos,
                               COUNT(DISTINCT CASE WHEN estado = 'ILESO' THEN objectid END) AS ilesos,
                               STRING_AGG(DISTINCT estado, ', ') AS estados,
                               STRING_AGG(DISTINCT genero, ', ') AS generos,
                               STRING_AGG(DISTINCT edad::text, ', ') AS edades
                        FROM vm_acc_actor_vial
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'causas': f"""
                        SELECT formulario, STRING_AGG(DISTINCT tipo_causa::text, ', ') AS Causante,
                               STRING_AGG(DISTINCT nombre::text, ', ') AS Causa
                        FROM vm_acc_causa
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """,
                    'vias': f"""
                        SELECT formulario, STRING_AGG(DISTINCT material::text, ', ') AS Terreno_via,
                               STRING_AGG(DISTINCT estado::text, ', ') AS Estado_via
                        FROM vm_acc_vial
                        WHERE formulario IN ({placeholders})
                        GROUP BY formulario
                    """
                }
                
                # Ejecutar consultas del lote
                datos_lote = {}
                for tipo, consulta in consultas_lote.items():
                    self.cursor.execute(consulta, formularios_lote)
                    if tipo == 'vehiculos':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                    elif tipo == 'actores':
                        datos_lote[tipo] = {row[0]: (row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in self.cursor.fetchall()}
                    elif tipo == 'causas':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                    elif tipo == 'vias':
                        datos_lote[tipo] = {row[0]: (row[1], row[2]) for row in self.cursor.fetchall()}
                
                # Combinar datos del lote
                for acc in lote:
                    formulario = acc[1]
                    
                    vehiculo_info = datos_lote['vehiculos'].get(formulario, (None, None))
                    actor_info = datos_lote['actores'].get(formulario, (None, None, None, None, None, None, None))
                    causa_info = datos_lote['causas'].get(formulario, (None, None))
                    via_info = datos_lote['vias'].get(formulario, (None, None))
                    
                    resultado = list(acc) + [
                        vehiculo_info[0], vehiculo_info[1],
                        actor_info[0], actor_info[1], actor_info[2], actor_info[3], 
                        actor_info[4], actor_info[5], actor_info[6],
                        causa_info[0], causa_info[1],
                        via_info[0], via_info[1]
                    ]
                    
                    resultados.append(tuple(resultado))
            
            return resultados

        except psycopg2.OperationalError as e:
            raise Exception("No fue posible establecer conexión con la base de datos")
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                raise Exception(f"Error al obtener siniestros: {str(e)}")
        finally:
            self.desconectar()

    def procesar_datos_api(self, nombre_tabla, registros, columnas, callback_progreso=None):
        """Procesa y guarda los datos de la API en la base de datos."""
        try:
            if not self.conectar():
                return None

            config = CONFIG_TABLAS[nombre_tabla]
            nombre_tabla_bd = config['nombre_tabla']
            columnas_tabla = config['columnas']

            # Obtener total de registros actuales
            self.cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla_bd}")
            total_actual = self.cursor.fetchone()[0]

            # Insertar nuevos registros
            registros_insertados = 0
            for i, registro in enumerate(registros, 1):
                valores = [registro.get(col) for col in columnas_tabla]
                placeholders = ', '.join(['%s'] * len(valores))
                columnas_str = ', '.join(columnas_tabla)

                consulta = f"""
                    INSERT INTO {nombre_tabla_bd} ({columnas_str})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                self.cursor.execute(consulta, valores)
                if self.cursor.rowcount > 0:
                    registros_insertados += 1

                if callback_progreso:
                    callback_progreso('db', i, len(registros))

            self.conexion.commit()

            return {
                'total_registros': len(registros),
                'nuevos_registros': registros_insertados,
                'total_en_bd': total_actual + registros_insertados,
                'registros_insertados': registros_insertados
            }

        except Exception as e:
            # Capturar específicamente errores de conexión
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                print(f"Error al procesar datos: {str(e)}")
                if self.conexion:
                    self.conexion.rollback()
                return None
        finally:
            self.desconectar()

    def consultar_siniestros(self, fecha_inicio, fecha_fin):
        """Consulta los siniestros en un rango de fechas."""
        try:
            with self.conexion.cursor() as cursor:
                consulta = """
                    SELECT 
                        s.id,
                        s.formulario,
                        s.fecha,
                        s.hora,
                        s.localidad,
                        s.clases_vehiculos,
                        s.placas,
                        s.condiciones_actores,
                        s.fallecidos,
                        s.heridos,
                        s.ilesos,
                        s.estados,
                        s.generos,
                        s.edades,
                        s.causante,
                        s.causa,
                        s.terreno_via,
                        s.estado_via
                    FROM siniestros s
                    WHERE s.fecha BETWEEN %s AND %s
                    ORDER BY s.fecha DESC, s.hora DESC
                """
                cursor.execute(consulta, (fecha_inicio, fecha_fin))
                return cursor.fetchall()
        except Exception as e:
            # Capturar específicamente errores de conexión
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("No fue posible establecer conexión con la base de datos")
            else:
                raise Exception(f"Error al consultar siniestros: {str(e)}") 