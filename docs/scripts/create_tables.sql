-- Script de creación de tablas para el sistema Qtrazer
-- Base de datos: Siniestros
-- Usuario: Analyst
-- Fecha: Enero 2025
-- Versión: 1.0

-- Conectar a la base de datos
\c "Siniestros";

-- ============================================================================
-- CREACIÓN DE TABLAS PRINCIPALES
-- ============================================================================

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

-- ============================================================================
-- CREACIÓN DE ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================================================

-- Índices para la tabla accidente
CREATE INDEX IF NOT EXISTS idx_accidente_formulario ON accidente(formulario);
CREATE INDEX IF NOT EXISTS idx_accidente_fecha ON accidente(fecha_ocurrencia_acc);
CREATE INDEX IF NOT EXISTS idx_accidente_localidad ON accidente(localidad);
CREATE INDEX IF NOT EXISTS idx_accidente_fecha_hora ON accidente(fecha_ocurrencia_acc, hora_ocurrencia_acc);
CREATE INDEX IF NOT EXISTS idx_accidente_localidad_fecha ON accidente(localidad, fecha_ocurrencia_acc);

-- Índices para la tabla vm_acc_actor_vial
CREATE INDEX IF NOT EXISTS idx_actor_vial_formulario ON vm_acc_actor_vial(formulario);
CREATE INDEX IF NOT EXISTS idx_actor_vial_estado ON vm_acc_actor_vial(estado);
CREATE INDEX IF NOT EXISTS idx_actor_vial_edad ON vm_acc_actor_vial(edad);
CREATE INDEX IF NOT EXISTS idx_actor_vial_genero ON vm_acc_actor_vial(genero);

-- Índices para la tabla vm_acc_causa
CREATE INDEX IF NOT EXISTS idx_causa_formulario ON vm_acc_causa(formulario);
CREATE INDEX IF NOT EXISTS idx_causa_tipo ON vm_acc_causa(tipo);
CREATE INDEX IF NOT EXISTS idx_causa_tipo_causa ON vm_acc_causa(tipo_causa);

-- Índices para la tabla vm_acc_vehiculo
CREATE INDEX IF NOT EXISTS idx_vehiculo_formulario ON vm_acc_vehiculo(formulario);
CREATE INDEX IF NOT EXISTS idx_vehiculo_clase ON vm_acc_vehiculo(clase);
CREATE INDEX IF NOT EXISTS idx_vehiculo_placa ON vm_acc_vehiculo(placa);

-- Índices para la tabla vm_acc_vial
CREATE INDEX IF NOT EXISTS idx_vial_formulario ON vm_acc_vial(formulario);
CREATE INDEX IF NOT EXISTS idx_vial_material ON vm_acc_vial(material);
CREATE INDEX IF NOT EXISTS idx_vial_estado ON vm_acc_vial(estado);

-- ============================================================================
-- CREACIÓN DE RESTRICCIONES Y CONSTRAINTS
-- ============================================================================

-- Agregar constraints de validación
ALTER TABLE accidente ADD CONSTRAINT chk_ano_accidente CHECK (ano_ocurrencia_acc >= 2000 AND ano_ocurrencia_acc <= 2030);
ALTER TABLE accidente ADD CONSTRAINT chk_mes_accidente CHECK (mes_ocurrencia_acc IN ('ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'));
ALTER TABLE accidente ADD CONSTRAINT chk_dia_accidente CHECK (dia_ocurrencia_acc >= 1 AND dia_ocurrencia_acc <= 7);

ALTER TABLE vm_acc_actor_vial ADD CONSTRAINT chk_estado_actor CHECK (estado IN ('HERIDO', 'ILESO', 'MUERTO'));
ALTER TABLE vm_acc_actor_vial ADD CONSTRAINT chk_genero_actor CHECK (genero IN ('MASCULINO', 'FEMENINO'));
ALTER TABLE vm_acc_actor_vial ADD CONSTRAINT chk_edad_actor CHECK (edad >= 0 AND edad <= 120);

ALTER TABLE vm_acc_vehiculo ADD CONSTRAINT chk_enfuga_vehiculo CHECK (enfuga IN ('SI', 'NO'));

-- ============================================================================
-- CREACIÓN DE VISTAS PARA CONSULTAS FRECUENTES
-- ============================================================================

-- Vista para resumen de accidentes por localidad
CREATE OR REPLACE VIEW v_resumen_accidentes_localidad AS
SELECT 
    localidad,
    COUNT(*) as total_accidentes,
    COUNT(DISTINCT DATE(fecha_ocurrencia_acc)) as dias_con_accidentes,
    MIN(fecha_ocurrencia_acc) as primer_accidente,
    MAX(fecha_ocurrencia_acc) as ultimo_accidente
FROM accidente 
WHERE localidad IS NOT NULL
GROUP BY localidad
ORDER BY total_accidentes DESC;

-- Vista para resumen de víctimas por estado
CREATE OR REPLACE VIEW v_resumen_victimas_estado AS
SELECT 
    estado,
    COUNT(*) as total_victimas,
    COUNT(CASE WHEN genero = 'MASCULINO' THEN 1 END) as masculino,
    COUNT(CASE WHEN genero = 'FEMENINO' THEN 1 END) as femenino,
    AVG(edad) as edad_promedio
FROM vm_acc_actor_vial 
WHERE estado IS NOT NULL
GROUP BY estado
ORDER BY total_victimas DESC;

-- Vista para resumen de vehículos por clase
CREATE OR REPLACE VIEW v_resumen_vehiculos_clase AS
SELECT 
    clase,
    COUNT(*) as total_vehiculos,
    COUNT(DISTINCT formulario) as accidentes_involucrados
FROM vm_acc_vehiculo 
WHERE clase IS NOT NULL
GROUP BY clase
ORDER BY total_vehiculos DESC;

-- ============================================================================
-- FUNCIONES PARA MANTENIMIENTO
-- ============================================================================

-- Función para limpiar registros duplicados
CREATE OR REPLACE FUNCTION limpiar_duplicados_accidente()
RETURNS INTEGER AS $$
DECLARE
    registros_eliminados INTEGER;
BEGIN
    DELETE FROM accidente a1
    WHERE a1.objectid NOT IN (
        SELECT MIN(a2.objectid)
        FROM accidente a2
        GROUP BY a2.formulario
    );
    
    GET DIAGNOSTICS registros_eliminados = ROW_COUNT;
    RETURN registros_eliminados;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas de la base de datos
CREATE OR REPLACE FUNCTION obtener_estadisticas_bd()
RETURNS TABLE(
    tabla VARCHAR,
    total_registros BIGINT,
    ultima_actualizacion TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'accidente'::VARCHAR as tabla,
        COUNT(*)::BIGINT as total_registros,
        MAX(fecha_hora_acc) as ultima_actualizacion
    FROM accidente
    UNION ALL
    SELECT 
        'vm_acc_actor_vial'::VARCHAR,
        COUNT(*)::BIGINT,
        MAX(fecha_posterior_muerte)
    FROM vm_acc_actor_vial
    UNION ALL
    SELECT 
        'vm_acc_causa'::VARCHAR,
        COUNT(*)::BIGINT,
        NULL::TIMESTAMP
    FROM vm_acc_causa
    UNION ALL
    SELECT 
        'vm_acc_vehiculo'::VARCHAR,
        COUNT(*)::BIGINT,
        NULL::TIMESTAMP
    FROM vm_acc_vehiculo
    UNION ALL
    SELECT 
        'vm_acc_vial'::VARCHAR,
        COUNT(*)::BIGINT,
        NULL::TIMESTAMP
    FROM vm_acc_vial;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS PARA MANTENER INTEGRIDAD DE DATOS
-- ============================================================================

-- Trigger para actualizar fecha_hora_acc cuando se modifica fecha_ocurrencia_acc
CREATE OR REPLACE FUNCTION actualizar_fecha_hora_acc()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_ocurrencia_acc IS NOT NULL AND NEW.hora_ocurrencia_acc IS NOT NULL THEN
        NEW.fecha_hora_acc = (NEW.fecha_ocurrencia_acc || ' ' || NEW.hora_ocurrencia_acc)::TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_fecha_hora_acc
    BEFORE INSERT OR UPDATE ON accidente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_hora_acc();

-- Trigger para validar edad en actores viales
CREATE OR REPLACE FUNCTION validar_edad_actor()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.edad IS NOT NULL AND (NEW.edad < 0 OR NEW.edad > 120) THEN
        RAISE EXCEPTION 'La edad debe estar entre 0 y 120 años';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validar_edad_actor
    BEFORE INSERT OR UPDATE ON vm_acc_actor_vial
    FOR EACH ROW
    EXECUTE FUNCTION validar_edad_actor();

-- ============================================================================
-- ASIGNACIÓN DE PERMISOS AL USUARIO ANALYST
-- ============================================================================

-- Asignar permisos en todas las tablas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "Analyst";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "Analyst";

-- Asignar permisos en las vistas
GRANT SELECT ON v_resumen_accidentes_localidad TO "Analyst";
GRANT SELECT ON v_resumen_victimas_estado TO "Analyst";
GRANT SELECT ON v_resumen_vehiculos_clase TO "Analyst";

-- Asignar permisos en las funciones
GRANT EXECUTE ON FUNCTION limpiar_duplicados_accidente() TO "Analyst";
GRANT EXECUTE ON FUNCTION obtener_estadisticas_bd() TO "Analyst";

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

-- Verificar creación de tablas
\dt

-- Verificar creación de índices
\di

-- Verificar creación de vistas
\dv

-- Verificar creación de funciones
\df

-- Verificar permisos del usuario Analyst
\du "Analyst"

-- Mostrar estadísticas iniciales
SELECT obtener_estadisticas_bd();

-- Mensaje de confirmación
\echo '==============================================='
\echo 'SISTEMA QTRAZER - BASE DE DATOS CONFIGURADA'
\echo '==============================================='
\echo 'Tablas creadas exitosamente'
\echo 'Índices configurados para optimización'
\echo 'Vistas creadas para consultas frecuentes'
\echo 'Funciones de mantenimiento implementadas'
\echo 'Triggers configurados para integridad'
\echo 'Usuario Analyst configurado con permisos'
\echo '==============================================='
