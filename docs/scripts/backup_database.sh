#!/bin/bash

# ============================================================================
# Script de backup automático para PostgreSQL - Sistema Qtrazer
# ============================================================================
# Fecha: Enero 2025
# Versión: 1.0
# Descripción: Script para realizar backups automáticos de la base de datos
#              del sistema Qtrazer con compresión y limpieza automática
# ============================================================================

# Configuración del script
DB_NAME="Siniestros"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgresql"
LOG_DIR="/var/log/qtrazer"
RETENTION_DAYS=7
COMPRESSION_LEVEL=9

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $timestamp: $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $timestamp: $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $timestamp: $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $timestamp: $message"
            ;;
    esac
    
    # Escribir en archivo de log
    echo "[$level] $timestamp: $message" >> "$LOG_DIR/backup.log"
}

# Función para verificar dependencias
check_dependencies() {
    log_message "INFO" "Verificando dependencias..."
    
    # Verificar si PostgreSQL está instalado
    if ! command -v psql &> /dev/null; then
        log_message "ERROR" "PostgreSQL no está instalado o no está en el PATH"
        exit 1
    fi
    
    # Verificar si pg_dump está disponible
    if ! command -v pg_dump &> /dev/null; then
        log_message "ERROR" "pg_dump no está disponible"
        exit 1
    fi
    
    # Verificar si gzip está disponible
    if ! command -v gzip &> /dev/null; then
        log_message "WARN" "gzip no está disponible, los backups no se comprimirán"
        COMPRESSION_LEVEL=0
    fi
    
    log_message "INFO" "Dependencias verificadas correctamente"
}

# Función para crear directorios necesarios
create_directories() {
    log_message "INFO" "Creando directorios necesarios..."
    
    # Crear directorio de backup si no existe
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log_message "INFO" "Directorio de backup creado: $BACKUP_DIR"
    fi
    
    # Crear directorio de logs si no existe
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        log_message "INFO" "Directorio de logs creado: $LOG_DIR"
    fi
    
    # Verificar permisos
    chmod 755 "$BACKUP_DIR"
    chmod 755 "$LOG_DIR"
}

# Función para verificar conectividad a la base de datos
check_database_connection() {
    log_message "INFO" "Verificando conectividad a la base de datos..."
    
    if pg_isready -U "$DB_USER" -d "$DB_NAME" &> /dev/null; then
        log_message "INFO" "Conexión a la base de datos exitosa"
        return 0
    else
        log_message "ERROR" "No se puede conectar a la base de datos"
        return 1
    fi
}

# Función para obtener estadísticas de la base de datos
get_database_stats() {
    log_message "INFO" "Obteniendo estadísticas de la base de datos..."
    
    local stats_query="
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    "
    
    local total_size=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename)))
        FROM pg_tables 
        WHERE schemaname = 'public';
    " | xargs)
    
    log_message "INFO" "Tamaño total de la base de datos: $total_size"
    
    # Guardar estadísticas en archivo
    psql -U "$DB_USER" -d "$DB_NAME" -c "$stats_query" > "$BACKUP_DIR/db_stats_$(date +%Y%m%d_%H%M%S).txt"
}

# Función para realizar el backup
perform_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="qtrazer_backup_$timestamp.sql"
    local backup_path="$BACKUP_DIR/$backup_file"
    
    log_message "INFO" "Iniciando backup de la base de datos..."
    log_message "INFO" "Archivo de backup: $backup_file"
    
    # Realizar backup con pg_dump
    if pg_dump -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --no-owner \
        --no-privileges \
        --format=plain \
        --file="$backup_path" 2>> "$LOG_DIR/backup.log"; then
        
        log_message "INFO" "Backup completado exitosamente: $backup_file"
        
        # Verificar tamaño del backup
        local backup_size=$(du -h "$backup_path" | cut -f1)
        log_message "INFO" "Tamaño del backup: $backup_size"
        
        # Comprimir backup si gzip está disponible
        if [ $COMPRESSION_LEVEL -gt 0 ]; then
            log_message "INFO" "Comprimiendo backup..."
            if gzip -$COMPRESSION_LEVEL "$backup_path"; then
                local compressed_size=$(du -h "$backup_path.gz" | cut -f1)
                local compression_ratio=$(echo "scale=1; $(stat -c%s "$backup_path.gz") * 100 / $(stat -c%s "$backup_path")" | bc -l 2>/dev/null || echo "N/A")
                log_message "INFO" "Backup comprimido: $backup_file.gz ($compressed_size, ratio: ${compression_ratio}%)"
                
                # Eliminar archivo sin comprimir
                rm -f "$backup_path"
            else
                log_message "WARN" "No se pudo comprimir el backup, manteniendo archivo original"
            fi
        fi
        
        # Crear archivo de metadatos
        create_backup_metadata "$backup_file" "$backup_size" "$timestamp"
        
        return 0
    else
        log_message "ERROR" "Falló la creación del backup"
        return 1
    fi
}

# Función para crear metadatos del backup
create_backup_metadata() {
    local backup_file=$1
    local backup_size=$2
    local timestamp=$3
    
    local metadata_file="$BACKUP_DIR/${backup_file%.*}.meta"
    
    cat > "$metadata_file" << EOF
# Metadatos del Backup - Sistema Qtrazer
# =====================================
Archivo: $backup_file
Fecha: $(date '+%Y-%m-%d %H:%M:%S')
Tamaño: $backup_size
Base de datos: $DB_NAME
Usuario: $DB_USER
Versión PostgreSQL: $(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version();" | xargs)
Sistema operativo: $(uname -a)
Hostname: $(hostname)
Script: $0
EOF
    
    log_message "INFO" "Metadatos del backup creados: ${backup_file%.*}.meta"
}

# Función para limpiar backups antiguos
cleanup_old_backups() {
    log_message "INFO" "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
    
    local deleted_count=0
    
    # Encontrar y eliminar backups antiguos
    find "$BACKUP_DIR" -name "qtrazer_backup_*.sql*" -mtime +$RETENTION_DAYS -print0 | while IFS= read -r -d '' file; do
        log_message "INFO" "Eliminando backup antiguo: $(basename "$file")"
        rm -f "$file"
        ((deleted_count++))
    done
    
    # Eliminar archivos de metadatos antiguos
    find "$BACKUP_DIR" -name "*.meta" -mtime +$RETENTION_DAYS -print0 | while IFS= read -r -d '' file; do
        log_message "INFO" "Eliminando metadatos antiguos: $(basename "$file")"
        rm -f "$file"
    done
    
    # Eliminar archivos de estadísticas antiguos
    find "$BACKUP_DIR" -name "db_stats_*.txt" -mtime +$RETENTION_DAYS -print0 | while IFS= read -r -d '' file; do
        log_message "INFO" "Eliminando estadísticas antiguas: $(basename "$file")"
        rm -f "$file"
    done
    
    log_message "INFO" "Limpieza completada"
}

# Función para verificar integridad del backup
verify_backup_integrity() {
    local backup_file=$1
    
    log_message "INFO" "Verificando integridad del backup..."
    
    # Verificar que el archivo existe
    if [ ! -f "$backup_file" ]; then
        log_message "ERROR" "Archivo de backup no encontrado: $backup_file"
        return 1
    fi
    
    # Verificar que el archivo no esté vacío
    if [ ! -s "$backup_file" ]; then
        log_message "ERROR" "Archivo de backup está vacío: $backup_file"
        return 1
    fi
    
    # Verificar que el archivo contenga datos SQL válidos
    if head -n 1 "$backup_file" | grep -q "PostgreSQL database dump"; then
        log_message "INFO" "Integridad del backup verificada correctamente"
        return 0
    else
        log_message "WARN" "El archivo de backup no parece ser un dump válido de PostgreSQL"
        return 1
    fi
}

# Función para generar reporte de backup
generate_backup_report() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="$BACKUP_DIR/backup_report_$timestamp.txt"
    
    log_message "INFO" "Generando reporte de backup..."
    
    cat > "$report_file" << EOF
# Reporte de Backup - Sistema Qtrazer
# ===================================
Fecha del reporte: $(date '+%Y-%m-%d %H:%M:%S')
Script ejecutado: $0
Usuario: $(whoami)
Hostname: $(hostname)

## Resumen del Backup
- Base de datos: $DB_NAME
- Usuario de backup: $DB_USER
- Directorio de backup: $BACKUP_DIR
- Retención configurada: $RETENTION_DAYS días
- Compresión: $([ $COMPRESSION_LEVEL -gt 0 ] && echo "Habilitada (nivel $COMPRESSION_LEVEL)" || echo "Deshabilitada")

## Estadísticas de la Base de Datos
$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
")

## Backups Disponibles
$(ls -lh "$BACKUP_DIR"/qtrazer_backup_*.sql* 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' || echo "No hay backups disponibles")

## Espacio en Disco
$(df -h "$BACKUP_DIR" | tail -1 | awk '{print "Disco: " $1, "Tamaño: " $2, "Usado: " $3, "Disponible: " $4, "Uso: " $5}')

## Logs del Sistema
$(tail -20 "$LOG_DIR/backup.log" 2>/dev/null || echo "No hay logs disponibles")
EOF
    
    log_message "INFO" "Reporte de backup generado: backup_report_$timestamp.txt"
}

# Función para enviar notificación (opcional)
send_notification() {
    local status=$1
    local message=$2
    
    # Aquí puedes implementar notificaciones por email, Slack, etc.
    # Por ahora solo se registra en el log
    
    if [ "$status" = "SUCCESS" ]; then
        log_message "INFO" "Notificación: Backup completado exitosamente"
    else
        log_message "ERROR" "Notificación: Backup falló - $message"
    fi
}

# Función principal
main() {
    local start_time=$(date +%s)
    
    log_message "INFO" "==============================================="
    log_message "INFO" "INICIANDO PROCESO DE BACKUP AUTOMÁTICO"
    log_message "INFO" "==============================================="
    log_message "INFO" "Script: $0"
    log_message "INFO" "Usuario: $(whoami)"
    log_message "INFO" "Hostname: $(hostname)"
    log_message "INFO" "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Verificar dependencias
    check_dependencies || exit 1
    
    # Crear directorios necesarios
    create_directories
    
    # Verificar conectividad a la base de datos
    check_database_connection || exit 1
    
    # Obtener estadísticas de la base de datos
    get_database_stats
    
    # Realizar backup
    if perform_backup; then
        # Verificar integridad del backup
        local backup_file="$BACKUP_DIR/qtrazer_backup_$(date +%Y%m%d_%H%M%S).sql"
        if [ -f "${backup_file}.gz" ]; then
            backup_file="${backup_file}.gz"
        fi
        
        if verify_backup_integrity "$backup_file"; then
            # Limpiar backups antiguos
            cleanup_old_backups
            
            # Generar reporte
            generate_backup_report
            
            # Calcular tiempo total
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            log_message "INFO" "==============================================="
            log_message "INFO" "BACKUP COMPLETADO EXITOSAMENTE"
            log_message "INFO" "==============================================="
            log_message "INFO" "Duración total: ${duration} segundos"
            log_message "INFO" "Archivo de backup: $(basename "$backup_file")"
            log_message "INFO" "Ubicación: $backup_file"
            
            # Enviar notificación de éxito
            send_notification "SUCCESS" "Backup completado en ${duration} segundos"
            
            exit 0
        else
            log_message "ERROR" "Falló la verificación de integridad del backup"
            send_notification "FAILURE" "Verificación de integridad falló"
            exit 1
        fi
    else
        log_message "ERROR" "Falló la creación del backup"
        send_notification "FAILURE" "Creación del backup falló"
        exit 1
    fi
}

# Función de ayuda
show_help() {
    cat << EOF
Uso: $0 [OPCIONES]

Script de backup automático para PostgreSQL - Sistema Qtrazer

OPCIONES:
    -h, --help          Mostrar esta ayuda
    -v, --verbose       Modo verbose
    -d, --dry-run       Simular ejecución sin realizar cambios
    -c, --cleanup       Solo limpiar backups antiguos
    -r, --retention N   Cambiar días de retención (por defecto: $RETENTION_DAYS)
    -o, --output DIR    Cambiar directorio de salida (por defecto: $BACKUP_DIR)

EJEMPLOS:
    $0                    # Ejecutar backup completo
    $0 --cleanup         # Solo limpiar backups antiguos
    $0 --retention 14    # Cambiar retención a 14 días
    $0 --output /tmp     # Cambiar directorio de salida

CONFIGURACIÓN:
    Base de datos: $DB_NAME
    Usuario: $DB_USER
    Directorio de backup: $BACKUP_DIR
    Días de retención: $RETENTION_DAYS
    Compresión: $([ $COMPRESSION_LEVEL -gt 0 ] && echo "Habilitada" || echo "Deshabilitada")

LOGS:
    Los logs se guardan en: $LOG_DIR/backup.log

EOF
}

# Procesar argumentos de línea de comandos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        -d|--dry-run)
            log_message "INFO" "MODO DRY-RUN: No se realizarán cambios reales"
            DRY_RUN=true
            shift
            ;;
        -c|--cleanup)
            log_message "INFO" "MODO LIMPIEZA: Solo se limpiarán backups antiguos"
            CLEANUP_ONLY=true
            shift
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            log_message "INFO" "Días de retención cambiados a: $RETENTION_DAYS"
            shift 2
            ;;
        -o|--output)
            BACKUP_DIR="$2"
            log_message "INFO" "Directorio de backup cambiado a: $BACKUP_DIR"
            shift 2
            ;;
        *)
            log_message "ERROR" "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Ejecutar función principal
if [ "$CLEANUP_ONLY" = true ]; then
    log_message "INFO" "Ejecutando solo limpieza de backups antiguos..."
    create_directories
    cleanup_old_backups
    log_message "INFO" "Limpieza completada"
else
    main
fi
