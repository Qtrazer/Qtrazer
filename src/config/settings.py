"""Configuración de la aplicación."""

# Configuración de la interfaz
CONFIG_INTERFAZ = {
    'titulo': 'Qtrazer - Sistema de Consulta de Siniestros Viales',
    'tamaño_ventana': '800x600',
    'tamaño_ventana_consulta': '800x600',
    'tamaño_ventana_actualizacion': '600x400'
}

# Configuración de la base de datos
PARAMETROS_BD = {
    'dbname': 'Siniestros',
    'user': 'Analyst',
    'password': 'Julio2019**',
    'host': '190.60.210.154', #10.14.15.35 | 190.60.210.154
    'port': '5432'
}

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