# 🧪 Sistema de Testing para Qtrazer

Este directorio contiene la suite completa de testing para el proyecto Qtrazer, implementando diferentes tipos de pruebas para asegurar la calidad y robustez del sistema.

## 📁 Estructura del Sistema de Testing

```
tests/
├── __init__.py                 # Paquete principal de testing
├── conftest.py                 # Configuración y fixtures comunes
├── unit/                       # Tests unitarios
│   ├── __init__.py
│   ├── test_api_client.py      # Tests del cliente API
│   ├── test_database.py        # Tests del gestor de BD
│   ├── test_update_model.py    # Tests del modelo de actualización
│   └── test_controllers.py     # Tests de los controladores
├── integration/                # Tests de integración
│   ├── __init__.py
│   └── test_api_database.py    # Tests de integración API-BD
├── functional/                 # Tests funcionales
│   ├── __init__.py
│   └── test_user_scenarios.py  # Tests de escenarios de usuario
├── performance/                # Tests de rendimiento
│   ├── __init__.py
│   └── test_load.py            # Tests de carga y rendimiento
└── fixtures/                   # Fixtures de testing
    ├── __init__.py
    └── test_data.py            # Datos de prueba específicos
```

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias de Testing

```bash
pip install -r requirements-testing.txt
```

### 2. Configuración de pytest

El archivo `pytest.ini` ya está configurado con:
- Marcadores para diferentes tipos de tests
- Configuración de cobertura de código
- Filtros de warnings
- Configuración de reportes

### 3. Variables de Entorno (Opcional)

```bash
# Para tests de integración con base de datos real
export QTRAZER_TEST_DB_HOST=localhost
export QTRAZER_TEST_DB_PORT=5432
export QTRAZER_TEST_DB_NAME=test_siniestros
export QTRAZER_TEST_DB_USER=test_user
export QTRAZER_TEST_DB_PASSWORD=test_password
```

## 🧪 Ejecución de Tests

### Ejecutar Todos los Tests

```bash
pytest
```

### Ejecutar Tests por Categoría

```bash
# Tests unitarios
pytest -m unit

# Tests de integración
pytest -m integration

# Tests funcionales
pytest -m functional

# Tests de rendimiento
pytest -m performance
```

### Ejecutar Tests Específicos

```bash
# Tests de una clase específica
pytest tests/unit/test_api_client.py::TestClienteAPI

# Tests de un método específico
pytest tests/unit/test_database.py::TestGestorBaseDatos::test_conectar_exitoso

# Tests que contengan una palabra específica
pytest -k "conexion"
```

### Ejecutar Tests con Cobertura

```bash
# Cobertura básica
pytest --cov=src

# Cobertura con reporte HTML
pytest --cov=src --cov-report=html

# Cobertura con reporte detallado
pytest --cov=src --cov-report=term-missing
```

### Ejecutar Tests en Paralelo

```bash
# Ejecutar tests en 4 procesos paralelos
pytest -n 4

# Ejecutar tests en modo auto (detecta número de CPUs)
pytest -n auto
```

## 📊 Tipos de Tests Implementados

### 1. Tests Unitarios (`tests/unit/`)

**Propósito**: Probar componentes individuales de forma aislada.

**Características**:
- Uso extensivo de mocks para aislar dependencias
- Tests rápidos y determinísticos
- Cobertura completa de lógica de negocio

**Archivos**:
- `test_api_client.py`: Cliente API con mocks de requests
- `test_database.py`: Gestor de BD con mocks de psycopg2
- `test_update_model.py`: Modelo de actualización
- `test_controllers.py`: Controladores principales

### 2. Tests de Integración (`tests/integration/`)

**Propósito**: Probar la interacción entre componentes.

**Características**:
- Prueban flujos completos de datos
- Simulan integraciones reales
- Verifican consistencia entre componentes

**Archivos**:
- `test_api_database.py`: Flujo completo API → BD

### 3. Tests Funcionales (`tests/functional/`)

**Propósito**: Probar escenarios de usuario reales.

**Características**:
- Simulan casos de uso completos
- Prueban la funcionalidad end-to-end
- Verifican comportamiento del sistema

**Archivos**:
- `test_user_scenarios.py`: Escenarios de consulta y actualización

### 4. Tests de Rendimiento (`tests/performance/`)

**Propósito**: Verificar el rendimiento del sistema.

**Características**:
- Prueban con grandes volúmenes de datos
- Verifican tiempos de respuesta
- Monitorean uso de memoria

**Archivos**:
- `test_load.py`: Tests de carga y rendimiento

## 🔧 Fixtures y Datos de Prueba

### Fixtures Comunes (`conftest.py`)

- `mock_database_connection`: Conexión simulada a BD
- `mock_api_response`: Respuestas simuladas de API
- `sample_accident_data`: Datos de muestra de accidentes
- `mock_settings`: Configuración simulada

### Fixtures Específicos (`fixtures/test_data.py`)

- `datos_accidentes_completos`: Datos completos de accidentes
- `datos_actor_vial`: Datos de actores viales
- `datos_vehiculos`: Datos de vehículos
- `datos_causas`: Datos de causas de accidentes
- `datos_vias`: Datos de características de vías

## 📈 Cobertura de Código

### Configuración de Cobertura

El sistema está configurado para generar reportes de cobertura que incluyen:

- **Cobertura por archivo**: Muestra qué archivos están probados
- **Cobertura por línea**: Identifica líneas no cubiertas
- **Reporte HTML**: Interfaz visual para análisis de cobertura

### Ejecutar Cobertura

```bash
# Cobertura básica
pytest --cov=src

# Cobertura con reporte HTML (se genera en htmlcov/)
pytest --cov=src --cov-report=html

# Cobertura con reporte XML (para CI/CD)
pytest --cov=src --cov-report=xml
```

## 🚨 Manejo de Errores en Tests

### Tests de Manejo de Errores

Los tests incluyen verificación de:

- **Errores de conexión**: Timeouts, conexiones fallidas
- **Errores de API**: Respuestas inválidas, errores HTTP
- **Errores de base de datos**: Fallos de consulta, rollbacks
- **Errores de validación**: Datos inválidos, campos faltantes

### Ejemplos de Tests de Error

```python
def test_conectar_error_conexion(self, mock_connect):
    """Prueba el manejo de errores de conexión."""
    mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
    
    gestor = GestorBaseDatos()
    with pytest.raises(Exception, match="Falló la conexión a la base de datos"):
        gestor.conectar()
```

## 🔄 Tests de Concurrencia

### Tests de Threading

Los tests verifican el comportamiento correcto con:

- **Múltiples consultas simultáneas**
- **Actualizaciones concurrentes**
- **Manejo de estados compartidos**
- **Limpieza de recursos**

### Ejemplo de Test de Concurrencia

```python
def test_rendimiento_concurrencia_multiples_consultas(self):
    """Prueba el rendimiento con múltiples consultas simultáneas."""
    # Ejecutar 10 consultas en paralelo
    threads = []
    for i in range(10):
        thread = threading.Thread(target=ejecutar_consulta, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Verificar que todas se completaron
    for thread in threads:
        thread.join()
```

## 📊 Reportes y Análisis

### Generar Reportes HTML

```bash
pytest --cov=src --cov-report=html --html=reports/test_report.html
```

### Reportes Disponibles

- **Cobertura de código**: `htmlcov/index.html`
- **Reporte de tests**: `reports/test_report.html`
- **Reporte de cobertura XML**: Para integración con CI/CD

## 🚀 Integración Continua (CI/CD)

### GitHub Actions

El sistema está preparado para integración con GitHub Actions:

```yaml
- name: Run Tests
  run: |
    pip install -r requirements-testing.txt
    pytest --cov=src --cov-report=xml --cov-report=term-missing
```

### Criterios de Aprobación

- **Todos los tests deben pasar**
- **Cobertura mínima del 80%**
- **Sin warnings críticos**
- **Tests de rendimiento dentro de límites**

## 🐛 Solución de Problemas

### Problemas Comunes

1. **ImportError**: Verificar que el PYTHONPATH incluya el directorio raíz
2. **Mock no funciona**: Verificar que se esté importando correctamente
3. **Tests lentos**: Usar `pytest -x` para parar en el primer fallo
4. **Cobertura baja**: Ejecutar `pytest --cov=src --cov-report=term-missing`

### Debug de Tests

```bash
# Ejecutar con output detallado
pytest -v -s

# Ejecutar un test específico con debug
pytest -v -s tests/unit/test_database.py::TestGestorBaseDatos::test_conectar_exitoso

# Ejecutar con pdb en caso de fallo
pytest --pdb
```

## 📚 Recursos Adicionales

### Documentación de pytest

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)

### Mejores Prácticas

- **Nombres descriptivos**: Los tests deben explicar qué prueban
- **Arrange-Act-Assert**: Estructura clara de los tests
- **Fixtures reutilizables**: Evitar duplicación de código
- **Mocks apropiados**: Solo mockear dependencias externas

### Contribución

Para agregar nuevos tests:

1. **Crear archivo de test** en el directorio apropiado
2. **Usar fixtures existentes** cuando sea posible
3. **Agregar marcadores** apropiados (`@pytest.mark.unit`)
4. **Documentar** el propósito del test
5. **Verificar cobertura** del nuevo código

---

**¡El sistema de testing está listo para asegurar la calidad de Qtrazer! 🎯**
