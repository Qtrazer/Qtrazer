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

from src.config.settings import PARAMETROS_BD, CONFIG_TABLAS, CAMPOS_API, COLUMNAS_FECHA, API_URLS, CAMPOS_API_ACTOR_VIAL

class ModeloActualizacion:
    def __init__(self):
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5  # segundos
        self.PAGE_SIZE = 1000  # número de registros por página
        self.REQUEST_DELAY = 1  # segundos entre solicitudes
        self.DIAS = {
            'LUNES': 1, 'MARTES': 2, 'MIERCOLES': 3, 'JUEVES': 4,
            'VIERNES': 5, 'SABADO': 6, 'DOMINGO': 7
        }

    def convertir_dia_a_numero(self, dia):
        """Convierte el nombre del día a su número correspondiente"""
        if isinstance(dia, str):
            return self.DIAS.get(dia.upper(), 0)
        return 0

    def formatear_fechas(self, df):
        """Formatea las columnas de fecha al formato correcto para PostgreSQL"""
        for columna in COLUMNAS_FECHA:
            if columna in df.columns and columna != 'FECHA_NACIMIENTO':  # Excluir FECHA_NACIMIENTO
                try:
                    # Convertir de milisegundos a datetime
                    df[columna] = pd.to_datetime(df[columna], unit='ms')
                    
                    # Reemplazar NaT con None (que se convertirá a NULL en PostgreSQL)
                    df[columna] = df[columna].where(df[columna].notna(), None)
                    
                    # Formatear según el tipo de columna
                    if columna in ['FECHA_OCURRENCIA_ACC', 'FECHA_POSTERIOR_MUERTE']:
                        # Formato DATE: YYYY-MM-DD
                        df[columna] = df[columna].dt.strftime('%Y-%m-%d')
                    elif columna in ['FECHA_HORA_ACC']:
                        # Formato TIMESTAMP: YYYY-MM-DD HH:MM:SS
                        df[columna] = df[columna].dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"\nAdvertencia: No se pudo formatear la columna {columna}: {str(e)}")
        return df

    def insertar_registros(self, df, config_tabla, callback_progreso=None):
        """Inserta los registros en la base de datos"""
        try:
            conn = psycopg2.connect(**PARAMETROS_BD)
            cursor = conn.cursor()
            
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
            
            # Renombrar las columnas del DataFrame
            df = df.rename(columns=mapeo_columnas)
            
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

            
            # Reemplazar valores nulos con cadenas vacías para campos de texto
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna('')
            
            # Preparar la consulta de inserción
            columnas = CONFIG_TABLAS[config_tabla]['columnas']
            placeholders = ', '.join(['%s'] * len(columnas))
            columnas_str = ', '.join(columnas)
            
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
                    valores = [fila[col] for col in columnas]
                    cursor.execute(consulta, valores)
                    if cursor.rowcount > 0:
                        registros_insertados += 1
                        # Actualizar progreso cada 100 registros
                        if registros_insertados % 100 == 0:
                            porcentaje = (registros_insertados / total_registros) * 100
                            if callback_progreso:
                                callback_progreso(f"[INFO] Registros insertados: {registros_insertados}/{total_registros} ({porcentaje:.1f}%)", porcentaje)
                
                conn.commit()
            
            # Mostrar el total final
            if callback_progreso:
                callback_progreso(f"[INFO] Total de registros insertados: {registros_insertados}/{total_registros} (100%)", 100)
            
            return True
            
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
            conn = psycopg2.connect(**PARAMETROS_BD)
            cursor = conn.cursor()
            
            nombre_tabla = CONFIG_TABLAS[tabla]['nombre_tabla']
            cursor.execute(f"SELECT MAX(objectid) FROM {nombre_tabla}")
            latest_objectid = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return latest_objectid
        except Exception as e:
            print(f"Error al obtener el ObjectID más reciente: {str(e)}")
            return None

    def get_new_records(self, api_url, last_objectid, campos_api, callback_progreso=None):
        """Obtiene los registros completos mayores al último ObjectID con paginación"""
        all_records = []
        offset = 0
        total_fetched = 0
        
        # Primero obtenemos el total de registros nuevos
        params = {
            'where': f"OBJECTID > {last_objectid}",
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            total_records = data.get('count', 0)
            
            if callback_progreso:
                callback_progreso(f"Total de registros a obtener: {total_records}", 0)
            
            # Obtenemos los registros por lotes
            while total_fetched < total_records:
                params = {
                    'where': f"OBJECTID > {last_objectid}",
                    'outFields': ','.join(campos_api),
                    'f': 'json',
                    'returnGeometry': 'false',
                    'resultOffset': offset,
                    'resultRecordCount': self.PAGE_SIZE
                }
                
                for attempt in range(self.MAX_RETRIES):
                    try:
                        response = requests.get(api_url, params=params, timeout=30)
                        response.raise_for_status()
                        data = response.json()
                        features = data.get('features', [])
                        records = [feature['attributes'] for feature in features]
                        all_records.extend(records)
                        
                        total_fetched += len(records)
                        offset += len(records)
                        
                        # Actualizar progreso en una sola línea
                        progress = total_fetched/total_records*100
                        mensaje = f"Obteniendo registros: {total_fetched}/{total_records} ({progress:.1f}%)"
                        
                        if callback_progreso:
                            callback_progreso(mensaje, progress)
                        
                        # Pequeña pausa entre solicitudes para no sobrecargar la API
                        time.sleep(self.REQUEST_DELAY)
                        break
                        
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
            
            return all_records
            
        except Exception as e:
            print(f"Error al obtener los nuevos registros: {str(e)}")
            return []

    def actualizar_datos(self, tabla, callback_progreso=None):
        """Actualiza los datos de la tabla especificada"""
        try:
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
            
            if callback_progreso:
                callback_progreso(f"ObjectID más reciente encontrado: {latest_objectid}", 0)
            
            # Obtener los nuevos registros
            campos_api = CAMPOS_API if tabla == 'Accidente' else (
                CAMPOS_API_ACTOR_VIAL if tabla == 'ActorVial' else (
                    [
                        'OBJECTID', 'FORMULARIO', 'CODIGO_ACCIDENTE', 'CODIGO_VIA',
                        'GEOMETRICA_A', 'GEOMETRICA_B', 'GEOMETRICA_C', 'UTILIZACION',
                        'CALZADAS', 'CARRILES', 'MATERIAL', 'ESTADO', 'CONDICIONES',
                        'ILUMINACION_A', 'ILUMINACION_B', 'AGENTE_TRANSITO',
                        'SEMAFORO', 'VISUAL', 'CODIGO'
                    ] if tabla == 'Accidente_via' else (
                        [
                            'CODIGO_AC_VH', 'OBJECTID', 'FORMULARIO', 'CODIGO_ACCIDENTE',
                            'CODIGO_VEHICULO', 'CODIGO_CAUSA', 'NOMBRE', 'TIPO',
                            'DESCRIPCION2', 'TIPO_CAUSA', 'CODIGO'
                        ] if tabla == 'Causa' else [
                            'OBJECTID', 'FORMULARIO', 'PLACA', 'CODIGO_VEHICULO',
                            'CLASE', 'SERVICIO', 'MODALIDAD', 'ENFUGA', 'CODIGO'
                        ]
                    )
                )
            )
            
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
            
            # Formatear fechas si es necesario
            if tabla in ['Accidente', 'ActorVial']:
                df = self.formatear_fechas(df)
            
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