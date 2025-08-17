"""Modelo para operaciones con la base de datos."""

import psycopg2
from src.config.settings import PARAMETROS_BD, CONFIG_TABLAS

class GestorBaseDatos:
    def __init__(self):
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Establece conexión con la base de datos."""
        try:
            self.conexion = psycopg2.connect(
                dbname=PARAMETROS_BD['dbname'],
                user=PARAMETROS_BD['user'],
                password=PARAMETROS_BD['password'],
                host=PARAMETROS_BD['host'],
                port=PARAMETROS_BD['port']
            )
            self.cursor = self.conexion.cursor()
            return True
        except psycopg2.OperationalError as e:
            # Error específico de conexión
            raise Exception("Falló la conexión a la base de datos, valida con el administrador")
        except Exception as e:
            # Otros errores
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")
            else:
                raise Exception(f"Error al conectar a la base de datos: {str(e)}")

    def desconectar(self):
        """Cierra la conexión con la base de datos."""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()

    def obtener_siniestros_por_fecha(self, fecha_inicio, fecha_fin):
        """Obtiene los siniestros en un rango de fechas con información detallada."""
        try:
            if not self.conectar():
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")

            consulta = """
                SELECT  
                    a.objectid, 
                    a.formulario, 
                    a.fecha_ocurrencia_acc, 
                    a.hora_ocurrencia_acc, 
                    a.localidad,
                    v.clases,
                    v.placas,
                    ac.condiciones_a,
                    ac.fallecidos,
                    ac.heridos,
                    ac.ilesos,
                    ac.estados,
                    ac.generos,
                    ac.edades,
                    c.Causante,
                    c.Causa,
                    av.Terreno_via,
                    av.Estado_via
                FROM 
                    accidente a
                LEFT JOIN (
                    SELECT 
                        formulario,
                        STRING_AGG(DISTINCT clase, ', ') AS clases,
                        STRING_AGG(DISTINCT placa, ', ') AS placas
                    FROM 
                        vm_acc_vehiculo
                    GROUP BY 
                        formulario
                ) v ON a.formulario = v.formulario
                LEFT JOIN (
                    SELECT 
                        formulario,
                        STRING_AGG(DISTINCT condicion_a, ', ') AS condiciones_a,
                        COUNT(DISTINCT CASE WHEN estado = 'MUERTO' THEN objectid END) AS fallecidos,
                        COUNT(DISTINCT CASE WHEN estado = 'HERIDO' THEN objectid END) AS heridos,
                        COUNT(DISTINCT CASE WHEN estado = 'ILESO' THEN objectid END) AS ilesos,
                        STRING_AGG(DISTINCT estado, ', ') AS estados,
                        STRING_AGG(DISTINCT genero, ', ') AS generos,
                        STRING_AGG(DISTINCT edad::text, ', ') AS edades
                    FROM 
                        vm_acc_actor_vial
                    GROUP BY 
                        formulario
                ) ac ON a.formulario = ac.formulario
                LEFT JOIN (
                    SELECT 
                        formulario,
                        STRING_AGG(DISTINCT tipo_causa::text, ', ') AS Causante,
                        STRING_AGG(DISTINCT nombre::text, ', ') AS Causa
                    FROM 
                        vm_acc_causa
                    GROUP BY 
                        formulario
                ) c ON a.formulario = c.formulario
                LEFT JOIN (
                    SELECT 
                        formulario,
                        STRING_AGG(DISTINCT material::text, ', ') AS Terreno_via,
                        STRING_AGG(DISTINCT estado::text, ', ') AS Estado_via
                    FROM 
                        vm_acc_vial
                    GROUP BY 
                        formulario
                ) av ON a.formulario = av.formulario
                WHERE a.fecha_ocurrencia_acc BETWEEN %s AND %s
                ORDER BY a.fecha_ocurrencia_acc
            """

            self.cursor.execute(consulta, (fecha_inicio, fecha_fin))
            resultados = self.cursor.fetchall()
            return resultados

        except psycopg2.OperationalError as e:
            # Error específico de conexión
            raise Exception("Falló la conexión a la base de datos, valida con el administrador")
        except Exception as e:
            # Otros errores
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")
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
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")
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
                raise Exception("Falló la conexión a la base de datos, valida con el administrador")
            else:
                raise Exception(f"Error al consultar siniestros: {str(e)}") 