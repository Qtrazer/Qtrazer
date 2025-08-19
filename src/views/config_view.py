"""Ventana de configuración de base de datos."""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

class ConfigView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Configuración conexión Base de Datos")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.center_window()
        
        # Configurar la ventana (no modal para mejor experiencia)
        self.transient(parent)
        
        # Variables para almacenar la configuración
        self.config_data = {}
        
        # Verificar si es ejecutable o desarrollo
        self.is_executable = getattr(sys, 'frozen', False)
        
        self.create_widgets()
        self.load_default_values()
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Título principal
        title_label = tk.Label(self, text="Configuración conexión Base de Datos", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Información del entorno
        env_text = "Entorno productivo" if self.is_executable else "Entorno de Desarrollo"
        env_label = tk.Label(self, text=f"Modo: {env_text}", 
                            font=("Arial", 10), fg="blue")
        env_label.pack(pady=5)
        
        # Información adicional sobre configuración
        # Verificar si hay configuración cargada automáticamente desde settings.py
        from src.config.settings import get_current_database_config
        current_config = get_current_database_config()
        
        if current_config and current_config.get('host'):
            config_info = "Configuración cargada automáticamente"
            config_color = "green"
        elif self.load_config_from_file():
            config_info = "Configuración guardada previamente"
            config_color = "blue"
        else:
            config_info = "Primera vez - Ingrese sus credenciales"
            config_color = "orange"
        
        config_label = tk.Label(self, text=config_info, 
                               font=("Arial", 9), fg=config_color)
        config_label.pack(pady=2)
        
        # Frame principal para los campos
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)
        
        # Campo Base de Datos
        ttk.Label(main_frame, text="Base de Datos:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.db_name = ttk.Entry(main_frame, width=30)
        self.db_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Campo Usuario
        ttk.Label(main_frame, text="Usuario:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.db_user = ttk.Entry(main_frame, width=30)
        self.db_user.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Campo Contraseña
        ttk.Label(main_frame, text="Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.db_password = ttk.Entry(main_frame, width=30, show="*")
        self.db_password.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Campo Host
        ttk.Label(main_frame, text="Host:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.db_host = ttk.Entry(main_frame, width=30)
        self.db_host.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Campo Puerto
        ttk.Label(main_frame, text="Puerto:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.db_port = ttk.Entry(main_frame, width=30)
        self.db_port.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Configurar el grid para que se expanda
        main_frame.columnconfigure(1, weight=1)
        
        # Frame para botones
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        
        # Botones
        ttk.Button(button_frame, text="Probar Conexión", command=self.test_connection).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Guardar", command=self.save_config).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel_config).pack(side="left", padx=10)
        
        # Configurar eventos
        self.protocol("WM_DELETE_WINDOW", self.cancel_config)
        
    def load_default_values(self):
        """Carga valores guardados previamente o deja los campos vacíos"""
        try:
            # Primero intentar usar la configuración global cargada automáticamente
            from src.config.settings import get_current_database_config
            current_config = get_current_database_config()
            
            if current_config and current_config.get('host'):
                # Usar configuración global cargada automáticamente
                self.db_name.insert(0, current_config.get('dbname', ''))
                self.db_user.insert(0, current_config.get('user', ''))
                self.db_password.insert(0, current_config.get('password', ''))
                self.db_host.insert(0, current_config.get('host', ''))
                self.db_port.insert(0, current_config.get('port', ''))
                print("Configuración cargada desde configuración global")
                return
            
            # Si no hay configuración global, intentar cargar desde archivo
            saved_config = self.load_config_from_file()
            if saved_config:
                # Insertar valores guardados previamente
                self.db_name.insert(0, saved_config.get('dbname', ''))
                self.db_user.insert(0, saved_config.get('user', ''))
                self.db_password.insert(0, saved_config.get('password', ''))
                self.db_host.insert(0, saved_config.get('host', ''))
                self.db_port.insert(0, saved_config.get('port', ''))
                print("Configuración cargada desde archivo guardado")
            else:
                print("No hay configuración guardada, campos vacíos")
        except Exception as e:
            print(f"Error al cargar configuración guardada: {str(e)}")
            # Los campos se dejan vacíos si hay error
    
    def load_config_from_file(self):
        """Carga la configuración desde el archivo JSON guardado"""
        try:
            import json
            import os
            
            # Determinar la ruta del archivo de configuración
            if getattr(sys, 'frozen', False):
                # Si es ejecutable (.exe), buscar en el directorio del usuario
                config_dir = os.path.expanduser("~\\AppData\\Local\\Qtrazer")
            else:
                # Si es desarrollo, buscar en el directorio del proyecto
                config_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            config_file = os.path.join(config_dir, 'qtrazer_config.json')
            
            # Verificar si existe el archivo de configuración
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"Configuración cargada desde: {config_file}")
                return config
            else:
                print(f"Archivo de configuración no encontrado: {config_file}")
                return None
                
        except Exception as e:
            print(f"Error al cargar archivo de configuración: {str(e)}")
            return None
    
    def save_config(self):
        """Guarda la configuración ingresada de forma persistente"""
        # Validar campos obligatorios
        if not self.db_name.get().strip():
            messagebox.showerror("Error", "El nombre de la base de datos es obligatorio")
            return
        
        if not self.db_user.get().strip():
            messagebox.showerror("Error", "El usuario es obligatorio")
            return
        
        if not self.db_host.get().strip():
            messagebox.showerror("Error", "El host es obligatorio")
            return
        
        # Recopilar configuración
        config = {
            'dbname': self.db_name.get().strip(),
            'user': self.db_user.get().strip(),
            'password': self.db_password.get(),
            'host': self.db_host.get().strip(),
            'port': self.db_port.get().strip() or '5432'
        }
        
        try:
            # Guardar configuración en memoria del sistema
            self.config_data = config
            
            # Guardar configuración de forma persistente en archivo JSON
            self.save_config_to_file(config)
            
            # Actualizar la configuración global en settings.py
            from src.config.settings import update_database_config
            update_database_config(config)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Configuración guardada exitosamente y será recordada en futuras sesiones")
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración:\n{str(e)}")
    
    def save_config_to_file(self, config):
        """Guarda la configuración en un archivo JSON de forma persistente"""
        try:
            import json
            import os
            
            # Determinar la ruta del archivo de configuración
            if getattr(sys, 'frozen', False):
                # Si es ejecutable (.exe), guardar en el directorio del usuario
                # Esto es más seguro y estándar en Windows
                config_dir = os.path.expanduser("~\\AppData\\Local\\Qtrazer")
                # Crear el directorio si no existe
                os.makedirs(config_dir, exist_ok=True)
            else:
                # Si es desarrollo, guardar en el directorio del proyecto
                config_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            config_file = os.path.join(config_dir, 'qtrazer_config.json')
            
            # Guardar configuración en archivo JSON
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            print(f"Configuración guardada en: {config_file}")
            
        except Exception as e:
            print(f"Error al guardar archivo de configuración: {str(e)}")
            # No fallar si no se puede guardar el archivo, solo la memoria
    
    def cancel_config(self):
        """Cancela la configuración y cierra la ventana"""
        self.destroy()
    
    def test_connection(self):
        """Prueba la conexión a la base de datos con la configuración actual"""
        # Validar campos obligatorios
        if not self.db_name.get().strip():
            messagebox.showerror("Error", "El nombre de la base de datos es obligatorio")
            return
        
        if not self.db_user.get().strip():
            messagebox.showerror("Error", "El usuario es obligatorio")
            return
        
        if not self.db_host.get().strip():
            messagebox.showerror("Error", "El host es obligatorio")
            return
        
        # Recopilar configuración temporal
        config = {
            'dbname': self.db_name.get().strip(),
            'user': self.db_user.get().strip(),
            'password': self.db_password.get(),
            'host': self.db_host.get().strip(),
            'port': self.db_port.get().strip() or '5432'
        }
        
        try:
            # Probar conexión
            import psycopg2
            conn = psycopg2.connect(
                dbname=config['dbname'],
                user=config['user'],
                password=config['password'],
                host=config['host'],
                port=config['port']
            )
            conn.close()
            
            messagebox.showinfo("Éxito", 
                f"Conexión exitosa a la base de datos:\n"
                f"Host: {config['host']}\n"
                f"Base de datos: {config['dbname']}\n"
                f"Usuario: {config['user']}")
                
        except Exception as e:
            messagebox.showerror("Error de Conexión", 
                f"No se pudo conectar a la base de datos:\n{str(e)}\n\n"
                f"Verifique:\n"
                f"• El host y puerto sean correctos\n"
                f"• El nombre de la base de datos exista\n"
                f"• El usuario y contraseña sean válidos\n"
                f"• El servidor esté activo")
    
    def get_config(self):
        """Retorna la configuración guardada"""
        return self.config_data
