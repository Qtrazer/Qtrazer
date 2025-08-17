# 🚗 Sistema Qtrazer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-green.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

**Qtrazer** es un sistema especializado para consultar datos de siniestros viales en Bogotá, desarrollado para proporcionar acceso a información oficial sobre accidentes de tránsito en la ciudad. El sistema permite a los usuarios consultar registros históricos de siniestros viales y mantener actualizada la base de datos local con información proveniente de los repositorios oficiales de la Secretaría Distrital de Movilidad.

## ✨ Características Principales

- 🔍 **Consulta de Siniestros**: Búsqueda y filtrado avanzado de registros de accidentes viales
- 🔄 **Actualización Automática**: Descarga y sincronización de datos oficiales desde APIs
- 💻 **Interfaz Intuitiva**: Diseño moderno y fácil de usar con Tkinter
- 📊 **Exportación de Datos**: Generación de reportes en formato Excel
- 🗄️ **Base de Datos PostgreSQL**: Almacenamiento robusto y escalable
- 🔒 **Seguridad**: Gestión de usuarios y permisos granulares
- 📱 **Responsive**: Interfaz que se adapta a diferentes tamaños de ventana

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura **Modelo-Vista-Controlador (MVC)**:

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

## 📁 Estructura del Proyecto

```
Qtrazer/
├── assets/                     # Recursos gráficos
│   ├── logo_qtrazer.png       # Logo principal
│   ├── Simbolo_Qtrazer.ico    # Icono de la aplicación
│   └── splash.png             # Imagen de pantalla de inicio
├── config/                     # Configuración del sistema
│   └── settings.py            # Parámetros de configuración
├── controllers/                # Lógica de control
│   ├── main_controller.py     # Controlador principal
│   └── update_controller.py   # Control de actualizaciones
├── docs/                       # Documentación
│   ├── manual_usuario.md      # Manual de usuario
│   ├── manual_tecnico.md      # Manual técnico
│   └── scripts/               # Scripts de base de datos
│       ├── create_tables.sql  # Creación de tablas
│       └── backup_database.sh # Backup automático
├── models/                     # Lógica de negocio
│   ├── database.py            # Gestión de base de datos
│   ├── update_model.py        # Actualización de datos
│   └── api_client.py          # Cliente de APIs
├── views/                      # Interfaces de usuario
│   ├── main_view.py           # Vista principal
│   ├── query_view.py          # Vista de consultas
│   ├── update_view.py         # Vista de actualización
│   └── splash_view.py         # Pantalla de inicio
├── src/                        # Código fuente principal
│   └── main.py                # Punto de entrada
├── requirements.txt            # Dependencias de Python
├── package.json               # Configuración del proyecto
└── README.md                  # Este archivo
```

## 🚀 Instalación Rápida

### Prerrequisitos

- **Python 3.8+**
- **PostgreSQL 12+**
- **Git**

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/qtrazer.git
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

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### Windows
1. Descargar desde [postgresql.org/download/windows](https://postgresql.org/download/windows)
2. Ejecutar instalador como administrador
3. Configurar contraseña del usuario `postgres`

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Crear Base de Datos y Usuario

```sql
-- Conectar como superusuario
sudo -u postgres psql

-- Crear base de datos
CREATE DATABASE "Siniestros";

-- Crear usuario Analyst
CREATE USER "Analyst" WITH PASSWORD 'Julio2019**';

-- Asignar permisos
GRANT CONNECT ON DATABASE "Siniestros" TO "Analyst";
GRANT USAGE ON SCHEMA public TO "Analyst";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "Analyst";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "Analyst";

-- Salir
\q
```

### Ejecutar Script de Creación de Tablas

```bash
sudo -u postgres psql -f docs/scripts/create_tables.sql
```

## ⚙️ Configuración

### Archivo de Configuración

Editar `src/config/settings.py`:

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

### Variables de Entorno (Opcional)

```bash
# Crear archivo .env
export QTRAZER_DB_HOST=10.14.15.35
export QTRAZER_DB_PORT=5432
export QTRAZER_DB_NAME=Siniestros
export QTRAZER_DB_USER=Analyst
export QTRAZER_DB_PASSWORD=Julio2019**
```

## 🔧 Desarrollo

### Configuración del IDE (Visual Studio Code)

1. **Instalar Extensiones Recomendadas**:
   - Python (Microsoft)
   - Python Indent (Kevin Rose)
   - Python Docstring Generator (Nils Werner)
   - GitLens (Eric Amodio)
   - PostgreSQL (Chris Kolkman)

2. **Configurar Python Interpreter**:
   - `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Seleccionar el entorno virtual del proyecto

3. **Configurar Debugging**:
   - Crear archivo `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Qtrazer",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Estructura de Código

#### Estándares de Codificación
- **PEP 8**: Estilo de código Python
- **Docstrings**: Documentación de funciones y clases
- **Type Hints**: Anotaciones de tipo (opcional)
- **Logging**: Sistema de logs estructurado

#### Ejemplo de Estructura de Clase

```python
class GestorBaseDatos:
    """Gestor para operaciones con la base de datos PostgreSQL."""
    
    def __init__(self):
        """Inicializa el gestor de base de datos."""
        self.conexion = None
        self.cursor = None
    
    def conectar(self) -> bool:
        """
        Establece conexión con la base de datos.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
            
        Raises:
            Exception: Si falla la conexión a la base de datos.
        """
        try:
            self.conexion = psycopg2.connect(**PARAMETROS_BD)
            self.cursor = self.conexion.cursor()
            return True
        except psycopg2.OperationalError as e:
            raise Exception("Falló la conexión a la base de datos")
```

## 🧪 Testing

### Instalar Dependencias de Testing

```bash
pip install pytest pytest-cov black flake8 mypy
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_database.py
```

### Linting y Formateo

```bash
# Formatear código
black src/

# Verificar estilo
flake8 src/

# Verificar tipos
mypy src/
```

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

## 🛠️ Mantenimiento

### Backup Automático

#### Configurar Cron Job
```bash
# Editar crontab
crontab -e

# Backup diario a las 2:00 AM
0 2 * * * /bin/bash /path/to/qtrazer/docs/scripts/backup_database.sh

# Backup semanal los domingos a las 3:00 AM
0 3 * * 0 /bin/bash /path/to/qtrazer/docs/scripts/backup_database.sh --retention 30
```

#### Ejecutar Backup Manualmente
```bash
# Backup completo
./docs/scripts/backup_database.sh

# Solo limpieza
./docs/scripts/backup_database.sh --cleanup

# Cambiar retención
./docs/scripts/backup_database.sh --retention 14
```

### Optimización de Base de Datos

#### Análisis de Rendimiento
```sql
-- Verificar estadísticas
ANALYZE accidente;
ANALYZE vm_acc_actor_vial;
ANALYZE vm_acc_causa;
ANALYZE vm_acc_vehiculo;
ANALYZE vm_acc_vial;

-- Verificar uso de índices
EXPLAIN ANALYZE SELECT * FROM accidente WHERE localidad = 'CHAPINERO';
```

#### Limpieza de Datos
```sql
-- Limpiar registros duplicados
SELECT limpiar_duplicados_accidente();

-- Obtener estadísticas
SELECT * FROM obtener_estadisticas_bd();
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

### Configurar como Servicio (Linux)

#### Crear Archivo de Servicio
```bash
sudo nano /etc/systemd/system/qtrazer.service
```

```ini
[Unit]
Description=Sistema Qtrazer
After=network.target postgresql.service

[Service]
Type=simple
User=qtrazer
WorkingDirectory=/opt/qtrazer
ExecStart=/opt/qtrazer/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Habilitar Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable qtrazer
sudo systemctl start qtrazer
```

## 📚 Documentación

### Manuales Disponibles

- **[Manual de Usuario](docs/manual_usuario.md)**: Guía completa para usuarios finales
- **[Manual Técnico](docs/manual_tecnico.md)**: Documentación para desarrolladores
- **[Scripts de Base de Datos](docs/scripts/)**: Scripts SQL y de mantenimiento

### Generar Documentación

```bash
# Instalar herramientas de documentación
pip install sphinx sphinx-rtd-theme

# Generar documentación
cd docs
sphinx-quickstart
make html
```

## 🤝 Contribución

### Flujo de Trabajo

1. **Fork** del repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
4. **Desarrolla** tu feature
5. **Testea** tu código
6. **Commit** tus cambios: `git commit -m "feat: agregar nueva funcionalidad"`
7. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
8. **Crea** un Pull Request

### Estándares de Commit

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Documentación
- **style**: Formato de código
- **refactor**: Refactorización
- **test**: Tests
- **chore**: Tareas de mantenimiento

### Checklist de Pull Request

- [ ] Código sigue estándares PEP 8
- [ ] Tests pasan exitosamente
- [ ] Documentación actualizada
- [ ] No hay conflictos de merge
- [ ] Descripción clara del cambio

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error de Conexión a Base de Datos
```bash
# Verificar estado del servicio
sudo systemctl status postgresql

# Verificar conectividad
ping 10.14.15.35
telnet 10.14.15.35 5432

# Verificar logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### Error de Dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Verificar versiones
python -c "import psycopg2; print(psycopg2.__version__)"
```

#### Problemas de Rendimiento
```sql
-- Verificar índices
\di

-- Analizar consultas lentas
EXPLAIN ANALYZE SELECT * FROM accidente WHERE fecha_ocurrencia_acc > '2024-01-01';
```

### Logs del Sistema

#### Habilitar Logs Detallados
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qtrazer.log'),
        logging.StreamHandler()
    ]
)
```

#### Ubicación de Logs
- **Aplicación**: `qtrazer.log` (directorio de ejecución)
- **PostgreSQL**: `/var/log/postgresql/`
- **Sistema**: `/var/log/syslog`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Desarrollador Principal**: [Tu Nombre]
- **Equipo de Desarrollo**: [Equipo]
- **Organización**: [Organización]

## 🙏 Agradecimientos

- **Secretaría Distrital de Movilidad de Bogotá** por proporcionar acceso a los datos abiertos
- **Comunidad de PostgreSQL** por el excelente motor de base de datos
- **Comunidad de Python** por las herramientas y bibliotecas utilizadas

## 📞 Soporte

### Canales de Soporte

- **Email**: [soporte@qtrazer.com](mailto:soporte@qtrazer.com)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/qtrazer/issues)
- **Documentación**: [Manual Técnico](docs/manual_tecnico.md)
- **Wiki**: [GitHub Wiki](https://github.com/tu-usuario/qtrazer/wiki)

### Recursos Adicionales

- **[Manual de Usuario](docs/manual_usuario.md)**: Guía completa para usuarios
- **[Manual Técnico](docs/manual_tecnico.md)**: Documentación para desarrolladores
- **[Scripts de Base de Datos](docs/scripts/)**: Scripts de mantenimiento
- **[Changelog](CHANGELOG.md)**: Historial de cambios

---

<div align="center">

**¿Te gustó el proyecto? ¡Dale una ⭐!**

[![GitHub stars](https://img.shields.io/github/stars/tu-usuario/qtrazer?style=social)](https://github.com/tu-usuario/qtrazer)
[![GitHub forks](https://img.shields.io/github/forks/tu-usuario/qtrazer?style=social)](https://github.com/tu-usuario/qtrazer)
[![GitHub issues](https://img.shields.io/github/issues/tu-usuario/qtrazer)](https://github.com/tu-usuario/qtrazer/issues)

</div>
