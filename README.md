# Qtrazer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-green.svg)](https://postgresql.org)

## 📋 Descripción

**Qtrazer** es una herramienta para consultar datos de siniestros viales en Bogotá, desarrollado para proporcionar acceso a información oficial sobre accidentes de tránsito en la ciudad. El sistema permite a los usuarios consultar registros históricos de siniestros viales y mantener actualizada la base de datos ya sea en servidor o local de acuerdo a la configuración que se defina.La información proviene de los repositorios oficiales de la Secretaría Distrital de Movilidad.

## ✨ Características Principales

- 🔍 **Consulta de Siniestros**: Búsqueda y filtrado avanzado de registros de accidentes viales.
- 🔄 **Actualización Automática**: Descarga y sincronización de datos oficiales desde APIs.
- 💻 **Interfaz Intuitiva**: Diseñado con Tkinter.
- 📊 **Exportación de Datos**: Generación de reportes en formato Excel.
- 🗄️ **Base de Datos PostgreSQL**: Almacenamiento escalable.
- 🔒 **Seguridad**: Gestión de usuarios y permisos granulares.
- 📱 **Responsive**: Interfaz que se adapta a diferentes tamaños de ventana.

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura **Modelo-Vista-Controlador (MVC)**:

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│     VISTAS      │    │   CONTROLADORES     │    │     MODELOS     │
│                 │    │                     │    │                 │
│ • main_view     │◄──►│ • main_controller   │◄──►│ • database      │
│ • query_view    │    │ • update_controller │    │ • update_model  │
│ • update_view   │    │                     │    │ • api_client    │
│ • splash_view   │    │                     │    │                 │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
                                │                          │
                                ▼                          ▼
                       ┌─────────────────┐        ┌─────────────────┐
                       │   CONFIGURACIÓN │        │  BASE DE DATOS  │
                       │                 │        │                 │
                       │ • settings.py   │        │ • PostgreSQL    │
                       │                 │        │ • Servidor      │
                       └─────────────────┘        │ • APIs Externas │
                                                  └─────────────────┘
```

## 📁 Estructura del Proyecto

```
Qtrazer/
├── assets/                     # Recursos gráficos
│   ├── logo_qtrazer.png        # Logo principal
│   ├── Simbolo_Qtrazer.ico     # Icono de la aplicación
│   └── splash.png              # Imagen de pantalla de inicio
├── config/                     # Configuración del sistema
│   └── settings.py             # Parámetros de configuración
├── controllers/                # Lógica de control
│   ├── main_controller.py      # Controlador principal
│   └── update_controller.py    # Control de actualizaciones
├── docs/                       # Documentación
│   ├── manual_usuario.md       # Manual de usuario
│   ├── manual_tecnico.md       # Manual técnico
│   └── scripts/                # Scripts de base de datos
│       ├── create_tables.sql   # Creación de tablas
│       └── backup_database.sh  # Backup automático
├── models/                     # Lógica de negocio
│   ├── database.py             # Gestión de base de datos
│   ├── update_model.py         # Actualización de datos
│   └── api_client.py           # Cliente de APIs
├── views/                      # Interfaces de usuario
│   ├── main_view.py            # Vista principal
│   ├── query_view.py           # Vista de consultas
│   ├── update_view.py          # Vista de actualización
│   └── splash_view.py          # Pantalla de inicio
├── src/                        # Código fuente principal
│   └── main.py                 # Punto de entrada
├── requirements.txt            # Dependencias de Python
├── package.json                # Configuración del proyecto
└── README.md                   # Este archivo
```

## 🚀 Instalación Rápida

### Prerrequisitos

- **Python 3.8+**
- **PostgreSQL 12+**
- **Git**

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Qtrazer/Qtrazer.git
cd qtrazer
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

```bash
# Ejecutar script de creación de tablas
sudo -u postgres psql -f docs/scripts/create_tables.sql
```

### 5. Ejecutar la Aplicación

```bash
python src/main.py
```

## 🗄️ Configuración de Base de Datos

### Instalación de PostgreSQL

#### Windows
1. Descargar desde [postgresql.org/download/windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Ejecutar instalador como administrador
3. Configurar contraseña del usuario `postgres`

### Crear Base de Datos y Usuario

```sql
-- Crear base de datos
CREATE DATABASE "Siniestros";

-- Crear usuario (reemplazar con usuario y contraseña reales)
CREATE USER "NombreUsuario" WITH PASSWORD 'ContraseñaSegura';

-- Asignar permisos
GRANT CONNECT ON DATABASE "Siniestros" TO "NombreUsuario";
GRANT USAGE ON SCHEMA public TO "NombreUsuario";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "NombreUsuario";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "NombreUsuario";
```

## ⚙️ Configuración

### Archivo de Configuración

Editar `src/config/settings.py`:

```python
# Configuración de la base de datos
PARAMETROS_BD = {
    'dbname': 'Siniestros',
    'user': 'Definir Usuario',
    'password': 'Definir Contraseña',
    'host': 'Localhost',  # IP del servidor PostgreSQL
    'port': '5432'
}
```

## 🔧 Desarrollo

### Configuración del IDE (Visual Studio Code)

1. **Instalar Extensiones Recomendadas**:
   - Python 
   - Python Indent 
   - Python Docstring Generator
   - GitLens
   - PostgreSQL

2. **Configurar Python Interpreter**:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Seleccionar el entorno virtual del proyecto



## 📊 Base de Datos

### Estructura de Tablas

#### Tabla Principal: `accidente`
- **objectid**: Identificador único (Primary Key)
- **formulario**: Número de formulario del accidente
- **fecha_ocurrencia_acc**: Fecha del accidente
- **hora_ocurrencia_acc**: Hora del accidente
- **localidad**: Barrio o zona de Bogotá
- **direccion**: Dirección del accidente
- **latitud/longitud**: Coordenadas geográficas

#### Tablas Relacionadas
- **`vm_acc_actor_vial`**: Personas involucradas
- **`vm_acc_causa`**: Causas del accidente
- **`vm_acc_vehiculo`**: Vehículos involucrados
- **`vm_acc_vial`**: Características de la vía

### Consultas de Ejemplo

#### Consulta Básica por Fecha
```sql
SELECT 
    formulario,
    fecha_ocurrencia_acc,
    localidad,
    direccion
FROM accidente 
WHERE fecha_ocurrencia_acc BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY fecha_ocurrencia_acc DESC;
```

#### Consulta con Joins
```sql
SELECT 
    a.formulario,
    a.fecha_ocurrencia_acc,
    a.localidad,
    COUNT(av.objectid) as total_victimas,
    COUNT(CASE WHEN av.estado = 'MUERTO' THEN 1 END) as fallecidos
FROM accidente a
LEFT JOIN vm_acc_actor_vial av ON a.formulario = av.formulario
WHERE a.fecha_ocurrencia_acc >= '2024-01-01'
GROUP BY a.formulario, a.fecha_ocurrencia_acc, a.localidad
ORDER BY total_victimas DESC;
```

## 🔄 APIs Externas

### Endpoints de la Secretaría de Movilidad

- **Accidentes**: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/2/query`
- **Actores Viales**: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/3/query`
- **Causas**: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/4/query`
- **Vehículos**: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/5/query`
- **Vías**: `https://sig.simur.gov.co/arcgis/rest/services/Accidentalidad/AccidentalidadAnalisis/FeatureServer/6/query`

### Cliente API

```python
from src.models.api_client import ClienteAPI

# Crear cliente
cliente = ClienteAPI()

# Obtener registros
registros = cliente.obtener_registros('Accidente')
```


## 🚀 Despliegue

### Crear Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed --icon=assets/Simbolo_Qtrazer.ico src/main.py

# El ejecutable se creará en dist/main.exe
```

## 👥 Autores

- **Desarrolladores Principales**: [Mario Lerma, Alexis Sierra]
