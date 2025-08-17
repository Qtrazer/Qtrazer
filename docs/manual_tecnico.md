# Manual Técnico - Sistema Qtrazer

## Tabla de Contenido
1. [Introducción](#introducción)
2. [Descripción General del Sistema](#descripción-general-del-sistema)
3. [Características de los Usuarios del Sistema](#características-de-los-usuarios-del-sistema)
4. [Requisitos de Hardware y Software](#requisitos-de-hardware-y-software)
5. [Instrucciones de Instalación, Configuración, Ejecución, Copias de Seguridad y Desinstalación](#instrucciones-de-instalación-configuración-ejecución-copias-de-seguridad-y-desinstalación)
6. [Solución de Problemas](#solución-de-problemas)

---

## 1. Introducción

### 1.1 Propósito del Manual
Este manual técnico proporciona información detallada para desarrolladores que deseen trabajar con el sistema Qtrazer, un sistema especializado para consultar datos de siniestros viales en Bogotá.

### 1.2 Alcance
El manual cubre la instalación, configuración, desarrollo y mantenimiento del sistema, incluyendo la gestión de la base de datos PostgreSQL y la integración con APIs externas.

### 1.3 Público Objetivo
- Desarrolladores de software
- Administradores de sistemas
- Administradores de bases de datos
- Técnicos de soporte
- Estudiantes de desarrollo de software

---

## 2. Descripción General del Sistema

### 2.1 Arquitectura del Sistema
El sistema Qtrazer sigue una arquitectura de **Modelo-Vista-Controlador (MVC)** con las siguientes características:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     VISTAS      │    │   CONTROLADORES │    │     MODELOS     │
│                 │    │                 │    │                 │
│ • main_view     │◄──►│ • main_controller│◄──►│ • database      │
│ • query_view    │    │ • update_controller│   │ • update_model │
│ • update_view   │    │                 │    │ • api_client    │
│ • splash_view   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CONFIGURACIÓN │    │  BASE DE DATOS  │
                       │                 │    │                 │
                       │ • settings.py   │    │ • PostgreSQL    │
                       │                 │    │ • Servidor      │
                       └─────────────────┘    │ • APIs Externas │
                                              └─────────────────┘
```

### 2.2 Componentes Principales

#### 2.2.1 Módulo de Vistas (`src/views/`)
- **`main_view.py`**: Interfaz principal del sistema
- **`query_view.py`**: Interfaz para consulta de siniestros
- **`update_view.py`**: Interfaz para actualización de base de datos
- **`splash_view.py`**: Pantalla de inicio del sistema

#### 2.2.2 Módulo de Controladores (`src/controllers/`)
- **`main_controller.py`**: Lógica de control principal
- **`update_controller.py`**: Control de actualizaciones de datos

#### 2.2.3 Módulo de Modelos (`src/models/`)
- **`database.py`**: Gestión de conexiones y consultas a PostgreSQL
- **`update_model.py`**: Lógica de actualización y sincronización
- **`api_client.py`**: Cliente para APIs externas

#### 2.2.4 Módulo de Configuración (`src/config/`)
- **`settings.py`**: Parámetros de configuración del sistema

### 2.3 Flujo de Datos
```
APIs Externas → API Client → Update Model → Database → PostgreSQL
                                    ↓
                              Query View ← Main Controller
```

### 2.4 Base de Datos
El sistema utiliza **PostgreSQL** como motor de base de datos principal, con las siguientes tablas:

#### 2.4.1 Estructura de Tablas
- **`accidente`**: Información general de siniestros viales
- **`vm_acc_actor_vial`**: Personas involucradas en accidentes
- **`vm_acc_causa`**: Causas de los accidentes
- **`vm_acc_vehiculo`**: Vehículos involucrados
- **`vm_acc_vial`**: Características de las vías

#### 2.4.2 Relaciones entre Tablas
```
accidente (formulario) ←→ vm_acc_actor_vial (formulario)
accidente (formulario) ←→ vm_acc_causa (formulario)
accidente (formulario) ←→ vm_acc_vehiculo (formulario)
accidente (formulario) ←→ vm_acc_vial (formulario)
```

---

## 3. Características de los Usuarios del Sistema

### 3.1 Tipos de Usuarios

#### 3.1.1 Usuario Final (Analyst)
- **Rol**: Consulta y análisis de datos
- **Permisos**: Lectura, inserción, actualización y eliminación de datos
- **Acceso**: Remoto a través de la aplicación cliente
- **Responsabilidades**: Mantener datos actualizados, generar reportes

#### 3.1.2 Desarrollador
- **Rol**: Desarrollo y mantenimiento del sistema
- **Permisos**: Acceso completo al código fuente y base de datos
- **Acceso**: Local y remoto
- **Responsabilidades**: Implementar nuevas funcionalidades, corregir errores

#### 3.1.3 Administrador del Sistema
- **Rol**: Gestión de infraestructura y seguridad
- **Permisos**: Administración completa del servidor y base de datos
- **Acceso**: Local al servidor
- **Responsabilidades**: Mantenimiento, copias de seguridad, seguridad

### 3.2 Perfiles de Acceso

#### 3.2.1 Usuario Analyst
```sql
-- Usuario con permisos para operaciones CRUD
CREATE USER Analyst WITH PASSWORD 'Julio2019**';
GRANT CONNECT ON DATABASE Siniestros TO Analyst;
GRANT USAGE ON SCHEMA public TO Analyst;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO Analyst;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO Analyst;
```

#### 3.2.2 Usuario Desarrollador
```sql
-- Usuario con permisos de desarrollo
CREATE USER Developer WITH PASSWORD 'DevPassword123';
GRANT ALL PRIVILEGES ON DATABASE Siniestros TO Developer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO Developer;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO Developer;
```

---

## 4. Requisitos de Hardware y Software

### 4.1 Requisitos del Servidor

#### 4.1.1 Hardware Mínimo
- **Procesador**: Intel Core i5 o AMD equivalente (4 núcleos)
- **Memoria RAM**: 8 GB mínimo, 16 GB recomendado
- **Almacenamiento**: 100 GB SSD mínimo, 500 GB recomendado
- **Red**: Conexión de 100 Mbps mínimo, 1 Gbps recomendado

#### 4.1.2 Hardware Recomendado
- **Procesador**: Intel Core i7 o AMD Ryzen 7 (8 núcleos)
- **Memoria RAM**: 32 GB
- **Almacenamiento**: 1 TB NVMe SSD
- **Red**: Conexión de 1 Gbps con redundancia

### 4.2 Requisitos del Cliente

#### 4.2.1 Hardware Mínimo
- **Procesador**: Intel Core i3 o AMD equivalente (2 núcleos)
- **Memoria RAM**: 4 GB mínimo, 8 GB recomendado
- **Almacenamiento**: 10 GB de espacio libre
- **Pantalla**: Resolución 1366x768 mínimo

#### 4.2.2 Hardware Recomendado
- **Procesador**: Intel Core i5 o AMD Ryzen 5 (4 núcleos)
- **Memoria RAM**: 16 GB
- **Almacenamiento**: 50 GB de espacio libre
- **Pantalla**: Resolución 1920x1080 o superior

### 4.3 Requisitos de Software

#### 4.3.1 Servidor
- **Sistema Operativo**: Ubuntu Server 20.04 LTS o superior
- **Base de Datos**: PostgreSQL 12 o superior
- **Python**: 3.8 o superior
- **Servidor Web**: Nginx (opcional, para monitoreo)

#### 4.3.2 Cliente
- **Sistema Operativo**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **Python**: 3.8 o superior
- **IDE**: Visual Studio Code (recomendado)
- **Git**: Para control de versiones

### 4.4 Dependencias de Python

#### 4.4.1 Dependencias Principales
```txt
psycopg2-binary==2.9.10    # Conexión a PostgreSQL
pandas==2.2.3              # Manipulación de datos
requests==2.32.3            # Cliente HTTP para APIs
Pillow==10.0.0             # Procesamiento de imágenes
tkcalendar==1.6.1          # Selector de fechas
```

#### 4.4.2 Dependencias de Desarrollo
```txt
pytest==8.3.4              # Framework de testing
black==23.0.0              # Formateador de código
flake8==6.0.0              # Linter de código
mypy==1.5.0                # Verificación de tipos
```

---

## 5. Instrucciones de Instalación, Configuración, Ejecución, Copias de Seguridad y Desinstalación

### 5.1 Preparación del Entorno de Desarrollo

#### 5.1.1 Instalación de Visual Studio Code
1. **Descargar VS Code**:
   - Visitar [code.visualstudio.com](https://code.visualstudio.com/)
   - Descargar la versión para tu sistema operativo
   - Instalar siguiendo el asistente

2. **Extensiones Recomendadas**:
   - **Python** (Microsoft)
   - **Python Indent** (Kevin Rose)
   - **Python Docstring Generator** (Nils Werner)
   - **GitLens** (Eric Amodio)
   - **PostgreSQL** (Chris Kolkman)

3. **Configuración de Python**:
   - Presionar `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (macOS)
   - Escribir "Python: Select Interpreter"
   - Seleccionar la versión de Python 3.8+

#### 5.1.2 Instalación de Git
1. **Windows**:
   ```bash
   # Descargar desde https://git-scm.com/download/win
   # Instalar con opciones por defecto
   ```

2. **macOS**:
   ```bash
   brew install git
   ```

3. **Ubuntu/Debian**:
   ```bash
   sudo apt update
   sudo apt install git
   ```

4. **Configuración inicial**:
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu.email@ejemplo.com"
   ```

### 5.2 Instalación de PostgreSQL

#### 5.2.1 Instalación en Ubuntu Server
```bash
# Actualizar repositorios
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Verificar instalación
sudo systemctl status postgresql

# Habilitar inicio automático
sudo systemctl enable postgresql
```

#### 5.2.2 Instalación en Windows
1. **Descargar instalador**:
   - Visitar [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
   - Descargar la versión más reciente

2. **Ejecutar instalador**:
   - Ejecutar como administrador
   - Seguir el asistente de instalación
   - Anotar la contraseña del usuario `postgres`

3. **Configurar PATH**:
   - Agregar `C:\Program Files\PostgreSQL\[version]\bin` al PATH del sistema

#### 5.2.3 Instalación en macOS
```bash
# Usando Homebrew
brew install postgresql

# Iniciar servicio
brew services start postgresql

# Crear base de datos
createdb `whoami`
```

### 5.3 Configuración de PostgreSQL

#### 5.3.1 Configuración de Red
1. **Editar `postgresql.conf`**:
   ```bash
   sudo nano /etc/postgresql/[version]/main/postgresql.conf
   ```

2. **Configurar escucha**:
   ```conf
   listen_addresses = '*'
   port = 5432
   ```

3. **Editar `pg_hba.conf`**:
   ```bash
   sudo nano /etc/postgresql/[version]/main/pg_hba.conf
   ```

4. **Agregar reglas de acceso**:
   ```conf
   # Conexiones locales
   local   all             postgres                                peer
   local   all             all                                     md5
   
   # Conexiones remotas
   host    all             all             0.0.0.0/0               md5
   host    all             all             ::/0                     md5
   ```

5. **Reiniciar PostgreSQL**:
   ```bash
   sudo systemctl restart postgresql
   ```

#### 5.3.2 Creación de Base de Datos y Usuarios
1. **Acceder como superusuario**:
   ```bash
   sudo -u postgres psql
   ```

2. **Crear base de datos**:
   ```sql
   CREATE DATABASE "Siniestros";
   ```

3. **Crear usuario Analyst**:
   ```sql
   CREATE USER "Analyst" WITH PASSWORD 'Julio2019**';
   ```

4. **Asignar permisos**:
   ```sql
   GRANT CONNECT ON DATABASE "Siniestros" TO "Analyst";
   GRANT USAGE ON SCHEMA public TO "Analyst";
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "Analyst";
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "Analyst";
   ```

5. **Salir de psql**:
   ```sql
   \q
   ```

### 5.4 Script de Creación de Tablas

#### 5.4.1 Archivo `create_tables.sql`
Crear el archivo `docs/scripts/create_tables.sql`:

```sql
-- Script de creación de tablas para el sistema Qtrazer
-- Base de datos: Siniestros
-- Usuario: Analyst

-- Conectar a la base de datos
\c "Siniestros";

-- Crear tabla de accidentes
CREATE TABLE IF NOT EXISTS accidente (
    objectid BIGINT PRIMARY KEY,
    formulario VARCHAR(50) NOT NULL,
    codigo_accidente INTEGER,
    fecha_ocurrencia_acc DATE,
    hora_ocurrencia_acc VARCHAR(10),
    ano_ocurrencia_acc INTEGER,
    mes_ocurrencia_acc VARCHAR(20),
    dia_ocurrencia_acc INTEGER,
    direccion TEXT,
    gravedad VARCHAR(50),
    clase_acc VARCHAR(100),
    localidad VARCHAR(100),
    municipio VARCHAR(100),
    fecha_hora_acc TIMESTAMP,
    latitud VARCHAR(20),
    longitud VARCHAR(20),
    civ INTEGER,
    pk_calzada INTEGER
);

-- Crear tabla de actores viales
CREATE TABLE IF NOT EXISTS vm_acc_actor_vial (
    objectid BIGINT PRIMARY KEY,
    formulario VARCHAR(50) NOT NULL,
    codigo_accidentado INTEGER,
    codigo_victima INTEGER,
    codigo_vehiculo INTEGER,
    condicion VARCHAR(100),
    estado VARCHAR(50),
    muerte_posterior VARCHAR(10),
    fecha_posterior_muerte DATE,
    genero VARCHAR(20),
    fecha_nacimiento DATE,
    edad INTEGER,
    codigo INTEGER,
    condicion_a VARCHAR(100)
);

-- Crear tabla de causas
CREATE TABLE IF NOT EXISTS vm_acc_causa (
    objectid BIGINT PRIMARY KEY,
    formulario VARCHAR(50) NOT NULL,
    codigo_ac_vh INTEGER,
    codigo_accidente INTEGER,
    codigo_vehiculo INTEGER,
    codigo_causa INTEGER,
    nombre TEXT,
    tipo VARCHAR(100),
    descripcion2 TEXT,
    tipo_causa VARCHAR(100),
    codigo INTEGER
);

-- Crear tabla de vehículos
CREATE TABLE IF NOT EXISTS vm_acc_vehiculo (
    objectid BIGINT PRIMARY KEY,
    formulario VARCHAR(50) NOT NULL,
    placa VARCHAR(20),
    codigo_vehiculo INTEGER,
    clase VARCHAR(100),
    servicio VARCHAR(100),
    modalidad VARCHAR(100),
    enfuga VARCHAR(10),
    codigo INTEGER
);

-- Crear tabla de vías
CREATE TABLE IF NOT EXISTS vm_acc_vial (
    objectid BIGINT PRIMARY KEY,
    formulario VARCHAR(50) NOT NULL,
    codigo_accidente INTEGER,
    codigo_via INTEGER,
    geometrica_a VARCHAR(100),
    geometrica_b VARCHAR(100),
    geometrica_c VARCHAR(100),
    utilizacion VARCHAR(100),
    calzadas INTEGER,
    carriles INTEGER,
    material VARCHAR(100),
    estado VARCHAR(100),
    condiciones VARCHAR(100),
    iluminacion_a VARCHAR(100),
    iluminacion_b VARCHAR(100),
    agente_transito VARCHAR(10),
    semaforo VARCHAR(10),
    visual VARCHAR(100),
    codigo INTEGER
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_accidente_formulario ON accidente(formulario);
CREATE INDEX IF NOT EXISTS idx_accidente_fecha ON accidente(fecha_ocurrencia_acc);
CREATE INDEX IF NOT EXISTS idx_accidente_localidad ON accidente(localidad);

CREATE INDEX IF NOT EXISTS idx_actor_vial_formulario ON vm_acc_actor_vial(formulario);
CREATE INDEX IF NOT EXISTS idx_causa_formulario ON vm_acc_causa(formulario);
CREATE INDEX IF NOT EXISTS idx_vehiculo_formulario ON vm_acc_vehiculo(formulario);
CREATE INDEX IF NOT EXISTS idx_vial_formulario ON vm_acc_vial(formulario);

-- Asignar permisos al usuario Analyst
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "Analyst";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "Analyst";

-- Verificar creación de tablas
\dt

-- Verificar permisos del usuario Analyst
\du "Analyst"
```

#### 5.4.2 Ejecución del Script
```bash
# Conectar a PostgreSQL y ejecutar el script
sudo -u postgres psql -f docs/scripts/create_tables.sql

# O desde psql
sudo -u postgres psql
\i docs/scripts/create_tables.sql
```

### 5.5 Configuración del Proyecto

#### 5.5.1 Clonación del Repositorio
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/qtrazer.git
cd qtrazer

# Crear rama de desarrollo
git checkout -b develop
```

#### 5.5.2 Configuración del Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 5.5.3 Configuración de la Base de Datos
1. **Editar `src/config/settings.py`**:
   ```python
   # Configuración de la base de datos
   PARAMETROS_BD = {
       'dbname': 'Siniestros',
       'user': 'Analyst',
       'password': 'Julio2019**',
       'host': '10.14.15.35',  # IP del servidor PostgreSQL
       'port': '5432'
   }
   ```

2. **Verificar conectividad**:
   ```bash
   # Probar conexión
   python -c "
   import psycopg2
   from src.config.settings import PARAMETROS_BD
   conn = psycopg2.connect(**PARAMETROS_BD)
   print('Conexión exitosa')
   conn.close()
   "
   ```

### 5.6 Ejecución del Sistema

#### 5.6.1 Ejecución en Modo Desarrollo
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Ejecutar aplicación
python src/main.py
```

#### 5.6.2 Ejecución en Modo Producción
```bash
# Crear ejecutable con PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/Simbolo_Qtrazer.ico src/main.py

# El ejecutable se creará en dist/main.exe
```

### 5.7 Copias de Seguridad

#### 5.7.1 Script de Backup Automático
Crear `docs/scripts/backup_database.sh`:

```bash
#!/bin/bash

# Script de backup automático para PostgreSQL
# Configuración
DB_NAME="Siniestros"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="qtrazer_backup_$DATE.sql"

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

# Crear backup
pg_dump -U $DB_USER -d "$DB_NAME" > $BACKUP_DIR/$BACKUP_FILE

# Comprimir backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Eliminar backups antiguos (mantener últimos 7 días)
find $BACKUP_DIR -name "qtrazer_backup_*.sql.gz" -mtime +7 -delete

# Log del backup
echo "Backup completado: $BACKUP_FILE.gz" >> $BACKUP_DIR/backup.log
```

#### 5.7.2 Configuración de Cron para Backups Automáticos
```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2:00 AM
0 2 * * * /bin/bash /path/to/qtrazer/docs/scripts/backup_database.sh
```

#### 5.7.3 Restauración de Backup
```bash
# Restaurar desde backup
gunzip -c /var/backups/postgresql/qtrazer_backup_20250101_020000.sql.gz | psql -U postgres -d "Siniestros"
```

### 5.8 Desinstalación

#### 5.8.1 Desinstalación del Sistema
```bash
# Detener servicios si están corriendo
sudo systemctl stop qtrazer  # si existe como servicio

# Eliminar archivos del sistema
sudo rm -rf /opt/qtrazer
sudo rm -f /usr/local/bin/qtrazer

# Eliminar usuario del sistema si se creó
sudo userdel -r qtrazer
```

#### 5.8.2 Desinstalación de PostgreSQL
```bash
# Ubuntu/Debian
sudo apt remove --purge postgresql postgresql-contrib
sudo rm -rf /var/lib/postgresql
sudo rm -rf /var/log/postgresql
sudo rm -rf /etc/postgresql

# Windows
# Usar "Agregar o quitar programas" del Panel de Control

# macOS
brew uninstall postgresql
brew services stop postgresql
```

---

## 6. Solución de Problemas

### 6.1 Problemas de Conexión a Base de Datos

#### 6.1.1 Error: "Falló la conexión a la base de datos"
**Síntomas**: Mensaje de error al intentar conectar
**Causas Posibles**:
- Servidor PostgreSQL no está ejecutándose
- Credenciales incorrectas
- Firewall bloqueando conexión
- Puerto incorrecto

**Soluciones**:
```bash
# Verificar estado del servicio
sudo systemctl status postgresql

# Verificar conectividad de red
ping 10.14.15.35
telnet 10.14.15.35 5432

# Verificar configuración de red en PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

#### 6.1.2 Error: "Permission denied"
**Síntomas**: Acceso denegado al intentar conectar
**Causas Posibles**:
- Usuario sin permisos suficientes
- Configuración incorrecta de pg_hba.conf

**Soluciones**:
```sql
-- Verificar permisos del usuario
\du "Analyst"

-- Asignar permisos si es necesario
GRANT ALL PRIVILEGES ON DATABASE "Siniestros" TO "Analyst";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "Analyst";
```

### 6.2 Problemas de Rendimiento

#### 6.2.1 Consultas Lentas
**Síntomas**: Respuesta lenta en consultas de datos
**Causas Posibles**:
- Falta de índices
- Consultas no optimizadas
- Recursos insuficientes del servidor

**Soluciones**:
```sql
-- Analizar consultas lentas
EXPLAIN ANALYZE SELECT * FROM accidente WHERE fecha_ocurrencia_acc BETWEEN '2024-01-01' AND '2024-12-31';

-- Crear índices adicionales si es necesario
CREATE INDEX idx_accidente_fecha_hora ON accidente(fecha_ocurrencia_acc, hora_ocurrencia_acc);
CREATE INDEX idx_accidente_localidad_fecha ON accidente(localidad, fecha_ocurrencia_acc);

-- Analizar y actualizar estadísticas
ANALYZE accidente;
ANALYZE vm_acc_actor_vial;
ANALYZE vm_acc_causa;
ANALYZE vm_acc_vehiculo;
ANALYZE vm_acc_vial;
```

#### 6.2.2 Alto Uso de Memoria
**Síntomas**: Servidor lento, errores de memoria
**Causas Posibles**:
- Configuración de memoria insuficiente
- Consultas que consumen mucha memoria

**Soluciones**:
```bash
# Editar configuración de PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf

# Ajustar parámetros de memoria
shared_buffers = 256MB          # 25% de RAM disponible
effective_cache_size = 1GB      # 75% de RAM disponible
work_mem = 4MB                  # Memoria por operación
maintenance_work_mem = 64MB     # Memoria para mantenimiento

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### 6.3 Problemas de APIs

#### 6.3.1 Error: "Error al obtener registros de la API"
**Síntomas**: Fallo al descargar datos de APIs externas
**Causas Posibles**:
- API no disponible
- Límites de rate limiting
- Problemas de conectividad

**Soluciones**:
```python
# Verificar conectividad a la API
import requests
try:
    response = requests.get("https://sig.simur.gov.co/arcgis/rest/services/")
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Implementar reintentos con backoff exponencial
import time
import random

def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### 6.4 Problemas de Interfaz de Usuario

#### 6.4.1 Error: "Logo no disponible"
**Síntomas**: Imágenes no se muestran correctamente
**Causas Posibles**:
- Archivos de imagen corruptos o faltantes
- Problemas de permisos de archivo
- Ruta incorrecta en el código

**Soluciones**:
```bash
# Verificar existencia de archivos
ls -la assets/
file assets/logo_qtrazer.png

# Verificar permisos
chmod 644 assets/*.png

# Verificar integridad de archivos
md5sum assets/logo_qtrazer.png
```

#### 6.4.2 Error: "Tkinter no disponible"
**Síntomas**: Error al importar tkinter
**Causas Posibles**:
- Tkinter no instalado en el sistema
- Versión de Python sin soporte para Tkinter

**Soluciones**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# Verificar instalación
python3 -c "import tkinter; print('Tkinter disponible')"
```

### 6.5 Problemas de Dependencias

#### 6.5.1 Error: "Module not found"
**Síntomas**: Módulos de Python no encontrados
**Causas Posibles**:
- Entorno virtual no activado
- Dependencias no instaladas
- Versiones incompatibles

**Soluciones**:
```bash
# Verificar entorno virtual
which python
pip list

# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Verificar versiones
python -c "import psycopg2; print(psycopg2.__version__)"
python -c "import pandas; print(pandas.__version__)"
```

### 6.6 Logs y Diagnóstico

#### 6.6.1 Habilitar Logs Detallados
```python
# En src/config/settings.py
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qtrazer.log'),
        logging.StreamHandler()
    ]
)

# En cada módulo
logger = logging.getLogger(__name__)
logger.debug("Mensaje de debug")
logger.info("Mensaje informativo")
logger.error("Mensaje de error")
```

#### 6.6.2 Monitoreo de Recursos
```bash
# Monitorear uso de CPU y memoria
htop
top

# Monitorear uso de disco
df -h
du -sh /var/lib/postgresql/*

# Monitorear logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 6.7 Recuperación de Desastres

#### 6.7.1 Plan de Recuperación
1. **Identificar el problema**:
   - Revisar logs del sistema
   - Verificar estado de servicios
   - Diagnosticar causa raíz

2. **Ejecutar procedimientos de recuperación**:
   - Restaurar desde backup más reciente
   - Recrear índices y estadísticas
   - Verificar integridad de datos

3. **Validar recuperación**:
   - Probar funcionalidades críticas
   - Verificar rendimiento del sistema
   - Documentar incidente y lecciones aprendidas

#### 6.7.2 Procedimientos de Emergencia
```bash
# Detener todos los servicios
sudo systemctl stop postgresql
sudo systemctl stop qtrazer

# Restaurar configuración de respaldo
sudo cp /etc/postgresql/*/main/postgresql.conf.backup /etc/postgresql/*/main/postgresql.conf
sudo cp /etc/postgresql/*/main/pg_hba.conf.backup /etc/postgresql/*/main/pg_hba.conf

# Restaurar base de datos
sudo -u postgres psql -c "DROP DATABASE \"Siniestros\";"
sudo -u postgres psql -c "CREATE DATABASE \"Siniestros\";"
gunzip -c /var/backups/postgresql/qtrazer_backup_latest.sql.gz | sudo -u postgres psql -d "Siniestros"

# Reiniciar servicios
sudo systemctl start postgresql
sudo systemctl start qtrazer
```

---

## Apéndices

### A. Comandos Útiles de PostgreSQL
```sql
-- Verificar estado de conexiones
SELECT * FROM pg_stat_activity;

-- Verificar tamaño de tablas
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Verificar índices
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Verificar permisos de usuario
\du "Analyst"
```

### B. Scripts de Mantenimiento
```bash
# Limpieza de logs antiguos
find /var/log -name "*.log" -mtime +30 -delete

# Optimización de base de datos
sudo -u postgres psql -d "Siniestros" -c "VACUUM ANALYZE;"

# Verificación de espacio en disco
df -h | grep -E 'Use%|/dev/'
```

### C. Configuración de Firewall
```bash
# Ubuntu/Debian
sudo ufw allow 5432/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
```

---

*Manual Técnico - Sistema Qtrazer v1.0*  
*Última actualización: Enero 2025*  
*Desarrollado para la consulta de datos de siniestros viales en Bogotá*
