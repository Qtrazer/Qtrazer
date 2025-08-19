"""Configuración de la aplicación."""
import os
import sys
from dotenv import load_dotenv

def get_database_config():
    """Configuración inteligente basada en el entorno de ejecución"""
    
    if getattr(sys, 'frozen', False):
        # EJECUTABLE (.exe) - desde cualquier ubicación
        print("Ejecutando desde ejecutable (.exe)")
        
        # Intentar cargar configuración guardada previamente
        saved_config = load_saved_config_from_file()
        if saved_config:
            print("Configuración guardada encontrada y cargada automáticamente")
            return saved_config
        else:
            print("No hay configuración previa, se mostrará interfaz de configuración")
            return None
    else:
        # CÓDIGO FUENTE (VS Code, terminal)
        print("Ejecutando desde código fuente (desarrollo)")
        
        # Intentar cargar configuración guardada previamente
        saved_config = load_saved_config_from_file()
        if saved_config:
            print("Configuración guardada encontrada y cargada automáticamente")
            return saved_config
        
        if os.path.exists('.env'):
            print("Archivo .env encontrado, cargando...")
            load_dotenv()
            return {
                'dbname': os.getenv('DB_NAME', 'Siniestros'),
                'user': os.getenv('DB_USER', 'Analyst'),
                'password': os.getenv('DB_PASSWORD', ''),
                'host': os.getenv('DB_HOST', '190.60.210.154'),
                'port': os.getenv('DB_PORT', '5432')
            }
        else:
            print("Archivo .env no encontrado, usando valores por defecto")
            return {
                'dbname': 'Siniestros',
                'user': 'Analyst',
                'password': '',
                'host': '190.60.210.154',
                'port': '5432'
            }

def load_saved_config_from_file():
    """Carga la configuración guardada desde el archivo JSON"""
    try:
        import json
        import os
        
        # Determinar la ruta del archivo de configuración
        if getattr(sys, 'frozen', False):
            # Si es ejecutable (.exe), buscar en el directorio del usuario
            config_dir = os.path.expanduser("~\\AppData\\Local\\Qtrazer")
        else:
            # Si es desarrollo, buscar en el directorio del proyecto
            config_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        config_file = os.path.join(config_dir, 'qtrazer_config.json')
        
        # Verificar si existe el archivo de configuración
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Configuración cargada desde: {config_file}")
            return config
        else:
            print(f"Archivo de configuración no encontrado: {config_file}")
            return None
            
    except Exception as e:
        print(f"Error al cargar archivo de configuración: {str(e)}")
        return None

# Cargar configuración inicial
PARAMETROS_BD = get_database_config()

def update_database_config(new_config):
    """Actualiza la configuración de la base de datos dinámicamente"""
    global PARAMETROS_BD
    PARAMETROS_BD = new_config
    print("Configuración de base de datos actualizada dinámicamente")

def get_current_database_config():
    """Retorna la configuración actual de la base de datos"""
    return PARAMETROS_BD

def get_database_params():
    """Función que siempre retorna la configuración actual (para uso en otros módulos)"""
    # Si PARAMETROS_BD es None, intentar obtener configuración
    if PARAMETROS_BD is None:
        return get_database_config()
    return PARAMETROS_BD

# Configuración de la interfaz
CONFIG_INTERFAZ = {
    'titulo': 'Qtrazer - Sistema de Consulta de Siniestros Viales',
    'tamaño_ventana': '800x600',
    'tamaño_ventana_consulta': '800x600',
    'tamaño_ventana_actualizacion': '600x400'
}

# Configuración de la base de datos (se define arriba en get_database_config())
# PARAMETROS_BD ya está definido arriba

# Configuración de las tablas
CONFIG_TABLAS = {
    'Accidente': {
        'nombre_tabla': 'accidente',
        'columnas': [
            'objectid', 'formulario', 'codigo_accidente', 'fecha_ocurrencia_acc',
            'hora_ocurrencia_acc', 'ano_ocurrencia_acc', 'mes_ocurrencia_acc',
            'dia_ocurrencia_acc', 'direccion', 'gravedad', 'clase_acc',
            'localidad', 'municipio', 'fecha_hora_acc', 'latitud', 'longitud',
            'civ', 'pk_calzada'
        ]
    },
    'ActorVial': {
        'nombre_tabla': 'vm_acc_actor_vial',
        'columnas': [
            'condicion_a', 'objectid', 'formulario', 'codigo_accidentado',
            'codigo_victima', 'codigo_vehiculo', 'condicion', 'estado',
            'muerte_posterior', 'fecha_posterior_muerte', 'genero',
            'fecha_nacimiento', 'edad', 'codigo'
        ]
    },
    'Causa': {
        'nombre_tabla': 'vm_acc_causa',
        'columnas': [
            'codigo_ac_vh', 'objectid', 'formulario', 'codigo_accidente',
            'codigo_vehiculo', 'codigo_causa', 'nombre', 'tipo',
            'descripcion2', 'tipo_causa', 'codigo'
        ]
    },
    'AccidenteVehiculo': {
        'nombre_tabla': 'vm_acc_vehiculo',
        'columnas': [
            'objectid', 'formulario', 'placa', 'codigo_vehiculo',
            'clase', 'servicio', 'modalidad', 'enfuga', 'codigo'
        ]
    },
    'Accidente_via': {
        'nombre_tabla': 'vm_acc_vial',
        'columnas': [
            'objectid', 'formulario', 'codigo_accidente', 'codigo_via',
            'geometrica_a', 'geometrica_b', 'geometrica_c', 'utilizacion',
            'calzadas', 'carriles', 'material', 'estado', 'condiciones',
            'iluminacion_a', 'iluminacion_b', 'agente_transito',
            'semaforo', 'visual', 'codigo'
        ]
    }
}

# URLs de las APIs
API_URLS = {
    'Accidente': "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query",
    'Accidente_via': "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/6/query",
    'Causa': "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/4/query",
    'AccidenteVehiculo': "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/5/query",
    'ActorVial': "https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/3/query"
}

# Lista de campos a obtener de la API
CAMPOS_API = [
    'OBJECTID',
    'FORMULARIO',
    'CODIGO_ACCIDENTE',
    'FECHA_OCURRENCIA_ACC',
    'HORA_OCURRENCIA_ACC',
    'ANO_OCURRENCIA_ACC',
    'MES_OCURRENCIA_ACC',
    'DIA_OCURRENCIA_ACC',
    'DIRECCION',
    'GRAVEDAD',
    'CLASE_ACC',
    'LOCALIDAD',
    'MUNICIPIO',
    'FECHA_HORA_ACC',
    'LATITUD',
    'LONGITUD',
    'CIV',
    'PK_CALZADA'
]

# Columnas que contienen fechas
COLUMNAS_FECHA = [
    'FECHA_OCURRENCIA_ACC',
    'FECHA_HORA_ACC',
    'FECHA_POSTERIOR_MUERTE',
    'FECHA_NACIMIENTO'
]

# Campos específicos para ActorVial
CAMPOS_API_ACTOR_VIAL = [
    'CONDICION_A',
    'OBJECTID',
    'FORMULARIO',
    'CODIGO_ACCIDENTADO',
    'CODIGO_VICTIMA',
    'CODIGO_VEHICULO',
    'CONDICION',
    'ESTADO',
    'MUERTE_POSTERIOR',
    'FECHA_POSTERIOR_MUERTE',
    'GENERO',
    'FECHA_NACIMIENTO',
    'EDAD',
    'CODIGO'
] 