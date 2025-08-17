# Paso 6: Archivo main.py
   #Este es el módulo principal que integra todos los componentes del sistema.


# src/main.py

import os
import sys
import tkinter as tk

def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, funciona tanto para desarrollo como para el ejecutable"""
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Agrega la carpeta raíz del proyecto al PYTHONPATH
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ruta_raiz)

from src.controllers.main_controller import ControladorPrincipal
from src.views.main_view import VistaPrincipal
from src.views.splash_view import SplashView

def main():
    """Función principal que inicia la aplicación."""
    # Crear ventana principal
    ventana_principal = tk.Tk()
    ventana_principal.withdraw()  # Ocultar la ventana principal temporalmente
    
    # Crear ventana de splash
    splash_root = tk.Toplevel()
    
    # Ruta al archivo PNG usando resource_path
    splash_path = resource_path(os.path.join("assets", "splash.png"))
    
    # Mostrar splash screen
    splash = SplashView(splash_root, splash_path, duration=4000)
    
    # Esperar a que el splash se cierre
    splash_root.wait_window()
    
    # Mostrar la ventana principal
    ventana_principal.deiconify()
    
    # Crear controlador
    controlador = ControladorPrincipal()
    
    # Crear vista principal
    vista = VistaPrincipal(ventana_principal, controlador)
    
    # Iniciar bucle principal
    ventana_principal.mainloop()

if __name__ == "__main__":
    main()