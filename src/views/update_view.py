"""Vista para la actualización de datos de siniestros viales."""

import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.update_controller import ControladorActualizacion
from src.config.settings import CONFIG_INTERFAZ
import threading
import time

class VistaActualizacion:
    def __init__(self, root, ventana_principal, controlador_principal):
        self.root = root
        self.ventana_principal = ventana_principal
        self.controlador_principal = controlador_principal
        self.controlador = ControladorActualizacion()
        
        self.configurar_ventana()
        self.crear_interfaz()
        
        # Configurar el protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

    def configurar_ventana(self):
        """Configura la ventana de actualización."""
        self.root.title("Actualización de Datos - " + CONFIG_INTERFAZ['titulo'])
        self.root.geometry("800x600")
        self.root.minsize(700, 550)
        self.root.resizable(True, True)
        self.root.configure(bg="#E8E8E8")

    def crear_interfaz(self):
        """Crea la interfaz de actualización."""
        # Configurar estilos específicos para esta ventana
        style = ttk.Style()
        style.configure('Update.TFrame', background='#E8E8E8')
        style.configure('Update.TLabel', background='#E8E8E8')

        # Frame principal con peso para expandirse
        main_frame = ttk.Frame(self.root, style='Update.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Actualización Bases de Siniestros Viales",
            font=("Helvetica", 16, "bold"),
            foreground="#34495e",
            wraplength=700,
            style='Update.TLabel'
        )
        title_label.pack(pady=(0, 15))

        # Texto descriptivo con mayor ancho y mejor espaciado
        description_text = "En esta interfaz se realizará una consulta a los repositorios de datos abiertos de la Secretaría de Movilidad de Bogotá, accediendo a las tablas de accidentes, por vía, causa, tipo de vehículo y actor vial; los datos serán procesados y almacenados en la base de datos del proyecto Qtrazer para su posterior consulta."
        
        description_label = ttk.Label(
            main_frame,
            text=description_text,
            font=("Helvetica", 11),
            foreground="#2c3e50",
            wraplength=700,  # Aumentamos el ancho máximo del texto
            justify=tk.LEFT,
            style='Update.TLabel'
        )
        description_label.pack(pady=(0, 25), fill=tk.X)

        # Frame para el estado con expansión horizontal
        status_frame = ttk.Frame(main_frame, style='Update.TFrame')
        status_frame.pack(fill=tk.X, pady=10)

        # Etiqueta de estado
        self.status_label = ttk.Label(
            status_frame,
            text="Listo para actualizar",
            font=("Helvetica", 12),
            foreground="#34495e",
            style='Update.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)

        # Frame para la barra de progreso
        progress_frame = ttk.Frame(main_frame, style='Update.TFrame')
        progress_frame.pack(fill=tk.X, pady=10)

        # Configurar estilo para la barra de progreso
        style.configure("Qtrazer.Horizontal.TProgressbar",
                        troughcolor='#f0f0f0',
                        background='#0d9330',
                        thickness=20)

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="Qtrazer.Horizontal.TProgressbar",
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Etiqueta de porcentaje
        self.percent_label = ttk.Label(
            progress_frame,
            text="0%",
            font=("Helvetica", 10),
            foreground="#34495e",
            style='Update.TLabel'
        )
        self.percent_label.pack(side=tk.RIGHT, padx=5)

        # Frame para el log con fondo claro
        log_frame = ttk.Frame(main_frame, style='Update.TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Área de log con fondo claro
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            font=("Helvetica", 10),
            height=10,
            state=tk.DISABLED,
            bg='#E8E8E8',  # Color de fondo para el área de texto
            relief=tk.FLAT  # Sin borde
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para el log
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Frame para los botones
        button_frame = ttk.Frame(main_frame, style='Update.TFrame')
        button_frame.pack(fill=tk.X, pady=20)

        # Estilo para los botones
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

        # Botón Iniciar Actualización
        self.start_button = ttk.Button(
            button_frame,
            text="Actualizar todas las Tablas",
            command=self.iniciar_actualizacion,
            style="Qtrazer.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Botón Actualización Individual
        self.individual_button = ttk.Button(
            button_frame,
            text="Actualización Individual",
            command=self.mostrar_selector_tabla,
            style="Qtrazer.TButton"
        )
        self.individual_button.pack(side=tk.LEFT, padx=10)

        # Botón Cerrar
        self.close_button = ttk.Button(
            button_frame,
            text="Cerrar",
            command=self.cerrar_ventana,
            style="Qtrazer.TButton"
        )
        self.close_button.pack(side=tk.RIGHT, padx=10)

    def agregar_log(self, mensaje):
        """Agrega un mensaje al área de log con formato."""
        self.log_text.config(state=tk.NORMAL)
        
        # Aplicar formato según el tipo de mensaje
        if "Error: list index out of range" in mensaje:
            self.log_text.insert(tk.END, "\n[ERROR] No fue posible establecer conexión con la base de datos\nDetalle: Error al obtener el ObjectID más reciente\n", "error")
        elif "Error al actualizar la tabla" in mensaje:
            tabla = mensaje.split("'")[1]
            self.log_text.insert(tk.END, f"\n[ERROR] No fue posible actualizar la tabla '{tabla}'\n", "error")
        elif "Iniciando actualización" in mensaje:
            self.log_text.insert(tk.END, f"\n[INICIO] {mensaje}\n", "inicio")
        elif "[PROGRESO]" in mensaje:
            # Manejar mensajes de progreso de manera especial para evitar saturación
            if not hasattr(self, 'linea_progreso'):
                # Primera vez que se muestra progreso, agregar nueva línea
                self.log_text.insert(tk.END, f"\n{mensaje}\n", "progreso")
                self.linea_progreso = True
            else:
                # Actualizar la última línea de progreso en lugar de agregar una nueva
                # Buscar la última línea que contiene [PROGRESO]
                contenido = self.log_text.get(1.0, tk.END)
                lineas = contenido.split('\n')
                
                # Encontrar la última línea con [PROGRESO]
                ultima_linea_progreso = -1
                for i in range(len(lineas) - 1, -1, -1):
                    if "[PROGRESO]" in lineas[i]:
                        ultima_linea_progreso = i
                        break
                
                if ultima_linea_progreso >= 0:
                    # Reemplazar la última línea de progreso
                    inicio_linea = f"{ultima_linea_progreso + 1}.0"
                    fin_linea = f"{ultima_linea_progreso + 1}.end"
                    self.log_text.delete(inicio_linea, fin_linea)
                    self.log_text.insert(inicio_linea, mensaje, "progreso")
                else:
                    # Si no se encuentra línea de progreso, agregar nueva
                    self.log_text.insert(tk.END, f"\n{mensaje}\n", "progreso")
        elif "Total de registros" in mensaje:
            self.log_text.insert(tk.END, f"\n[INFO] {mensaje}\n", "info")
        elif "ObjectID más reciente" in mensaje:
            objectid = mensaje.split(":")[1].strip()
            self.log_text.insert(tk.END, f"[INFO] ObjectID más reciente en BD: {objectid}\n", "info")
        elif "Progreso:" in mensaje:
            partes = mensaje.split("(")
            if len(partes) > 1:
                registros = partes[0].split(":")[1].strip()
                porcentaje = partes[1].replace(")", "").strip()
                self.log_text.insert(tk.END, f"[PROGRESO] {registros} ({porcentaje})\n", "progreso")
        elif "Error" in mensaje:
            self.log_text.insert(tk.END, f"\n{mensaje}\n", "error")
        elif "Actualización completada" in mensaje:
            self.log_text.insert(tk.END, f"\n[ÉXITO] Actualización completada\n", "exito")
        else:
            if "Insertando registros" in mensaje and not hasattr(self, 'mostrado_insercion'):
                self.log_text.insert(tk.END, f"\n[INFO] Iniciando inserción de registros\n", "info")
                self.mostrado_insercion = True
        
        # Configurar tags para el formato
        self.log_text.tag_configure("inicio", foreground="blue", font=("Helvetica", 10, "bold"))
        self.log_text.tag_configure("info", foreground="#34495e", font=("Helvetica", 10))
        self.log_text.tag_configure("progreso", foreground="#0d9330", font=("Helvetica", 10))
        self.log_text.tag_configure("error", foreground="red", font=("Helvetica", 10, "bold"))
        self.log_text.tag_configure("exito", foreground="#0d9330", font=("Helvetica", 10, "bold"))
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def iniciar_actualizacion(self):
        """Inicia el proceso de actualización."""
        if self.controlador.esta_actualizando():
            messagebox.showwarning(
                "Actualización en Progreso",
                "Ya hay una actualización en curso. Por favor espere."
            )
            return

        # Deshabilitar el botón de actualización
        self.start_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.DISABLED)
        
        # Limpiar el log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Resetear los flags de inserción y progreso
        if hasattr(self, 'mostrado_insercion'):
            delattr(self, 'mostrado_insercion')
        if hasattr(self, 'linea_progreso'):
            delattr(self, 'linea_progreso')
        
        def actualizar_progreso(mensaje, porcentaje):
            self.status_label.config(text=mensaje)
            self.progress_bar['value'] = porcentaje
            self.percent_label['text'] = f"{porcentaje:.1f}%"
            self.agregar_log(mensaje)
            self.root.update_idletasks()
            
            # Verificar si se completó todo el proceso
            if "Actualización completada exitosamente" in mensaje:
                self.finalizar_actualizacion()
        
        def ejecutar_actualizacion():
            try:
                resultado = self.controlador.iniciar_actualizacion(actualizar_progreso)
                if resultado:
                    self.progress_bar['value'] = 100
                    self.percent_label['text'] = "100%"
                else:
                    actualizar_progreso("Error en la actualización", 0)
            except Exception as e:
                actualizar_progreso(f"Error: {str(e)}", 0)
            finally:
                self.root.after(0, self.finalizar_actualizacion)
        
        # Iniciar actualización en un hilo separado
        threading.Thread(target=ejecutar_actualizacion, daemon=True).start()

    def finalizar_actualizacion(self):
        """Finaliza el proceso de actualización."""
        # Restaurar el estado de los botones
        self.start_button.config(state=tk.NORMAL)
        self.individual_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.NORMAL)
        
        # Limpiar la barra de progreso
        self.progress_bar.config(value=0)
        self.percent_label.config(text="0%")
        
        # Actualizar el estado para indicar que la actualización ha terminado
        self.status_label.config(text="Actualización finalizada - Ventana conservada para revisar historial")

    def mostrar_selector_tabla(self):
        """Muestra un diálogo para seleccionar una tabla específica para actualizar."""
        if self.controlador.esta_actualizando():
            messagebox.showwarning(
                "Actualización en Progreso",
                "Ya hay una actualización en curso. Por favor espere."
            )
            return

        # Crear ventana de selección
        selector_window = tk.Toplevel(self.root)
        selector_window.title("Seleccionar Tabla para Actualización Individual")
        selector_window.geometry("400x300")
        selector_window.resizable(False, False)
        selector_window.configure(bg="#E8E8E8")
        
        # Centrar la ventana
        selector_window.transient(self.root)
        selector_window.grab_set()

        # Frame principal
        main_frame = ttk.Frame(selector_window, style='Update.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Seleccione la tabla a actualizar:",
            font=("Helvetica", 14, "bold"),
            foreground="#34495e",
            style='Update.TLabel'
        )
        title_label.pack(pady=(0, 20))

        # Lista de tablas disponibles
        tablas_disponibles = [
            ("Accidente", "Tabla principal de accidentes"),
            ("Accidente_via", "Tabla de información vial"),
            ("Causa", "Tabla de causas de accidentes"),
            ("AccidenteVehiculo", "Tabla de vehículos involucrados"),
            ("ActorVial", "Tabla de actores viales")
        ]

        # Variable para almacenar la selección
        self.tabla_seleccionada = tk.StringVar()
        self.tabla_seleccionada.set(tablas_disponibles[0][0])

        # Crear radio buttons para cada tabla
        for i, (tabla, descripcion) in enumerate(tablas_disponibles):
            radio_frame = ttk.Frame(main_frame, style='Update.TFrame')
            radio_frame.pack(fill=tk.X, pady=5)

            radio_button = ttk.Radiobutton(
                radio_frame,
                text=f"{tabla}",
                variable=self.tabla_seleccionada,
                value=tabla,
                style='Update.TRadiobutton'
            )
            radio_button.pack(side=tk.LEFT)

            desc_label = ttk.Label(
                radio_frame,
                text=f"- {descripcion}",
                font=("Helvetica", 10),
                foreground="#666666",
                style='Update.TLabel'
            )
            desc_label.pack(side=tk.LEFT, padx=(10, 0))

        # Frame para botones
        button_frame = ttk.Frame(main_frame, style='Update.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))

        # Botón Actualizar
        actualizar_button = ttk.Button(
            button_frame,
            text="Actualizar Tabla Seleccionada",
            command=lambda: self.iniciar_actualizacion_individual(selector_window),
            style="Qtrazer.TButton"
        )
        actualizar_button.pack(side=tk.LEFT, padx=(0, 10))

        # Botón Cancelar
        cancelar_button = ttk.Button(
            button_frame,
            text="Cancelar",
            command=selector_window.destroy,
            style="Qtrazer.TButton"
        )
        cancelar_button.pack(side=tk.LEFT)

    def iniciar_actualizacion_individual(self, selector_window):
        """Inicia la actualización de la tabla seleccionada individualmente."""
        tabla = self.tabla_seleccionada.get()
        selector_window.destroy()
        
        # Deshabilitar botones durante la actualización
        self.start_button.config(state=tk.DISABLED)
        self.individual_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.DISABLED)
        
        # Limpiar el log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Resetear los flags de inserción y progreso
        if hasattr(self, 'mostrado_insercion'):
            delattr(self, 'mostrado_insercion')
        if hasattr(self, 'linea_progreso'):
            delattr(self, 'linea_progreso')
        
        def actualizar_progreso(mensaje, porcentaje):
            self.status_label.config(text=mensaje)
            self.progress_bar['value'] = porcentaje
            self.percent_label['text'] = f"{porcentaje:.1f}%"
            self.agregar_log(mensaje)
            self.root.update_idletasks()
            
            # Verificar si se completó todo el proceso
            if "Actualización completada exitosamente" in mensaje:
                self.finalizar_actualizacion()
        
        def ejecutar_actualizacion_individual():
            try:
                resultado = self.controlador.iniciar_actualizacion_individual(tabla, actualizar_progreso)
                if resultado:
                    self.progress_bar['value'] = 100
                    self.percent_label['text'] = "100%"
                else:
                    actualizar_progreso("Error en la actualización", 0)
            except Exception as e:
                actualizar_progreso(f"Error: {str(e)}", 0)
            finally:
                self.root.after(0, self.finalizar_actualizacion)
        
        # Iniciar actualización en un hilo separado
        threading.Thread(target=ejecutar_actualizacion_individual, daemon=True).start()

    def cerrar_ventana(self):
        """Cierra la ventana de actualización."""
        if self.controlador.esta_actualizando():
            # Preguntar al usuario si quiere cancelar la actualización
            respuesta = messagebox.askyesno(
                "Actualización en Progreso",
                "Hay una actualización en curso. ¿Desea cancelar la actualización y cerrar la ventana?"
            )
            if respuesta:
                # Cancelar la actualización pero mantener la ventana abierta
                self.controlador.cancelar_actualizacion()
                self.agregar_log("Actualización cancelada por el usuario")
                self.agregar_log("La ventana permanecerá abierta para mostrar el historial de la actualización")
                self.finalizar_actualizacion()
                # NO cerrar la ventana para conservar el historial
                # self.root.destroy()  # Comentado para mantener la ventana abierta
            # Si el usuario dice "No", no hacer nada (mantener la ventana abierta)
        else:
            self.root.destroy() 