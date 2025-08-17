# Manual de Usuario - Sistema Qtrazer

## Índice
1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Inicio del Sistema](#inicio-del-sistema)
5. [Interfaz Principal](#interfaz-principal)
6. [Módulo de Actualización de Base de Datos](#módulo-de-actualización-de-base-de-datos)
7. [Módulo de Consulta de Siniestros](#módulo-de-consulta-de-siniestros)
8. [Funcionalidades Avanzadas](#funcionalidades-avanzadas)
9. [Solución de Problemas](#solución-de-problemas)
10. [Información Legal](#información-legal)

---

## Introducción

**Qtrazer** es un sistema especializado para consultar datos de siniestros viales en Bogotá, desarrollado para proporcionar acceso a información oficial sobre accidentes de tránsito en la ciudad. El sistema permite a los usuarios consultar registros históricos de siniestros viales y mantener actualizada la base de datos local con información proveniente de los repositorios oficiales de la Secretaría Distrital de Movilidad.

### Características Principales
- **Consulta de Siniestros**: Búsqueda y filtrado de registros de accidentes viales
- **Actualización Automática**: Descarga y sincronización de datos oficiales
- **Interfaz Intuitiva**: Diseño moderno y fácil de usar
- **Exportación de Datos**: Generación de reportes en formato Excel
- **Filtros Avanzados**: Búsqueda específica por múltiples criterios

---

## Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo**: Windows 10 o superior
- **Memoria RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en Disco**: 2 GB de espacio libre
- **Python**: Versión 3.8 o superior
- **Conexión a Internet**: Para actualizaciones de base de datos

### Dependencias del Sistema
El sistema requiere las siguientes bibliotecas de Python:
- `tkinter` - Interfaz gráfica
- `pandas` - Manipulación de datos
- `psycopg2` - Conexión a base de datos PostgreSQL
- `requests` - Comunicación con APIs
- `PIL` - Procesamiento de imágenes
- `tkcalendar` - Selector de fechas

---

## Instalación

### Instalación Automática
1. Ejecute el archivo `Qtrazer.exe` (si está disponible)
2. Siga las instrucciones del instalador
3. El sistema se configurará automáticamente

### Instalación Manual
1. Asegúrese de tener Python 3.8+ instalado
2. Clone o descargue el repositorio del proyecto
3. Navegue al directorio del proyecto
4. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Ejecute el archivo principal:
   ```bash
   python src/main.py
   ```

---

## Inicio del Sistema

### Pantalla de Inicio (Splash Screen)
Al iniciar el sistema, se mostrará una pantalla de bienvenida con el logo de Qtrazer durante 4 segundos. Esta pantalla indica que el sistema se está cargando.

### Ventana Principal
Después del splash screen, se abre la ventana principal del sistema que contiene:
- **Logo de Qtrazer** en la parte superior
- **Mensaje de bienvenida** explicando el propósito del sistema
- **Dos botones principales**:
  - Actualizar Base de datos
  - Consultar Siniestros
- **Botón de Finalizar Sesión** en la parte inferior
- **Información legal** sobre el origen de los datos

---

## Interfaz Principal

### Navegación
La interfaz principal es el punto de acceso a todas las funcionalidades del sistema. Desde aquí puede:

1. **Actualizar la Base de Datos**: Acceder al módulo de sincronización
2. **Consultar Siniestros**: Acceder al módulo de consultas
3. **Finalizar Sesión**: Cerrar el sistema completamente

### Diseño Visual
- **Colores**: Esquema de colores verde (#0d9330) para botones principales
- **Tipografía**: Helvetica para mejor legibilidad
- **Responsive**: La interfaz se adapta al tamaño de la ventana
- **Logo**: Imagen corporativa de Qtrazer en la parte superior

---

## Módulo de Actualización de Base de Datos

### Propósito
Este módulo permite sincronizar la base de datos local con los datos oficiales más recientes de la Secretaría de Movilidad de Bogotá.

### Acceso
- Desde la ventana principal, haga clic en **"Actualizar Base de datos"**
- Se abrirá una nueva ventana dedicada a la actualización

### Funcionalidades

#### 1. Panel de Control
- **Botón "Iniciar Actualización"**: Comienza el proceso de sincronización
- **Botón "Cerrar"**: Cierra la ventana de actualización
- **Barra de Progreso**: Muestra el avance del proceso
- **Porcentaje**: Indicador numérico del progreso

#### 2. Área de Log
- **Registro en Tiempo Real**: Muestra todos los eventos del proceso
- **Códigos de Color**:
  - 🔵 **Azul**: Mensajes de inicio
  - 🟢 **Verde**: Información de progreso y éxito
  - 🔴 **Rojo**: Errores y advertencias
  - ⚫ **Negro**: Información general

#### 3. Estados del Proceso
- **"Listo para actualizar"**: Estado inicial
- **"Iniciando actualización..."**: Proceso comenzando
- **"Progreso: X registros (Y%)"**: Actualización en curso
- **"Actualización completada exitosamente"**: Proceso finalizado

### Proceso de Actualización

#### Fase 1: Verificación de Conexión
- El sistema verifica la conectividad con la base de datos
- Obtiene el ObjectID más reciente para determinar qué datos descargar

#### Fase 2: Descarga de Datos
- Se conecta a las APIs oficiales de la Secretaría de Movilidad
- Descarga datos de las siguientes tablas:
  - **Accidentes**: Información general de siniestros
  - **Actores Viales**: Personas involucradas en accidentes
  - **Causas**: Motivos de los accidentes
  - **Vehículos**: Información de vehículos involucrados
  - **Vías**: Características de las carreteras

#### Fase 3: Procesamiento
- Los datos se procesan y validan
- Se insertan en la base de datos local
- Se actualiza el progreso en tiempo real

#### Fase 4: Finalización
- Se verifica la integridad de los datos
- Se muestra el resumen final
- Los botones se habilitan nuevamente

### Consideraciones Importantes
- **No cierre la ventana** durante la actualización
- **Mantenga la conexión a internet** activa
- **El proceso puede tomar varios minutos** dependiendo de la cantidad de datos
- **Los datos existentes se preservan** y solo se agregan los nuevos

---

## Módulo de Consulta de Siniestros

### Propósito
Este módulo permite buscar, filtrar y analizar los registros de siniestros viales almacenados en la base de datos local.

### Acceso
- Desde la ventana principal, haga clic en **"Consultar Siniestros"**
- Se abrirá una ventana dedicada a las consultas

### Funcionalidades Principales

#### 1. Selección de Fechas
- **Fecha Inicial**: Seleccione la fecha de inicio del período de consulta
- **Fecha Final**: Seleccione la fecha de fin del período de consulta
- **Formato**: DD/MM/AAAA
- **Selector de Calendario**: Haga clic en el campo de fecha para abrir un calendario

#### 2. Botones de Control
- **"Consultar"**: Inicia la búsqueda con los parámetros seleccionados
- **"Cancelar"**: Detiene una consulta en progreso
- **"Filtros Avanzados"**: Muestra/oculta opciones de filtrado adicionales

#### 3. Filtros Avanzados
Haga clic en **"Filtros Avanzados ▼"** para acceder a opciones adicionales:

- **Localidad**: Filtra por barrio o zona de Bogotá
- **Vehículo**: Filtra por tipo de vehículo involucrado
- **Estado Actor Vial**: Filtra por condición de la persona (Herido, Ileso, Muerto)
- **Causante**: Filtra por responsable del accidente

#### 4. Aplicación de Filtros
- **"Aplicar Filtros"**: Ejecuta el filtrado con los criterios seleccionados
- **"Limpiar Filtros"**: Restablece todos los filtros a valores vacíos

### Tabla de Resultados

#### Columnas Disponibles
La tabla muestra la siguiente información para cada siniestro:

| Columna | Descripción |
|---------|-------------|
| **ID** | Identificador único del registro |
| **Formulario** | Número de formulario del accidente |
| **Fecha** | Fecha de ocurrencia del siniestro |
| **Hora** | Hora aproximada del accidente |
| **Localidad** | Barrio o zona de Bogotá |
| **Clases Vehículos** | Tipos de vehículos involucrados |
| **Placas** | Números de placa de los vehículos |
| **Condiciones Actores** | Estado de las personas involucradas |
| **Fallecidos** | Número de personas fallecidas |
| **Heridos** | Número de personas heridas |
| **Ilesos** | Número de personas ilesas |
| **Estados** | Condición de los actores viales |
| **Géneros** | Género de las personas involucradas |
| **Edades** | Edades de las personas involucradas |
| **Causante** | Responsable del accidente |
| **Causa** | Descripción de la causa del accidente |
| **Terreno Vía** | Tipo de superficie de la carretera |
| **Estado Vía** | Condición de la vía |

#### Navegación en la Tabla
- **Scroll Vertical**: Use la rueda del mouse o la barra de desplazamiento
- **Scroll Horizontal**: Use la barra de desplazamiento horizontal
- **Ordenamiento**: Haga clic en los encabezados de columna para ordenar
- **Selección**: Haga clic en una fila para seleccionarla

### Funcionalidades de Exportación

#### Exportar a Excel
- Haga clic en **"Exportar a Excel"**
- Seleccione la ubicación donde guardar el archivo
- El archivo contendrá todos los resultados filtrados
- Formato: Archivo .xlsx compatible con Microsoft Excel

### Navegación y Control

#### Botones de Navegación
- **"Volver al Inicio"**: Regresa a la ventana principal
- **"Cerrar"**: Cierra la ventana de consulta

#### Barra de Estado
- **Indicador de Progreso**: Muestra el estado de la consulta
- **Mensajes de Estado**: Informa sobre el proceso actual

---

## Funcionalidades Avanzadas

### Filtrado Inteligente
- **Filtros Combinados**: Puede aplicar múltiples filtros simultáneamente
- **Búsqueda por Rango**: Seleccione períodos específicos de tiempo
- **Filtros Dinámicos**: Los valores disponibles se actualizan según los resultados

### Gestión de Datos
- **Conexión a Base de Datos**: Integración con PostgreSQL
- **Sincronización Automática**: Descarga de datos oficiales
- **Validación de Datos**: Verificación de integridad

### Interfaz Responsiva
- **Adaptación de Tamaño**: La interfaz se ajusta al tamaño de la ventana
- **Scroll Inteligente**: Navegación fluida en tablas grandes
- **Diseño Moderno**: Interfaz gráfica profesional

---

## Solución de Problemas

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
**Síntomas**: Mensaje "Error: list index out of range" en el log
**Solución**:
- Verifique que el servidor de base de datos esté activo
- Confirme las credenciales de conexión
- Revise la conectividad de red

#### 2. Error al Actualizar Tablas
**Síntomas**: Mensaje "Error al actualizar la tabla 'X'"
**Solución**:
- Verifique la conexión a internet
- Confirme que las APIs estén disponibles
- Revise los permisos de escritura en la base de datos

#### 3. Problemas de Rendimiento
**Síntomas**: Consultas lentas o interfaz no responsiva
**Solución**:
- Cierre otras aplicaciones que consuman recursos
- Verifique el espacio disponible en disco
- Considere aumentar la memoria RAM

#### 4. Errores de Imagen
**Síntomas**: Logo no se muestra correctamente
**Solución**:
- Verifique que los archivos de imagen estén en la carpeta `assets/`
- Confirme que las imágenes no estén corruptas
- Reinicie la aplicación

### Logs y Diagnóstico
- **Área de Log**: Revise los mensajes en tiempo real
- **Códigos de Color**: Identifique rápidamente el tipo de mensaje
- **Mensajes de Error**: Copie los mensajes de error para soporte técnico

### Reinicio del Sistema
Si experimenta problemas persistentes:
1. Cierre completamente la aplicación
2. Espere 10 segundos
3. Reinicie la aplicación
4. Si el problema persiste, contacte al soporte técnico

---

## Información Legal

### Origen de los Datos
Los datos consultados y presentados en este sistema provienen del repositorio oficial de datos abiertos de la Secretaría Distrital de Movilidad de Bogotá, disponible en [datos.movilidadbogota.gov.co](https://datos.movilidadbogota.gov.co).

### Marco Legal
Estos conjuntos de datos son de acceso público y están disponibles para su uso y reutilización sin restricciones legales, conforme a la **Ley 1712 de 2014** sobre Transparencia y Acceso a la Información Pública Nacional.

### Responsabilidad
La Secretaría de Movilidad ha dispuesto esta información en formatos estándar e interoperables, permitiendo su aprovechamiento por parte de:
- Ciudadanos
- Entidades públicas y privadas
- Academia
- Investigadores

### Uso de Datos
- Los datos son de carácter público y oficial
- Se recomienda citar la fuente en cualquier publicación o análisis
- La información se actualiza periódicamente según la disponibilidad oficial

---

## Soporte Técnico

### Contacto
Para soporte técnico o reportar problemas:
- **Email**: [soporte@qtrazer.com](mailto:soporte@qtrazer.com)
- **Documentación**: Consulte la documentación técnica del proyecto
- **Issues**: Reporte problemas a través del sistema de gestión de incidencias

### Recursos Adicionales
- **Manual Técnico**: Documentación para desarrolladores
- **API Reference**: Referencia de las APIs utilizadas
- **Base de Conocimientos**: Soluciones a problemas comunes

---

## Conclusión

El sistema Qtrazer proporciona una herramienta completa y profesional para el análisis de datos de siniestros viales en Bogotá. Con su interfaz intuitiva, funcionalidades avanzadas de filtrado y capacidad de exportación, permite a los usuarios acceder fácilmente a información oficial y actualizada sobre la seguridad vial en la ciudad.

Para obtener el máximo provecho del sistema:
1. **Mantenga la base de datos actualizada** regularmente
2. **Utilice los filtros avanzados** para consultas específicas
3. **Exporte los resultados** para análisis posteriores
4. **Revise los logs** en caso de problemas
5. **Consulte la documentación** para funcionalidades avanzadas

---

*Manual de Usuario - Sistema Qtrazer v1.0*  
*Última actualización: Enero 2025* 