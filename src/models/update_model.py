"""Modelo para la actualización de datos de siniestros viales."""

import psycopg2
import requests
import pandas as pd
from datetime import datetime
import time
import sys
import os
import sys

# Agregar el directorio raíz al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import get_database_params, CONFIG_TABLAS, CAMPOS_API, COLUMNAS_FECHA, API_URLS, CAMPOS_API_ACTOR_VIAL

class ModeloActualizacion:
    def __init__(self):
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5  # segundos
        self.PAGE_SIZE = 1000  # número de registros por página (optimizado para APIs rápidas)
        self.REQUEST_DELAY = 0.5  # segundos entre solicitudes (reducido para APIs rápidas)
        self.API_TIMEOUT = 60  # timeout aumentado para APIs lentas
        self.MAX_INITIAL_RECORDS = 50000  # límite para carga inicial masiva
        self.DIAS = {
            'LUNES': 1, 'MARTES': 2, 'MIERCOLES': 3, 'JUEVES': 4,
            'VIERNES': 5, 'SABADO': 6, 'DOMINGO': 7
        }

    def convertir_dia_a_numero(self, dia):
        """Convierte el nombre del día a su número correspondiente"""
        if isinstance(dia, str):
            return self.DIAS.get(dia.upper(), 0)
        return 0

    def obtener_campos_fecha_por_tabla(self, tabla):
        """Obtiene los campos de fecha específicos para cada tabla"""
        campos_fecha_por_tabla = {
            'Accidente': ['fecha_ocurrencia_acc', 'fecha_hora_acc'],
            'ActorVial': ['fecha_posterior_muerte', 'fecha_nacimiento'],
            'Causa': [],  # No tiene campos de fecha
            'AccidenteVehiculo': [],  # No tiene campos de fecha
            'Accidente_via': []  # No tiene campos de fecha
        }
        return campos_fecha_por_tabla.get(tabla, [])

    def limpiar_valores_fecha(self, df, campos_fecha):
        """Limpia valores vacíos e inválidos en campos de fecha para todas las tablas.
        También convierte timestamps de milisegundos a formatos de fecha apropiados.
        """
        print(f"DEBUG: Limpiando campos de fecha: {campos_fecha}")
        
        for columna in campos_fecha:
            if columna in df.columns:
                print(f"DEBUG: Procesando columna {columna}")
                print(f"DEBUG: Valores únicos antes de limpieza: {df[columna].unique()[:10]}")
                
                try:
                    # Limpiar la columna: reemplazar cadenas vacías y valores inválidos con None
                    df[columna] = df[columna].replace('', None)
                    df[columna] = df[columna].replace('null', None)
                    df[columna] = df[columna].replace('NULL', None)
                    df[columna] = df[columna].replace('None', None)
                    df[columna] = df[columna].replace('nan', None)
                    df[columna] = df[columna].replace('NaN', None)
                    
                    # Convertir valores que son solo espacios en blanco a None
                    df[columna] = df[columna].apply(lambda x: None if isinstance(x, str) and x.strip() == '' else x)
                    
                    print(f"DEBUG: Valores únicos después de limpieza: {df[columna].unique()[:10]}")
                    
                    # Verificar si hay timestamps de milisegundos para convertir
                    mask_not_null = df[columna].notna()
                    if mask_not_null.any():
                        valores_not_null = df.loc[mask_not_null, columna]
                        
                        # Verificar si los valores son timestamps numéricos
                        valores_numericos = pd.to_numeric(valores_not_null, errors='coerce')
                        mask_numeric = valores_numericos.notna()
                        mask_positive = valores_numericos > 0
                        mask_timestamp = mask_numeric & mask_positive
                        
                        # Verificar si los valores parecen ser timestamps (mayores a 1000000000000 para milisegundos)
                        if mask_timestamp.any():
                            timestamps = valores_numericos[mask_timestamp]
                            # Verificar si son timestamps de milisegundos (13 dígitos)
                            mask_milliseconds = (timestamps >= 1000000000000) & (timestamps < 10000000000000)
                            
                            if mask_milliseconds.any():
                                print(f"DEBUG: Detectados timestamps de milisegundos en {columna}")
                                # Convertir timestamps de milisegundos a datetime
                                timestamps_validos = timestamps[mask_milliseconds]
                                fechas_convertidas = pd.to_datetime(timestamps_validos, unit='ms')
                                
                                # Asignar las fechas convertidas
                                indices_validos = df.loc[mask_not_null & mask_timestamp & mask_milliseconds, columna].index
                                df.loc[indices_validos, columna] = fechas_convertidas
                                
                                # Formatear según el tipo de columna
                                if columna in ['fecha_ocurrencia_acc', 'fecha_posterior_muerte', 'fecha_nacimiento']:
                                    # Formato DATE: YYYY-MM-DD
                                    df.loc[indices_validos, columna] = fechas_convertidas.dt.strftime('%Y-%m-%d')
                                    print(f"DEBUG: Formateado como DATE: {df.loc[indices_validos, columna].iloc[0] if len(indices_validos) > 0 else 'N/A'}")
                                elif columna in ['fecha_hora_acc']:
                                    # Formato TIMESTAMP: YYYY-MM-DD HH:MM:SS
                                    df.loc[indices_validos, columna] = fechas_convertidas.dt.strftime('%Y-%m-%d %H:%M:%S')
                                    print(f"DEBUG: Formateado como TIMESTAMP: {df.loc[indices_validos, columna].iloc[0] if len(indices_validos) > 0 else 'N/A'}")
                                
                                # Convertir valores que no son timestamps válidos a None
                                df.loc[mask_not_null & mask_timestamp & ~mask_milliseconds, columna] = None
                    
                    # Reemplazar NaT con None
                    df[columna] = df[columna].where(df[columna].notna(), None)
                    
                    print(f"DEBUG: Valores finales de {columna}: {df[columna].unique()[:10]}")
                    
                except Exception as e:
                    print(f"\nAdvertencia: No se pudo limpiar la columna {columna}: {str(e)}")
                    # En caso de error, convertir a None para evitar errores de inserción
                    df[columna] = None
        
        return df

    def formatear_fechas(self, df):
        """Formatea las columnas de fecha al formato correcto para PostgreSQL.
        Convierte timestamps de milisegundos de la API a formatos de fecha/datetime de PostgreSQL.
        """
        print(f"DEBUG: Iniciando formateo de fechas. Columnas: {list(df.columns)}")
        
        for columna in COLUMNAS_FECHA:
            if columna in df.columns:
                print(f"DEBUG: Procesando columna {columna}")
                print(f"DEBUG: Valores únicos antes de limpieza: {df[columna].unique()[:10]}")
                
                try:
                    # Limpiar la columna: reemplazar cadenas vacías y valores inválidos con None
                    df[columna] = df[columna].replace('', None)
                    df[columna] = df[columna].replace('null', None)
                    df[columna] = df[columna].replace('NULL', None)
                    df[columna] = df[columna].replace('None', None)
                    df[columna] = df[columna].replace('nan', None)
                    df[columna] = df[columna].replace('NaN', None)
                    
                    # Convertir valores que son solo espacios en blanco a None
                    df[columna] = df[columna].apply(lambda x: None if isinstance(x, str) and x.strip() == '' else x)
                    
                    print(f"DEBUG: Valores únicos después de limpieza: {df[columna].unique()[:10]}")
                    
                    # Verificar si la columna tiene valores válidos después de la limpieza
                    if df[columna].isna().all():
                        print(f"DEBUG: Todos los valores de {columna} son None/NaN")
                        df[columna] = None
                        continue
                    
                    # Convertir valores no nulos de milisegundos a datetime
                    mask_not_null = df[columna].notna()
                    if mask_not_null.any():
                        valores_not_null = df.loc[mask_not_null, columna]
                        print(f"DEBUG: Valores no nulos de {columna}: {valores_not_null.unique()[:5]}")
                        
                        # Convertir a numérico para verificar si son timestamps válidos
                        valores_numericos = pd.to_numeric(valores_not_null, errors='coerce')
                        mask_numeric = valores_numericos.notna()
                        mask_positive = valores_numericos > 0
                        mask_valid = mask_numeric & mask_positive
                        
                        print(f"DEBUG: Máscara válida para {columna}: {mask_valid.sum()} valores válidos de {len(mask_valid)}")
                        
                        if mask_valid.any():
                            # Convertir de milisegundos a datetime solo para valores válidos
                            timestamps_validos = valores_numericos[mask_valid]
                            fechas_convertidas = pd.to_datetime(timestamps_validos, unit='ms')
                            
                            # Asignar las fechas convertidas de vuelta al DataFrame
                            indices_validos = df.loc[mask_not_null & mask_valid, columna].index
                            df.loc[indices_validos, columna] = fechas_convertidas
                            
                            # Formatear según el tipo de columna
                            if columna in ['FECHA_OCURRENCIA_ACC', 'FECHA_POSTERIOR_MUERTE', 'FECHA_NACIMIENTO']:
                                # Formato DATE: YYYY-MM-DD
                                df.loc[indices_validos, columna] = fechas_convertidas.dt.strftime('%Y-%m-%d')
                                print(f"DEBUG: Formateado como DATE: {df.loc[indices_validos, columna].iloc[0] if len(indices_validos) > 0 else 'N/A'}")
                            elif columna in ['FECHA_HORA_ACC']:
                                # Formato TIMESTAMP: YYYY-MM-DD HH:MM:SS
                                df.loc[indices_validos, columna] = fechas_convertidas.dt.strftime('%Y-%m-%d %H:%M:%S')
                                print(f"DEBUG: Formateado como TIMESTAMP: {df.loc[indices_validos, columna].iloc[0] if len(indices_validos) > 0 else 'N/A'}")
                        
                        # Convertir valores inválidos a None
                        df.loc[mask_not_null & ~mask_valid, columna] = None
                        print(f"DEBUG: Valores inválidos convertidos a None: {(~mask_valid).sum()}")
                    
                    # Reemplazar NaT con None (que se convertirá a NULL en PostgreSQL)
                    df[columna] = df[columna].where(df[columna].notna(), None)
                    
                    print(f"DEBUG: Valores finales de {columna}: {df[columna].unique()[:10]}")
                    
                except Exception as e:
                    print(f"\nAdvertencia: No se pudo formatear la columna {columna}: {str(e)}")
                    # En caso de error, convertir a None para evitar errores de inserción
                    df[columna] = None
        return df

    def insertar_registros(self, df, config_tabla, callback_progreso=None):
        """Inserta los registros en la base de datos"""
        try:
            config = get_database_params()
            if config is None:
                raise Exception("No hay configuración de base de datos. Por favor, configure la base de datos primero.")
            
            # Validar conexión antes de insertar
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Verificar que la conexión funciona
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            # Mapear los nombres de columnas de la API a los nombres de la base de datos
            mapeo_columnas = {}
            if config_tabla == 'Accidente':
                mapeo_columnas = {
                    'OBJECTID': 'objectid',
                    'FORMULARIO': 'formulario',
                    'CODIGO_ACCIDENTE': 'codigo_accidente',
                    'FECHA_OCURRENCIA_ACC': 'fecha_ocurrencia_acc',
                    'HORA_OCURRENCIA_ACC': 'hora_ocurrencia_acc',
                    'ANO_OCURRENCIA_ACC': 'ano_ocurrencia_acc',
                    'MES_OCURRENCIA_ACC': 'mes_ocurrencia_acc',
                    'DIA_OCURRENCIA_ACC': 'dia_ocurrencia_acc',
                    'DIRECCION': 'direccion',
                    'GRAVEDAD': 'gravedad',
                    'CLASE_ACC': 'clase_acc',
                    'LOCALIDAD': 'localidad',
                    'MUNICIPIO': 'municipio',
                    'FECHA_HORA_ACC': 'fecha_hora_acc',
                    'LATITUD': 'latitud',
                    'LONGITUD': 'longitud',
                    'CIV': 'civ',
                    'PK_CALZADA': 'pk_calzada'
                }
            elif config_tabla == 'Accidente_via':
                mapeo_columnas = {
                    'OBJECTID': 'objectid',
                    'FORMULARIO': 'formulario',
                    'CODIGO_ACCIDENTE': 'codigo_accidente',
                    'CODIGO_VIA': 'codigo_via',
                    'GEOMETRICA_A': 'geometrica_a',
                    'GEOMETRICA_B': 'geometrica_b',
                    'GEOMETRICA_C': 'geometrica_c',
                    'UTILIZACION': 'utilizacion',
                    'CALZADAS': 'calzadas',
                    'CARRILES': 'carriles',
                    'MATERIAL': 'material',
                    'ESTADO': 'estado',
                    'CONDICIONES': 'condiciones',
                    'ILUMINACION_A': 'iluminacion_a',
                    'ILUMINACION_B': 'iluminacion_b',
                    'AGENTE_TRANSITO': 'agente_transito',
                    'SEMAFORO': 'semaforo',
                    'VISUAL': 'visual',
                    'CODIGO': 'codigo'
                }
            elif config_tabla == 'Causa':
                mapeo_columnas = {
                    'CODIGO_AC_VH': 'codigo_ac_vh',
                    'OBJECTID': 'objectid',
                    'FORMULARIO': 'formulario',
                    'CODIGO_ACCIDENTE': 'codigo_accidente',
                    'CODIGO_VEHICULO': 'codigo_vehiculo',
                    'CODIGO_CAUSA': 'codigo_causa',
                    'NOMBRE': 'nombre',
                    'TIPO': 'tipo',
                    'DESCRIPCION2': 'descripcion2',
                    'TIPO_CAUSA': 'tipo_causa',
                    'CODIGO': 'codigo'
                }
            elif config_tabla == 'AccidenteVehiculo':
                mapeo_columnas = {
                    'OBJECTID': 'objectid',
                    'FORMULARIO': 'formulario',
                    'PLACA': 'placa',
                    'CODIGO_VEHICULO': 'codigo_vehiculo',
                    'CLASE': 'clase',
                    'SERVICIO': 'servicio',
                    'MODALIDAD': 'modalidad',
                    'ENFUGA': 'enfuga',
                    'CODIGO': 'codigo'
                }
            elif config_tabla == 'ActorVial':
                mapeo_columnas = {
                    'CONDICION_A': 'condicion_a',
                    'OBJECTID': 'objectid',
                    'FORMULARIO': 'formulario',
                    'CODIGO_ACCIDENTADO': 'codigo_accidentado',
                    'CODIGO_VICTIMA': 'codigo_victima',
                    'CODIGO_VEHICULO': 'codigo_vehiculo',
                    'CONDICION': 'condicion',
                    'ESTADO': 'estado',
                    'MUERTE_POSTERIOR': 'muerte_posterior',
                    'FECHA_POSTERIOR_MUERTE': 'fecha_posterior_muerte',
                    'GENERO': 'genero',
                    'FECHA_NACIMIENTO': 'fecha_nacimiento',
                    'EDAD': 'edad',
                    'CODIGO': 'codigo'
                }
            
            # Renombrar las columnas del DataFrame - solo mapear campos que existen
            print(f"DEBUG: Columnas disponibles en DataFrame: {list(df.columns)}")
            print(f"DEBUG: Mapeo de columnas disponible: {mapeo_columnas}")
            
            # Crear un mapeo filtrado solo con las columnas que existen en el DataFrame
            mapeo_filtrado = {k: v for k, v in mapeo_columnas.items() if k in df.columns}
            print(f"DEBUG: Mapeo filtrado aplicado: {mapeo_filtrado}")
            
            # Renombrar solo las columnas que existen
            df = df.rename(columns=mapeo_filtrado)
            
            # Eliminar columnas que no están en el mapeo (campos extra de la API)
            columnas_mapeadas = set(mapeo_filtrado.values())
            columnas_a_eliminar = [col for col in df.columns if col not in columnas_mapeadas]
            if columnas_a_eliminar:
                print(f"DEBUG: Eliminando columnas no mapeadas: {columnas_a_eliminar}")
                df = df.drop(columns=columnas_a_eliminar)
            
            # Debug: Verificar valores de fecha_nacimiento después del mapeo
            if 'fecha_nacimiento' in df.columns:
                print(f"DEBUG: Valores de fecha_nacimiento después del mapeo:")
                print(f"DEBUG: Tipo: {df['fecha_nacimiento'].dtype}")
                print(f"DEBUG: Muestra: {df['fecha_nacimiento'].head(5).tolist()}")
                print(f"DEBUG: Valores únicos: {df['fecha_nacimiento'].unique()[:10]}")
                print(f"DEBUG: ¿Hay cadenas vacías?: {'Sí' if (df['fecha_nacimiento'] == '').any() else 'No'}")
                print(f"DEBUG: ¿Hay valores None?: {'Sí' if df['fecha_nacimiento'].isna().any() else 'No'}")
            
            # Asegurar que todos los campos numéricos se manejen correctamente
            df['objectid'] = df['objectid'].fillna(0).astype(int)
            
            # Manejar campos específicos según la tabla
            if config_tabla == 'Accidente':
                # Campos numéricos
                df['codigo_accidente'] = df['codigo_accidente'].fillna(0).astype(int)
                df['ano_ocurrencia_acc'] = df['ano_ocurrencia_acc'].fillna(0).astype(int)
                df['dia_ocurrencia_acc'] = df['dia_ocurrencia_acc'].apply(self.convertir_dia_a_numero)
                df['civ'] = df['civ'].fillna(0).astype(int)
                df['pk_calzada'] = df['pk_calzada'].fillna(0).astype(int)
                
                # Campos de texto
                df['mes_ocurrencia_acc'] = df['mes_ocurrencia_acc'].fillna('')
                df['direccion'] = df['direccion'].fillna('')
                df['gravedad'] = df['gravedad'].fillna('')
                df['clase_acc'] = df['clase_acc'].fillna('')
                df['localidad'] = df['localidad'].fillna('')
                df['municipio'] = df['municipio'].fillna('')
                df['latitud'] = df['latitud'].fillna('')
                df['longitud'] = df['longitud'].fillna('')
            elif config_tabla == 'AccidenteVehiculo':
                df['codigo_vehiculo'] = df['codigo_vehiculo'].fillna(0).astype(int)
                df['enfuga'] = df['enfuga'].fillna('').astype(str)
            elif config_tabla == 'ActorVial':
                df['codigo_vehiculo'] = df['codigo_vehiculo'].fillna(0).astype(int)
                df['codigo_accidentado'] = df['codigo_accidentado'].fillna(0).astype(int)
                df['codigo_victima'] = df['codigo_victima'].fillna(0).astype(int)
                df['edad'] = df['edad'].fillna(0).astype(int)
            elif config_tabla == 'Causa':
                df['codigo_vehiculo'] = df['codigo_vehiculo'].fillna(0).astype(int)
                df['codigo_causa'] = df['codigo_causa'].fillna(0).astype(int)
            elif config_tabla == 'Accidente_via':
                df['codigo_via'] = df['codigo_via'].fillna(0).astype(int)

            
            # Obtener campos de fecha para la tabla actual
            campos_fecha = self.obtener_campos_fecha_por_tabla(config_tabla)
            
            # Limpiar campos de fecha específicos
            if campos_fecha:
                df = self.limpiar_valores_fecha(df, campos_fecha)
            
            # Limpiar valores vacíos e inválidos en todas las columnas
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Para campos de fecha, ya fueron limpiados arriba
                    if col not in campos_fecha:
                        # Para otros campos de texto, reemplazar con cadenas vacías
                        df[col] = df[col].fillna('')
            
            # Preparar la consulta de inserción - solo usar columnas que existen en el DataFrame
            columnas_config = CONFIG_TABLAS[config_tabla]['columnas']
            columnas_df = list(df.columns)
            
            # Filtrar solo las columnas que existen tanto en la configuración como en el DataFrame
            columnas_validas = [col for col in columnas_config if col in columnas_df]
            
            print(f"DEBUG: Columnas en configuración: {columnas_config}")
            print(f"DEBUG: Columnas en DataFrame: {columnas_df}")
            print(f"DEBUG: Columnas válidas para inserción: {columnas_validas}")
            
            if not columnas_validas:
                raise Exception(f"No hay columnas válidas para insertar en la tabla {config_tabla}")
            
            placeholders = ', '.join(['%s'] * len(columnas_validas))
            columnas_str = ', '.join(columnas_validas)
            
            consulta = f"""
                INSERT INTO {CONFIG_TABLAS[config_tabla]['nombre_tabla']} ({columnas_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            
            # Insertar registros
            total_registros = len(df)
            registros_insertados = 0
            lote_size = 1000  # Tamaño del lote para insertar
            
            if callback_progreso:
                callback_progreso(f"Iniciando inserción de {total_registros} registros en la base de datos...", 0)
                callback_progreso(f"[INFO] Registros insertados: 0/{total_registros}", 0)
            
            for i in range(0, total_registros, lote_size):
                lote = df.iloc[i:i + lote_size]
                registros_en_lote = len(lote)
                
                for _, fila in lote.iterrows():
                    valores = [fila[col] for col in columnas_validas]
                    
                    # Limpiar valores vacíos e inválidos: reemplazar con None
                    for i, valor in enumerate(valores):
                        if valor == '' or valor == 'null' or valor == 'NULL' or valor == 'None':
                            valores[i] = None
                        elif isinstance(valor, str) and valor.strip() == '':
                            valores[i] = None
                        elif isinstance(valor, str) and len(valor) > 20:
                            # DEBUG: Identificar campos que exceden 20 caracteres
                            nombre_campo = columnas_validas[i]
                            print(f"DEBUG: Campo '{nombre_campo}' excede 20 caracteres: '{valor}' (longitud: {len(valor)})")
                            # Truncar a 20 caracteres para evitar error de base de datos
                            valores[i] = valor[:20]
                            print(f"DEBUG: Campo '{nombre_campo}' truncado a: '{valores[i]}'")
                    
                    try:
                        cursor.execute(consulta, valores)
                        if cursor.rowcount > 0:
                            registros_insertados += 1
                            # Actualizar progreso cada 100 registros
                            if registros_insertados % 100 == 0:
                                porcentaje = (registros_insertados / total_registros) * 100
                                if callback_progreso:
                                    callback_progreso(f"[INFO] Registros insertados: {registros_insertados}/{total_registros} ({porcentaje:.1f}%)", porcentaje)
                    except Exception as e:
                        # DEBUG: Mostrar información detallada del error de inserción
                        print(f"DEBUG: Error al insertar registro:")
                        print(f"DEBUG: Columnas: {columnas_validas}")
                        print(f"DEBUG: Valores: {valores}")
                        for j, (col, val) in enumerate(zip(columnas_validas, valores)):
                            if isinstance(val, str) and len(val) > 20:
                                print(f"DEBUG: PROBLEMA - Campo '{col}' tiene {len(val)} caracteres: '{val}'")
                        raise e
                
                conn.commit()
            
            # Mostrar el total final
            if callback_progreso:
                callback_progreso(f"[INFO] Total de registros insertados: {registros_insertados}/{total_registros} (100%)", 100)
            
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = "No fue posible establecer conexión con la base de datos"
            print(f"Error de conexión: {str(e)}")
            if callback_progreso:
                callback_progreso(f"[ERROR] {error_msg}", 0)
            return False
        except psycopg2.Error as e:
            error_msg = "No fue posible establecer conexión con la base de datos"
            print(f"Error de base de datos: {str(e)}")
            if callback_progreso:
                callback_progreso(f"[ERROR] {error_msg}", 0)
            return False
        except Exception as e:
            print(f"Error al insertar registros: {str(e)}")
            if callback_progreso:
                callback_progreso(f"Error al insertar registros: {str(e)}", 0)
            return False
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_total_records(self, api_url):
        """Obtiene el número total de registros en la API"""
        params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('count', 0)
        except Exception as e:
            print(f"Error al obtener el total de registros: {str(e)}")
            return 0

    def get_latest_objectid(self, tabla):
        """Obtiene el ObjectID más reciente de la tabla especificada"""
        try:
            config = get_database_params()
            if config is None:
                raise Exception("No hay configuración de base de datos. Por favor, configure la base de datos primero.")
            
            print(f"DEBUG: Conectando a base de datos: {config['dbname']} en {config['host']}")
            
            # Validar conexión con timeout
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Verificar que la conexión funciona con una consulta simple
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            nombre_tabla = CONFIG_TABLAS[tabla]['nombre_tabla']
            print(f"DEBUG: Buscando ObjectID más reciente en tabla: {nombre_tabla}")
            
            # Verificar si la tabla existe y tiene datos
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{nombre_tabla}'
            """)
            tabla_existe = cursor.fetchone()[0] > 0
            
            if not tabla_existe:
                print(f"DEBUG: La tabla {nombre_tabla} no existe, usando ObjectID = 0 para obtener todos los datos")
                latest_objectid = 0
            else:
                # Verificar si la tabla tiene datos
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                total_registros = cursor.fetchone()[0]
                
                if total_registros == 0:
                    print(f"DEBUG: La tabla {nombre_tabla} está vacía, usando ObjectID = 0 para obtener todos los datos")
                    latest_objectid = 0
                else:
                    # Obtener el ObjectID más reciente
                    cursor.execute(f"SELECT MAX(objectid) FROM {nombre_tabla}")
                    result = cursor.fetchone()
                    
                    if result is None or result[0] is None:
                        print(f"DEBUG: No se encontró ObjectID válido en {nombre_tabla}, usando ObjectID = 0")
                        latest_objectid = 0
                    else:
                        latest_objectid = result[0]
                        print(f"DEBUG: ObjectID más reciente encontrado en {nombre_tabla}: {latest_objectid}")
            
            cursor.close()
            conn.close()
            return latest_objectid
            
        except psycopg2.OperationalError as e:
            print(f"Error de conexión a la base de datos: {str(e)}")
            raise Exception("No fue posible establecer conexión con la base de datos")
        except psycopg2.Error as e:
            print(f"Error de base de datos: {str(e)}")
            raise Exception("No fue posible establecer conexión con la base de datos")
        except Exception as e:
            print(f"Error al obtener el ObjectID más reciente: {str(e)}")
            # En caso de error, usar ObjectID = 0 para obtener todos los datos
            print("DEBUG: Usando ObjectID = 0 debido a error en consulta")
            return 0

    def get_new_records(self, api_url, last_objectid, campos_api, callback_progreso=None):
        """Obtiene los registros completos mayores al último ObjectID con paginación"""
        all_records = []
        offset = 0
        total_fetched = 0
        
        # Determinar la condición WHERE según el ObjectID
        if last_objectid == 0:
            # Si ObjectID es 0, significa que la tabla está vacía
            # Para tablas vacías, obtener TODOS los registros desde el ObjectID 1
            where_condition = "OBJECTID >= 1"  # Obtener primeros registros desde ObjectID 1
            print("DEBUG: Tabla vacía detectada, obteniendo TODOS los registros desde ObjectID 1")
            print("DEBUG: ADVERTENCIA: Si hay muchos registros, esto puede tomar mucho tiempo")
        else:
            # Si hay ObjectID, obtener solo los registros nuevos
            where_condition = f"OBJECTID > {last_objectid}"
            print(f"DEBUG: Obteniendo registros con ObjectID > {last_objectid}")
        
        # Primero obtenemos el total de registros nuevos
        params = {
            'where': where_condition,
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            print(f"DEBUG: Solicitando conteo total de registros desde API: {api_url}")
            print(f"DEBUG: Parámetros de consulta: {params}")
            
            response = requests.get(api_url, params=params, timeout=self.API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            total_records = data.get('count', 0)
            
            print(f"DEBUG: Total de registros encontrados en API: {total_records}")
            
            # Para tablas vacías, obtener TODOS los registros sin límites
            if last_objectid == 0:
                print(f"DEBUG: Tabla vacía - obteniendo TODOS los {total_records:,} registros disponibles")
                if callback_progreso:
                    callback_progreso(f"Tabla vacía detectada - se obtendrán TODOS los {total_records:,} registros", 0)
            
            if callback_progreso:
                callback_progreso(f"Total de registros a obtener: {total_records}", 0)
            
            # Inicializar tiempo de inicio
            self.start_time = time.time()
            
            # Obtenemos los registros por lotes
            lotes_sin_registros = 0  # Contador de lotes consecutivos sin registros
            MAX_LOTES_SIN_REGISTROS = 3  # Máximo de lotes sin registros antes de terminar
            
            while total_fetched < total_records:
                # Verificar si hay una cancelación (si se pasa el controlador)
                if callback_progreso and hasattr(callback_progreso, '__self__') and hasattr(callback_progreso.__self__, 'esta_actualizando'):
                    if not callback_progreso.__self__.esta_actualizando():
                        print("DEBUG: Actualización cancelada durante obtención de registros")
                        return all_records
                
                params = {
                    'where': where_condition,
                    'outFields': ','.join(campos_api),
                    'f': 'json',
                    'returnGeometry': 'false',
                    'resultOffset': offset,
                    'resultRecordCount': self.PAGE_SIZE
                }
                
                lote_obtenido = False
                for attempt in range(self.MAX_RETRIES):
                    try:
                        print(f"DEBUG: Solicitando lote {offset//self.PAGE_SIZE + 1} (offset: {offset}, límite: {self.PAGE_SIZE})")
                        print(f"DEBUG: Parámetros del lote: {params}")
                        
                        response = requests.get(api_url, params=params, timeout=self.API_TIMEOUT)
                        response.raise_for_status()
                        data = response.json()
                        
                        # DEBUG: Verificar si hay errores en la respuesta
                        if 'error' in data:
                            print(f"DEBUG: ERROR en respuesta de API: {data['error']}")
                            return all_records
                        
                        # DEBUG: Mostrar la respuesta completa de la API
                        print(f"DEBUG: Respuesta de la API: {str(data)[:500]}...")
                        
                        features = data.get('features', [])
                        print(f"DEBUG: Features encontradas: {len(features)}")
                        
                        # DEBUG: Mostrar una feature de ejemplo si existe
                        if features:
                            print(f"DEBUG: Ejemplo de feature: {features[0]}")
                        
                        records = [feature['attributes'] for feature in features]
                        print(f"DEBUG: Registros procesados: {len(records)}")
                        
                        all_records.extend(records)
                        
                        total_fetched += len(records)
                        offset += len(records)
                        
                        print(f"DEBUG: Lote obtenido exitosamente: {len(records)} registros")
                        print(f"DEBUG: Total acumulado: {total_fetched}/{total_records}")
                        
                        # Si no se obtuvieron registros, incrementar contador
                        if len(records) == 0:
                            lotes_sin_registros += 1
                            print(f"DEBUG: Lote sin registros #{lotes_sin_registros}")
                            
                            # Si hemos tenido demasiados lotes sin registros, terminar
                            if lotes_sin_registros >= MAX_LOTES_SIN_REGISTROS:
                                print(f"DEBUG: Se han obtenido {MAX_LOTES_SIN_REGISTROS} lotes consecutivos sin registros. Terminando obtención.")
                                return all_records
                            
                            # Si no hemos alcanzado el límite, continuar con el siguiente lote
                            lote_obtenido = True
                            break
                        else:
                            # Si obtuvimos registros, resetear el contador
                            lotes_sin_registros = 0
                            lote_obtenido = True
                        
                        # Calcular tiempo estimado restante
                        if total_fetched > 0:
                            tiempo_transcurrido = time.time() - getattr(self, 'start_time', time.time())
                            if not hasattr(self, 'start_time'):
                                self.start_time = time.time()
                                tiempo_transcurrido = 0
                            
                            if tiempo_transcurrido > 0:
                                registros_por_segundo = total_fetched / tiempo_transcurrido
                                registros_restantes = total_records - total_fetched
                                tiempo_restante = registros_restantes / registros_por_segundo if registros_por_segundo > 0 else 0
                                
                                horas = int(tiempo_restante // 3600)
                                minutos = int((tiempo_restante % 3600) // 60)
                                segundos = int(tiempo_restante % 60)
                                
                                tiempo_estimado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                            else:
                                tiempo_estimado = "Calculando..."
                        else:
                            tiempo_estimado = "Calculando..."
                        
                        # Actualizar progreso con tiempo estimado
                        progress = total_fetched/total_records*100 if total_records > 0 else 100
                        mensaje = f"Obteniendo registros: {total_fetched:,}/{total_records:,} ({progress:.1f}%) - Tiempo estimado: {tiempo_estimado}"
                        
                        if callback_progreso:
                            callback_progreso(mensaje, progress)
                        
                        # Pausa entre solicitudes para no sobrecargar la API
                        print(f"DEBUG: Esperando {self.REQUEST_DELAY} segundos antes de la siguiente solicitud...")
                        time.sleep(self.REQUEST_DELAY)
                        break
                        
                    except requests.exceptions.Timeout as e:
                        print(f"\nTIMEOUT en intento {attempt + 1}/{self.MAX_RETRIES}: {str(e)}")
                        print(f"La API está respondiendo muy lentamente. Timeout configurado: {self.API_TIMEOUT} segundos")
                        if attempt < self.MAX_RETRIES - 1:
                            print(f"Reintentando en {self.RETRY_DELAY} segundos...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print("\nSe agotaron los reintentos por timeout. Continuando con los datos obtenidos hasta ahora.")
                            return all_records
                    except requests.exceptions.ConnectionError as e:
                        print(f"\nERROR DE CONEXIÓN en intento {attempt + 1}/{self.MAX_RETRIES}: {str(e)}")
                        print("Verifique su conexión a internet y la disponibilidad de la API")
                        if attempt < self.MAX_RETRIES - 1:
                            print(f"Reintentando en {self.RETRY_DELAY} segundos...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print("\nSe agotaron los reintentos por error de conexión. Continuando con los datos obtenidos hasta ahora.")
                            return all_records
                    except requests.exceptions.RequestException as e:
                        print(f"\nError en intento {attempt + 1}/{self.MAX_RETRIES}: {str(e)}")
                        if attempt < self.MAX_RETRIES - 1:
                            print(f"Reintentando en {self.RETRY_DELAY} segundos...")
                            time.sleep(self.RETRY_DELAY)
                        else:
                            print("\nSe agotaron los reintentos. Continuando con los datos obtenidos hasta ahora.")
                            return all_records
                    except Exception as e:
                        print(f"\nError inesperado: {str(e)}")
                        return all_records
                
                # Si no se pudo obtener el lote después de todos los reintentos, salir del bucle
                if not lote_obtenido:
                    print("DEBUG: No se pudo obtener el lote después de todos los reintentos. Terminando obtención.")
                    break
            
            print(f"DEBUG: Finalizada la obtención de registros. Total obtenido: {total_fetched}")
            return all_records
            
        except Exception as e:
            print(f"Error al obtener los nuevos registros: {str(e)}")
            return []

    def actualizar_datos(self, tabla, callback_progreso=None, controlador=None):
        """Actualiza los datos de la tabla especificada"""
        try:
            # Verificar si la actualización ha sido cancelada
            if controlador and not controlador.esta_actualizando():
                print(f"DEBUG: Actualización de {tabla} cancelada")
                return False
            
            # Validar conexión a la base de datos ANTES de proceder
            if callback_progreso:
                callback_progreso("Validando conexión a la base de datos...", 0)
            
            try:
                config = get_database_params()
                if config is None:
                    raise Exception("No hay configuración de base de datos. Por favor, configure la base de datos primero.")
                
                # Probar conexión con timeout
                conn = psycopg2.connect(**config)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                conn.close()
                
                if callback_progreso:
                    callback_progreso("Conexión a la base de datos validada correctamente", 0)
                    
            except psycopg2.OperationalError as e:
                error_msg = "No fue posible establecer conexión con la base de datos"
                if callback_progreso:
                    callback_progreso(f"[ERROR] {error_msg}", 0)
                raise Exception(error_msg)
            except psycopg2.Error as e:
                error_msg = "No fue posible establecer conexión con la base de datos"
                if callback_progreso:
                    callback_progreso(f"[ERROR] {error_msg}", 0)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = "No fue posible establecer conexión con la base de datos"
                if callback_progreso:
                    callback_progreso(f"[ERROR] {error_msg}", 0)
                raise Exception(error_msg)
                
            # Obtener el total de registros en la API
            api_url = API_URLS[tabla]
            total_records = self.get_total_records(api_url)
            
            if callback_progreso:
                callback_progreso(f"Total de registros en la API: {total_records}", 0)
            
            # Obtener el ObjectID más reciente
            latest_objectid = self.get_latest_objectid(tabla)
            if latest_objectid is None:
                if callback_progreso:
                    callback_progreso("No se pudo obtener el ObjectID más reciente", 0)
                return False
            
            if latest_objectid == 0:
                if callback_progreso:
                    callback_progreso("Tabla vacía detectada - se obtendrán todos los datos desde el inicio", 0)
            else:
                if callback_progreso:
                    callback_progreso(f"ObjectID más reciente encontrado: {latest_objectid}", 0)
            
            # Verificar cancelación antes de obtener registros
            if controlador and not controlador.esta_actualizando():
                print(f"DEBUG: Actualización de {tabla} cancelada antes de obtener registros")
                return False
                
            # Obtener los nuevos registros - usar * para obtener todos los campos disponibles
            # Esto evita errores 400 cuando se especifican campos que no existen en la API
            campos_api = ['*']
            
            new_records = self.get_new_records(api_url, latest_objectid, campos_api, callback_progreso)
            
            if not new_records:
                if callback_progreso:
                    callback_progreso("No hay nuevos registros para procesar", 0)
                return True
            
            if callback_progreso:
                callback_progreso(f"Total de nuevos registros encontrados: {len(new_records)}", 0)
                callback_progreso(f"Porcentaje de nuevos registros: {(len(new_records)/total_records)*100:.2f}%", 0)
            
            # Crear DataFrame con los registros
            df = pd.DataFrame(new_records)
            
            # Formatear fechas si es necesario (solo para tablas que tienen campos de fecha complejos)
            if tabla in ['Accidente', 'ActorVial']:
                df = self.formatear_fechas(df)
            
            # Aplicar limpieza básica de fechas para todas las tablas que tengan campos de fecha
            campos_fecha = self.obtener_campos_fecha_por_tabla(tabla)
            if campos_fecha:
                df = self.limpiar_valores_fecha(df, campos_fecha)
            
            # Ordenar por OBJECTID
            df = df.sort_values('OBJECTID')
            
            # Insertar registros en la base de datos
            if callback_progreso:
                callback_progreso("Iniciando inserción de registros en la base de datos...", 0)
            
            resultado = self.insertar_registros(df, tabla, callback_progreso)
            
            if resultado:
                if callback_progreso:
                    callback_progreso("Actualización completada exitosamente", 100)
                return True
            else:
                if callback_progreso:
                    callback_progreso("Error al insertar los registros", 0)
                return False
            
        except Exception as e:
            print(f"Error en el proceso de actualización: {str(e)}")
            if callback_progreso:
                callback_progreso(f"Error: {str(e)}", 0)
            return False 