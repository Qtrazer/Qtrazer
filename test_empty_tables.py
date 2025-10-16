#!/usr/bin/env python3
"""
Script de prueba para verificar el comportamiento con tablas vacías
Ejecutar: python test_empty_tables.py
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_empty_tables_behavior():
    """Prueba el comportamiento del sistema con tablas vacías"""
    print("=== PRUEBA DE COMPORTAMIENTO CON TABLAS VACÍAS ===\n")
    
    try:
        from src.models.update_model import ModeloActualizacion
        from src.config.settings import get_database_params
        
        # Verificar configuración
        config = get_database_params()
        if config is None:
            print("❌ No hay configuración de base de datos")
            return False
        
        print(f"📋 Configuración de BD:")
        print(f"   - Base de datos: {config['dbname']}")
        print(f"   - Host: {config['host']}")
        print(f"   - Usuario: {config['user']}")
        print()
        
        # Crear instancia del modelo
        modelo = ModeloActualizacion()
        
        # Probar con cada tabla
        tablas = ['Accidente', 'ActorVial', 'Causa', 'AccidenteVehiculo', 'Accidente_via']
        
        for tabla in tablas:
            print(f"🔍 Probando tabla: {tabla}")
            
            try:
                # Obtener ObjectID más reciente
                latest_objectid = modelo.get_latest_objectid(tabla)
                
                if latest_objectid == 0:
                    print(f"   ✅ Tabla vacía detectada correctamente - ObjectID = 0")
                    print(f"   📝 El sistema obtendrá todos los datos desde el inicio")
                elif latest_objectid is None:
                    print(f"   ❌ Error al obtener ObjectID")
                else:
                    print(f"   📊 ObjectID más reciente: {latest_objectid}")
                    print(f"   📝 El sistema obtendrá solo registros nuevos")
                
            except Exception as e:
                print(f"   ❌ Error al probar tabla {tabla}: {str(e)}")
            
            print()
        
        print("✅ Prueba completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_empty_tables_behavior()
    sys.exit(0 if success else 1)
