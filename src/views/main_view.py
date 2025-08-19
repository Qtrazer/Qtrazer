"""Vista principal de la aplicación."""

import tkinter as tk
from tkinter import ttk
from src.config.settings import CONFIG_INTERFAZ
from PIL import Image, ImageTk
import os
import sys

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller"""
    try:
        # PyInstaller crea un temp folder y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class VistaPrincipal:
    def __init__(self, root, controlador):
        self.root = root
        self.controlador = controlador
        self.configurar_ventana()
        self.crear_interfaz()

    def configurar_ventana(self):
        """Configura la ventana principal."""
        self.root.title(CONFIG_INTERFAZ['titulo'])
        self.root.geometry(CONFIG_INTERFAZ['tamaño_ventana'])
        self.root.minsize(800, 600)

    def crear_interfaz(self):
        """Crea la interfaz principal."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cargar y mostrar el logo
        try:
            logo_path = get_resource_path('assets/logo_qtrazer.png')
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"No se encontró el logo en: {logo_path}")
            
            if hasattr(Image, 'Resampling'):
                imagen_logo = Image.open(logo_path).resize((239, 150), Image.Resampling.LANCZOS)
            else:
                imagen_logo = Image.open(logo_path).resize((239, 150), Image.ANTIALIAS)
            
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            logo_label = ttk.Label(main_frame, image=self.logo_img)
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Error al cargar el logo: {str(e)}")
            logo_label = ttk.Label(main_frame, text="[Logo no disponible]", font=("Helvetica", 14, "italic"))
            logo_label.pack(pady=(0, 20))

        # Mensaje de bienvenida
        welcome_label = ttk.Label(
            main_frame,
            text="Bienvenido al Sistema para consultar datos de Siniestros Viales en Bogotá",
            font=("Helvetica", 16),
            foreground="#34495e"
        )
        welcome_label.pack(pady=20)

        # Frame para los botones principales
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=50)

        # Estilo personalizado para los botones
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Qtrazer.TButton",
                        font=("Helvetica", 12),
                        background="#0d9330",
                        foreground="white",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#0d9330",
                        relief="flat")
        style.map("Qtrazer.TButton",
                  background=[('active', '#0b7a27'), ('!active', '#0d9330')],
                  foreground=[('active', 'white'), ('!active', 'white')],
                  bordercolor=[('active', '#0d9330'), ('!active', '#0d9330')])

        # Botón Actualizar Base de datos
        update_button = ttk.Button(
            button_frame,
            text="Actualizar Base de datos",
            command=self.mostrar_vista_actualizacion,
            style="Qtrazer.TButton"
        )
        update_button.pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

        # Botón Consultar Siniestros
        query_button = ttk.Button(
            button_frame,
            text="Consultar Siniestros",
            command=self.mostrar_vista_consulta,
            style="Qtrazer.TButton"
        )
        query_button.pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

        # Botón Configuración de Base de Datos
        config_button = ttk.Button(
            button_frame,
            text="Credenciales BD",
            command=self.mostrar_configuracion,
            style="Qtrazer.TButton"
        )
        config_button.pack(side=tk.LEFT, padx=20, ipadx=20, ipady=10)

        # Frame contenedor para el botón de finalizar sesión y el texto legal
        bottom_container = ttk.Frame(main_frame)
        bottom_container.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 10))

        # Estilo personalizado para el botón de finalizar sesión
        style.configure("Finalizar.TButton",
                        font=("Helvetica", 8),
                        background="#D5D515",
                        foreground="black",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="#D5D515",
                        relief="flat",
                        padding=3)
        style.map("Finalizar.TButton",
                  background=[('active', '#B8B800'), ('!active', '#D5D515')],
                  foreground=[('active', 'black'), ('!active', 'black')],
                  bordercolor=[('active', '#D5D515'), ('!active', '#D5D515')])

        # Botón Finalizar Sesión
        logout_button = ttk.Button(
            bottom_container,
            text="Finalizar Sesión",
            command=self.cerrar_sesion,
            style="Finalizar.TButton"
        )
        logout_button.pack(pady=(0, 10))

        # Texto de avisos legales
        legal_text = "Los datos consultados y presentados en este sistema provienen del repositorio oficial de datos abiertos de la Secretaría Distrital de Movilidad de Bogotá, disponible en datos.movilidadbogota.gov.co. Estos conjuntos de datos son de acceso público y están disponibles para su uso y reutilización sin restricciones legales, conforme a la Ley 1712 de 2014 sobre Transparencia y Acceso a la Información Pública Nacional. La Secretaría de Movilidad ha dispuesto esta información en formatos estándar e interoperables, permitiendo su aprovechamiento por parte de ciudadanos, entidades públicas y privadas, y la academia."

        legal_label = ttk.Label(
            bottom_container,
            text=legal_text,
            font=("Helvetica", 7),
            foreground="#666666",
            wraplength=700,
            justify=tk.CENTER
        )
        legal_label.pack(pady=(0, 5))

    def cerrar_sesion(self):
        """Cierra la sesión y termina el programa."""
        self.root.quit()
        self.root.destroy()

    def mostrar_vista_actualizacion(self):
        """Muestra la vista de actualización."""
        from src.views.update_view import VistaActualizacion
        ventana_actualizacion = tk.Toplevel(self.root)
        VistaActualizacion(ventana_actualizacion, self.root, self.controlador)

    def mostrar_vista_consulta(self):
        """Muestra la vista de consulta."""
        from src.views.query_view import VistaConsulta
        ventana_consulta = tk.Toplevel(self.root)
        VistaConsulta(ventana_consulta, self.root, self.controlador)
    
    def mostrar_configuracion(self):
        """Muestra la vista de configuración de base de datos."""
        from src.views.config_view import ConfigView
        ConfigView(self.root) 