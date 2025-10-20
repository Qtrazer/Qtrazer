-- Script de creación de tablas para el sistema Qtrazer
-- Base de datos: Siniestros
-- Usuario: Por definir (Agregarlo al final del documento "CREACIÓN DE USUARIO Y ASIGNACIÓN DE PERMISOS")
-- Contraseña: Por definir  (Agregarlo al final del documento "CREACIÓN DE USUARIO Y ASIGNACIÓN DE PERMISOS")

-- ============================================================================
-- CREACIÓN DE TABLAS PRINCIPALES
-- ============================================================================

-- Crear tabla de accidentes
CREATE TABLE IF NOT EXISTS accidente (
    objectid BIGINT PRIMARY KEY,
	Formulario VARCHAR(50),
	Codigo_Accidente VARCHAR(50),
    Fecha_ocurrencia_acc DATE,
    Hora_ocurrencia_acc TIME,
    Ano_ocurrencia_acc INT,
    Mes_ocurrencia_acc VARCHAR(20),
    Dia_ocurrencia_acc VARCHAR(20),
    Direccion VARCHAR(255),
    Gravedad VARCHAR(50),
    Clase_acc VARCHAR(100),
    Localidad VARCHAR(100),
    Municipio VARCHAR(100),
    Fecha_hora_acc TIMESTAMP,
    Latitud VARCHAR(20),
    Longitud VARCHAR(20),
    Civ INT,
    Pk_calzada INT
);

-- Crear tabla de actores viales
CREATE TABLE IF NOT EXISTS vm_acc_actor_vial (
    objectid BIGINT PRIMARY KEY,
    Condicion_a VARCHAR(100),
    Formulario VARCHAR(50),
    Codigo_accidentado VARCHAR(50),
    Codigo_victima VARCHAR(50),
    Codigo_vehiculo VARCHAR(50),
    Condicion VARCHAR(100),
    Estado VARCHAR(100),
    Muerte_posterior VARCHAR(15),
    Fecha_posterior_muerte VARCHAR(255),
    Genero VARCHAR(50),
    Fecha_nacimiento DATE,
    Edad VARCHAR(5),
    Codigo VARCHAR(100)
);

-- Crear tabla de causas
CREATE TABLE IF NOT EXISTS vm_acc_causa (
    objectid BIGINT PRIMARY KEY,
	Codigo_ac_vh VARCHAR(50),
    Formulario VARCHAR(50),
    Codigo_accidente VARCHAR(50),
    Codigo_vehiculo VARCHAR(50),
    Codigo_causa VARCHAR(10),
    Nombre TEXT,
    Tipo VARCHAR(5),
    Descripcion2 TEXT,
    Tipo_causa VARCHAR(20),
    Codigo VARCHAR(50)
);

-- Crear tabla de vehículos
CREATE TABLE IF NOT EXISTS vm_acc_vehiculo (
    objectid BIGINT PRIMARY KEY,
    Formulario VARCHAR(20),
    Placa VARCHAR(10),
    Codigo_Vehiculo VARCHAR(50),
    Clase VARCHAR(50),
    Servicio VARCHAR(50),
    Modalidad VARCHAR(50),
    Enfuga CHAR(5),
    Codigo VARCHAR(20)
);

-- Crear tabla de vías
CREATE TABLE IF NOT EXISTS vm_acc_vial (
    objectid BIGINT PRIMARY KEY,
    Formulario VARCHAR(20),
    Codigo_accidente VARCHAR(50),
    Codigo_via VARCHAR(50),
    Geometrica_a VARCHAR(20),
    Geometrica_b VARCHAR(20),
    Geometrica_c VARCHAR(50),
    Utilizacion VARCHAR(20),
    Calzadas VARCHAR(20),
    Carriles VARCHAR(20),
    Material VARCHAR(20),
    Estado VARCHAR(20),
    Condiciones VARCHAR(50),
    Iluminacion_a VARCHAR(20),
    Iluminacion_b VARCHAR(20),
    Agente_transito VARCHAR(10),
    Semaforo VARCHAR(20),
    Visual VARCHAR(50),
    Codigo VARCHAR(20)
);

-- ============================================================================
-- CREACIÓN DE ÍNDICES BÁSICOS PARA MEJORAR RENDIMIENTO
-- ============================================================================

-- Índices para la tabla accidente
CREATE INDEX IF NOT EXISTS idx_accidente_formulario ON accidente(formulario);
CREATE INDEX IF NOT EXISTS idx_accidente_fecha ON accidente(fecha_ocurrencia_acc);
CREATE INDEX IF NOT EXISTS idx_accidente_localidad ON accidente(localidad);

-- Índices para la tabla vm_acc_actor_vial
CREATE INDEX IF NOT EXISTS idx_actor_vial_formulario ON vm_acc_actor_vial(formulario);

-- Índices para la tabla vm_acc_causa
CREATE INDEX IF NOT EXISTS idx_causa_formulario ON vm_acc_causa(formulario);

-- Índices para la tabla vm_acc_vehiculo
CREATE INDEX IF NOT EXISTS idx_vehiculo_formulario ON vm_acc_vehiculo(formulario);

-- Índices para la tabla vm_acc_vial
CREATE INDEX IF NOT EXISTS idx_vial_formulario ON vm_acc_vial(formulario);

-- ============================================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN DE CONSULTAS
-- ============================================================================

-- Índices compuestos para mejorar el rendimiento de las consultas por fecha
CREATE INDEX IF NOT EXISTS idx_accidente_fecha_formulario ON accidente(fecha_ocurrencia_acc, formulario);

-- Índices adicionales para las tablas relacionadas
CREATE INDEX IF NOT EXISTS idx_actor_vial_estado ON vm_acc_actor_vial(estado);
CREATE INDEX IF NOT EXISTS idx_actor_vial_condicion ON vm_acc_actor_vial(condicion_a);

-- Índices para optimizar las consultas de agregación
CREATE INDEX IF NOT EXISTS idx_vehiculo_clase ON vm_acc_vehiculo(clase);
CREATE INDEX IF NOT EXISTS idx_causa_tipo ON vm_acc_causa(tipo_causa);
CREATE INDEX IF NOT EXISTS idx_vial_material ON vm_acc_vial(material);
CREATE INDEX IF NOT EXISTS idx_vial_estado ON vm_acc_vial(estado);

-- ============================================================================
-- CREACIÓN DE USUARIO Y ASIGNACIÓN DE PERMISOS
-- ============================================================================

-- Crear usuario Analyst si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'Por definir') THEN
        CREATE USER "Por definir" WITH PASSWORD 'Por definir';
    END IF;
END
$$;

-- Asignar permisos básicos (consultar e insertar datos)
GRANT CONNECT ON DATABASE "Por definir" TO "Por definir";
GRANT USAGE ON SCHEMA public TO "Por definir";
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO "Por definir";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "Por definir";
