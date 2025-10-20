-- Script para actualizar tipos de datos de campos que contienen códigos alfanuméricos
-- Ejecutar este script en PostgreSQL para cambiar los campos de INT a VARCHAR

-- ============================================================================
-- ACTUALIZACIÓN DE TIPOS DE DATOS PARA CÓDIGOS ALFANUMÉRICOS
-- ============================================================================

-- Actualizar tabla accidente
ALTER TABLE accidente ALTER COLUMN codigo_accidente TYPE VARCHAR(50);

-- Actualizar tabla vm_acc_actor_vial
ALTER TABLE vm_acc_actor_vial ALTER COLUMN codigo_accidentado TYPE VARCHAR(50);
ALTER TABLE vm_acc_actor_vial ALTER COLUMN codigo_victima TYPE VARCHAR(50);
ALTER TABLE vm_acc_actor_vial ALTER COLUMN codigo_vehiculo TYPE VARCHAR(50);

-- Actualizar tabla vm_acc_causa
ALTER TABLE vm_acc_causa ALTER COLUMN codigo_accidente TYPE VARCHAR(50);
ALTER TABLE vm_acc_causa ALTER COLUMN codigo_vehiculo TYPE VARCHAR(50);

-- Actualizar tabla vm_acc_vehiculo
ALTER TABLE vm_acc_vehiculo ALTER COLUMN codigo_vehiculo TYPE VARCHAR(50);

-- Actualizar tabla vm_acc_vial
ALTER TABLE vm_acc_vial ALTER COLUMN codigo_accidente TYPE VARCHAR(50);
ALTER TABLE vm_acc_vial ALTER COLUMN codigo_via TYPE VARCHAR(50);

-- ============================================================================
-- VERIFICACIÓN DE CAMBIOS
-- ============================================================================

-- Verificar los tipos de datos actualizados
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name IN ('accidente', 'vm_acc_actor_vial', 'vm_acc_causa', 'vm_acc_vehiculo', 'vm_acc_vial')
    AND column_name LIKE '%codigo%'
ORDER BY table_name, column_name;
