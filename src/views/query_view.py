"""Vista para consulta de siniestros."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from src.config.settings import CONFIG_INTERFAZ
import threading
import time
import pandas as pd
from datetime import datetime
import os
from PIL import Image, ImageTk

class VistaConsulta:
    def __init__(self, root, ventana_principal, controlador):
        # Inicializar atributos básicos
        self.root = root
        self.ventana_principal = ventana_principal
        self.controlador = controlador
        
        # Inicializar atributos de estado
        self.consulta_en_progreso = False
        self.resultados_completos = None
        self.filtros_activos = False
        
        # Variables para controlar el ordenamiento
        self.columna_ordenamiento = None
        self.orden_descendente = True  # True = descendente, False = ascendente
        
        # Listas predefinidas para los filtros
        self.lista_vehiculos = [
            "AMBULACIA", "AUTOMOVIL", "BICICLETA", "BICITAXI", "BUS",
            "BUS ALIMENTADOR", "BUS ARTICULADO", "BUSETA", "CAMION, FURGON",
            "CAMIONETA", "CAMPERO", "CUATRIMOTO", "M. AGRICOLA", "M. INDUSTRIAL",
            "METRO", "MICROBUS", "MOTOCARRO", "MOTOCICLETA", "MOTOCICLO",
            "MOTOTRICICLO", "NO IDENTIFICADO", "OTRO", "REMOLQUE", "SEMI-REMOLQUE",
            "TRACCION ANIMAL", "TRACTOCAMION", "TREN", "VOLQUETA"
        ]
        
        self.lista_estados = ["HERIDO", "ILESO", "MUERTO"]
        self.lista_causantes = ["CONDUCTOR", "PASAJERO", "PEATON", "VEHICULO", "VIA"]
        
        # Configurar la interfaz
        self.configurar_ventana()
        self.crear_interfaz()

    def configurar_ventana(self):
        """Configura la ventana de consulta."""
        self.root.title("Consulta de Siniestros")
        self.root.geometry("1200x800")
        # Configurar el tamaño mínimo de la ventana
        self.root.minsize(800, 600)

    def crear_interfaz(self):
        """Crea la interfaz de consulta."""
        # Frame contenedor principal
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        # Frame principal con scrollbar
        main_canvas = tk.Canvas(container)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configurar el canvas
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Frame principal dentro del canvas
        main_frame = ttk.Frame(main_canvas, padding="10")
        
        # Crear la ventana en el canvas
        window_id = main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=self.root.winfo_width())

        # Función para actualizar el scroll y el ancho
        def update_scroll_region(event):
            # Actualizar el ancho del frame
            main_canvas.itemconfig(window_id, width=event.width)
            # Actualizar la región de scroll
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Vincular el evento de configuración
        main_canvas.bind('<Configure>', update_scroll_region)

        # Permitir scroll con la rueda del mouse
        def _on_mousewheel(event):
            # Invertir la dirección del scroll
            main_canvas.yview_scroll(int(event.delta/120), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Frame para el logo en la esquina superior izquierda
        logo_frame = ttk.Frame(self.root)
        logo_frame.pack(anchor="nw")

        # Cargar y mostrar el logo reducido
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'logo_qtrazer.png')
        logo_path = os.path.abspath(logo_path)
        try:
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"No se encontró el logo en: {logo_path}")
            if hasattr(Image, 'Resampling'):
                imagen_logo = Image.open(logo_path).resize((90, 60), Image.Resampling.LANCZOS)
            else:
                imagen_logo = Image.open(logo_path).resize((90, 60), Image.ANTIALIAS)
            self.logo_img = ImageTk.PhotoImage(imagen_logo)
            logo_label = ttk.Label(logo_frame, image=self.logo_img)
            logo_label.pack(anchor="nw")
        except Exception as e:
            logo_label = ttk.Label(logo_frame, text="[Logo no disponible]", font=("Helvetica", 10, "italic"))
            logo_label.pack(anchor="nw")

        # Título
        ttk.Label(
            main_frame, 
            text="Consulta de Siniestros", 
            font=("Helvetica", 16)
        ).pack(pady=10)

        # Mensaje descriptivo
        ttk.Label(
            main_frame,
            text="A través de la siguiente vista podrá consultar los registros de siniestros viales en Bogotá, por favor seleccione un rango de fechas",
            font=("Helvetica", 12),
            wraplength=600
        ).pack(pady=20)

        # Frame para fechas
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(pady=10)

        # Fecha inicial
        ttk.Label(date_frame, text="Fecha Inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_inicio = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.fecha_inicio.grid(row=0, column=1, padx=5, pady=5)

        # Fecha final
        ttk.Label(date_frame, text="Fecha Final:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_fin = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.fecha_fin.grid(row=0, column=3, padx=5, pady=5)

        # Frame para botones de consulta
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Botón de consulta
        self.boton_consulta = ttk.Button(
            button_frame,
            text="Consultar",
            command=self.iniciar_consulta
        )
        self.boton_consulta.pack(side=tk.LEFT, padx=5)

        # Botón de cancelar
        self.boton_cancelar = ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancelar_consulta,
            state='disabled'
        )
        self.boton_cancelar.pack(side=tk.LEFT, padx=5)

        # Botón de filtros avanzados
        self.boton_filtros = ttk.Button(
            button_frame,
            text="Filtros Avanzados ▼",
            command=self.toggle_filtros
        )
        self.boton_filtros.pack(side=tk.LEFT, padx=5)

        # Frame para filtros avanzados (inicialmente oculto)
        self.frame_filtros = ttk.LabelFrame(main_frame, text="Filtros Avanzados", padding="10")
        self.frame_filtros.pack(fill=tk.X, pady=10)
        self.frame_filtros.pack_forget()  # Ocultar inicialmente

        # Frame para los filtros
        filtros_frame = ttk.Frame(self.frame_filtros)
        filtros_frame.pack(fill=tk.X, pady=5)

        # Filtro de Localidad
        ttk.Label(filtros_frame, text="Localidad:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_localidad = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_localidad.grid(row=0, column=1, padx=5, pady=5)

        # Filtro de Vehículo
        ttk.Label(filtros_frame, text="Vehículo:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_vehiculo = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_vehiculo['values'] = [''] + self.lista_vehiculos
        self.combo_vehiculo.grid(row=0, column=3, padx=5, pady=5)

        # Filtro de Estado Actor vial
        ttk.Label(filtros_frame, text="Estado Actor vial:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_estado = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_estado['values'] = [''] + self.lista_estados
        self.combo_estado.grid(row=1, column=1, padx=5, pady=5)

        # Filtro de Causante
        ttk.Label(filtros_frame, text="Causante:").grid(row=1, column=2, padx=5, pady=5)
        self.combo_causante = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_causante['values'] = [''] + self.lista_causantes
        self.combo_causante.grid(row=1, column=3, padx=5, pady=5)

        # Filtro de ID
        ttk.Label(filtros_frame, text="ID:").grid(row=2, column=0, padx=5, pady=5)
        self.combo_id = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_id.grid(row=2, column=1, padx=5, pady=5)

        # Filtro de Formulario
        ttk.Label(filtros_frame, text="Formulario:").grid(row=2, column=2, padx=5, pady=5)
        self.combo_formulario = ttk.Combobox(filtros_frame, state="readonly", width=30)
        self.combo_formulario.grid(row=2, column=3, padx=5, pady=5)

        # Filtro de Fecha - Rango
        ttk.Label(filtros_frame, text="Fecha Inicial:").grid(row=3, column=0, padx=5, pady=5)
        self.fecha_filtro_inicio = DateEntry(
            filtros_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.fecha_filtro_inicio.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(filtros_frame, text="Fecha Final:").grid(row=3, column=2, padx=5, pady=5)
        self.fecha_filtro_fin = DateEntry(
            filtros_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy'
        )
        self.fecha_filtro_fin.grid(row=3, column=3, padx=5, pady=5)

        # Filtro de Hora - Rango
        ttk.Label(filtros_frame, text="Hora Inicial:").grid(row=4, column=0, padx=5, pady=5)
        self.hora_filtro_inicio = ttk.Combobox(filtros_frame, state="readonly", width=15)
        self.hora_filtro_inicio.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(filtros_frame, text="Hora Final:").grid(row=4, column=2, padx=5, pady=5)
        self.hora_filtro_fin = ttk.Combobox(filtros_frame, state="readonly", width=15)
        self.hora_filtro_fin.grid(row=4, column=3, padx=5, pady=5)

        # Frame para botones de filtros
        filtros_button_frame = ttk.Frame(self.frame_filtros)
        filtros_button_frame.pack(pady=5)

        # Botón para aplicar filtros
        self.boton_aplicar_filtros = ttk.Button(
            filtros_button_frame,
            text="Aplicar Filtros",
            command=self.aplicar_filtros
        )
        self.boton_aplicar_filtros.pack(side=tk.LEFT, padx=5)

        # Botón para limpiar filtros
        self.boton_limpiar_filtros = ttk.Button(
            filtros_button_frame,
            text="Limpiar Filtros",
            command=self.limpiar_filtros
        )
        self.boton_limpiar_filtros.pack(side=tk.LEFT, padx=5)

        # Barra de progreso
        self.barra_progreso = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.barra_progreso.pack(pady=10)

        # Etiqueta de estado
        self.etiqueta_estado = ttk.Label(
            main_frame,
            text="Listo para consultar",
            font=("Helvetica", 10)
        )
        self.etiqueta_estado.pack(pady=5)

        # Frame para la tabla de resultados
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear tabla con las nuevas columnas
        columnas = (
            "ID", "Formulario", "Fecha", "Hora", "Localidad",
            "Clases Vehículos", "Placas", "Condiciones Actores",
            "Fallecidos", "Heridos", "Ilesos", "Estados",
            "Géneros", "Edades", "Causante", "Causa", 
            "Terreno Vía", "Estado Vía"
        )

        self.tree = ttk.Treeview(table_frame, columns=columnas, show="headings")

        # Configurar columnas con funcionalidad de ordenamiento
        for col in columnas:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c))
            self.tree.column(col, width=100, minwidth=50)

        # Ajustar anchos específicos para algunas columnas
        self.tree.column("ID", width=50)
        self.tree.column("Formulario", width=100)
        self.tree.column("Fecha", width=100)
        self.tree.column("Hora", width=80)
        self.tree.column("Localidad", width=120)
        self.tree.column("Clases Vehículos", width=150)
        self.tree.column("Placas", width=120)
        self.tree.column("Condiciones Actores", width=150)
        self.tree.column("Fallecidos", width=80)
        self.tree.column("Heridos", width=80)
        self.tree.column("Ilesos", width=80)
        self.tree.column("Estados", width=120)
        self.tree.column("Géneros", width=100)
        self.tree.column("Edades", width=100)
        self.tree.column("Causante", width=120)
        self.tree.column("Causa", width=150)
        self.tree.column("Terreno Vía", width=120)
        self.tree.column("Estado Vía", width=120)

        # Agregar scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Configurar el grid para que la tabla se expanda
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Frame para botones de navegación
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(pady=20)

        # Botón para exportar a Excel
        self.boton_exportar = ttk.Button(
            nav_frame,
            text="Exportar a Excel",
            command=self.exportar_a_excel
        )
        self.boton_exportar.pack(side=tk.LEFT, padx=10)

        # Botón para volver al inicio
        ttk.Button(
            nav_frame,
            text="Volver al Inicio",
            command=self.volver_inicio
        ).pack(side=tk.LEFT, padx=10)

    def toggle_filtros(self):
        """Alterna la visibilidad del panel de filtros."""
        if self.frame_filtros.winfo_ismapped():
            self.frame_filtros.pack_forget()
            self.boton_filtros.config(text="Filtros Avanzados ▼")
            # Ajustar el tamaño del canvas después de ocultar los filtros
            self.root.after(100, self.ajustar_tamano_canvas)
        else:
            self.frame_filtros.pack(fill=tk.X, pady=10)
            self.boton_filtros.config(text="Filtros Avanzados ▲")
            # Actualizar los valores de los combobox si hay resultados
            if self.resultados_completos:
                self.actualizar_valores_filtros()
            # Ajustar el tamaño del canvas después de mostrar los filtros
            self.root.after(100, self.ajustar_tamano_canvas)

    def ajustar_tamano_canvas(self):
        """Ajusta el tamaño del canvas y actualiza la región de scroll."""
        try:
            # Obtener el canvas
            canvas = self.root.winfo_children()[0].winfo_children()[0]
            # Actualizar la región de scroll
            canvas.configure(scrollregion=canvas.bbox("all"))
        except Exception as e:
            print(f"Error al ajustar el tamaño del canvas: {str(e)}")

    def actualizar_valores_filtros(self):
        """Actualiza los valores disponibles en los combobox de filtros."""
        if not self.resultados_completos:
            return

        try:
            # Obtener valores únicos para cada filtro
            localidades = sorted(set(str(resultado[4]).strip() for resultado in self.resultados_completos if resultado[4]))
            ids = sorted(set(str(resultado[0]).strip() for resultado in self.resultados_completos if resultado[0]))
            formularios = sorted(set(str(resultado[1]).strip() for resultado in self.resultados_completos if resultado[1]))
            horas = sorted(set(str(resultado[3]).strip() for resultado in self.resultados_completos if resultado[3]))
            
            # Actualizar comboboxes
            self.combo_localidad['values'] = [''] + localidades
            self.combo_id['values'] = [''] + ids
            self.combo_formulario['values'] = [''] + formularios
            self.hora_filtro_inicio['values'] = [''] + horas
            self.hora_filtro_fin['values'] = [''] + horas
            
            # Limpiar selecciones actuales
            self.combo_localidad.set('')
            self.combo_vehiculo.set('')
            self.combo_estado.set('')
            self.combo_causante.set('')
            self.combo_id.set('')
            self.combo_formulario.set('')
            self.fecha_filtro_inicio.set_date('01/01/2020')  # Fecha por defecto
            self.fecha_filtro_fin.set_date('31/12/2030')     # Fecha por defecto
            self.hora_filtro_inicio.set('')
            self.hora_filtro_fin.set('')

        except Exception as e:
            print(f"Error al actualizar filtros: {str(e)}")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados a los resultados."""
        if not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay resultados para filtrar.")
            return

        try:
            # Obtener valores seleccionados
            localidad = self.combo_localidad.get()
            vehiculo = self.combo_vehiculo.get()
            estado = self.combo_estado.get()
            causante = self.combo_causante.get()
            id_filtro = self.combo_id.get()
            formulario = self.combo_formulario.get()
            fecha_inicio = self.fecha_filtro_inicio.get_date()
            fecha_fin = self.fecha_filtro_fin.get_date()
            hora_inicio = self.hora_filtro_inicio.get()
            hora_fin = self.hora_filtro_fin.get()

            # Verificar si hay algún filtro seleccionado
            # Para fechas, verificar si ambas están seleccionadas y son diferentes a los valores por defecto
            fecha_filtro_activo = False
            if fecha_inicio and fecha_fin:
                # Verificar si las fechas son diferentes a los valores por defecto
                fecha_inicio_default = fecha_inicio.strftime('%d/%m/%Y') == '01/01/2020'
                fecha_fin_default = fecha_fin.strftime('%d/%m/%Y') == '31/12/2030'
                fecha_filtro_activo = not (fecha_inicio_default and fecha_fin_default)
            
            if not any([localidad, vehiculo, estado, causante, id_filtro, formulario, hora_inicio, hora_fin, fecha_filtro_activo]):
                messagebox.showinfo("Información", "Por favor seleccione al menos un filtro.")
                return

            # Filtrar resultados de manera progresiva
            resultados_filtrados = self.resultados_completos.copy()

            # PASO 1: Aplicar filtro de rango de fecha PRIMERO (si está activo)
            if fecha_filtro_activo:
                from datetime import datetime
                try:
                    # Convertir fechas a objetos datetime para comparación
                    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
                    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
                    
                    resultados_filtrados = [r for r in resultados_filtrados 
                                          if r[2] and fecha_inicio_str <= str(r[2]).strip() <= fecha_fin_str]
                    
                    # Actualizar opciones de hora basadas en los datos filtrados por fecha
                    self._actualizar_opciones_hora(resultados_filtrados)
                    
                except Exception as e:
                    print(f"Error al filtrar por fecha: {str(e)}")

            # PASO 2: Aplicar filtro de rango de hora (si está activo)
            if hora_inicio and hora_fin:
                try:
                    # Convertir horas a formato comparable
                    def hora_a_minutos(hora_str):
                        if not hora_str:
                            return 0
                        try:
                            # Asumir formato HH:MM o HH:MM:SS
                            partes = str(hora_str).split(':')
                            return int(partes[0]) * 60 + int(partes[1])
                        except:
                            return 0
                    
                    hora_inicio_min = hora_a_minutos(hora_inicio)
                    hora_fin_min = hora_a_minutos(hora_fin)
                    
                    resultados_filtrados = [r for r in resultados_filtrados 
                                          if r[3] and hora_inicio_min <= hora_a_minutos(r[3]) <= hora_fin_min]
                    
                except Exception as e:
                    print(f"Error al filtrar por hora: {str(e)}")

            # PASO 3: Aplicar filtros de otros campos basados en los datos ya filtrados
            if localidad:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[4]).strip() == localidad.strip()]

            if vehiculo:
                resultados_filtrados = [r for r in resultados_filtrados if vehiculo in str(r[5]).split(', ')]

            if estado:
                resultados_filtrados = [r for r in resultados_filtrados if estado in str(r[11]).split(', ')]

            if causante:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[15]).strip() == causante.strip()]

            if id_filtro:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[0]).strip() == id_filtro.strip()]

            if formulario:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[1]).strip() == formulario.strip()]

            # Actualizar opciones de todos los campos basadas en los datos filtrados
            self._actualizar_opciones_filtros(resultados_filtrados)

            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Aplicar ordenamiento si hay uno activo
            if self.columna_ordenamiento:
                resultados_filtrados = self._aplicar_ordenamiento(resultados_filtrados, self.columna_ordenamiento, self.orden_descendente)
            
            # Mostrar resultados filtrados
            for resultado in resultados_filtrados:
                # Convertir None a cadena vacía
                valores = ['' if valor is None else str(valor) for valor in resultado]
                self.tree.insert("", tk.END, values=valores)

            self.filtros_activos = True
            self.etiqueta_estado.config(text=f"Mostrando {len(resultados_filtrados)} registros filtrados")

        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")

    def limpiar_filtros(self):
        """Limpia los filtros y muestra todos los resultados."""
        if not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar.")
            return

        try:
            # Limpiar selecciones en los comboboxes
            self.combo_localidad.set('')
            self.combo_vehiculo.set('')
            self.combo_estado.set('')
            self.combo_causante.set('')
            self.combo_id.set('')
            self.combo_formulario.set('')
            self.fecha_filtro_inicio.set_date('01/01/2020')
            self.fecha_filtro_fin.set_date('31/12/2030')
            self.hora_filtro_inicio.set('')
            self.hora_filtro_fin.set('')

            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Aplicar ordenamiento si hay uno activo
            resultados_a_mostrar = self.resultados_completos
            if self.columna_ordenamiento:
                resultados_a_mostrar = self._aplicar_ordenamiento(resultados_a_mostrar, self.columna_ordenamiento, self.orden_descendente)
            
            # Mostrar todos los resultados
            for resultado in resultados_a_mostrar:
                # Convertir None a cadena vacía
                valores = ['' if valor is None else str(valor) for valor in resultado]
                self.tree.insert("", tk.END, values=valores)

            self.filtros_activos = False
            self.etiqueta_estado.config(text=f"Mostrando {len(resultados_a_mostrar)} registros")

        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar filtros: {str(e)}")

    def iniciar_consulta(self):
        """Inicia el proceso de consulta en un hilo separado."""
        if self.consulta_en_progreso:
            messagebox.showwarning("Advertencia", "Ya hay una consulta en progreso.")
            return

        # Limpiar tabla y filtros
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.combo_localidad.set('')
        self.combo_vehiculo.set('')
        self.combo_estado.set('')
        self.combo_causante.set('')
        self.combo_id.set('')
        self.combo_formulario.set('')
        self.fecha_filtro_inicio.set_date('01/01/2020')
        self.fecha_filtro_fin.set_date('31/12/2030')
        self.hora_filtro_inicio.set('')
        self.hora_filtro_fin.set('')

        # Obtener fechas
        fecha_inicio = self.fecha_inicio.get_date()
        fecha_fin = self.fecha_fin.get_date()

        # Configurar estado de la interfaz
        self.consulta_en_progreso = True
        self.boton_consulta.config(state='disabled')
        self.boton_cancelar.config(state='normal')
        self.barra_progreso.start()
        self.etiqueta_estado.config(text="Consultando datos...")

        # Iniciar consulta
        cola_resultados = self.controlador.consultar_siniestros(fecha_inicio, fecha_fin)

        # Iniciar hilo para verificar resultados
        threading.Thread(target=self.verificar_resultados, args=(cola_resultados,), daemon=True).start()

    def verificar_resultados(self, cola_resultados):
        """Verifica periódicamente si hay resultados disponibles."""
        while self.consulta_en_progreso:
            try:
                resultado = self.controlador.obtener_resultados_consulta()
                if resultado is not None:
                    self.mostrar_resultados(resultado)
                    break
            except Exception as e:
                # Capturar errores específicos de conexión
                error_msg = str(e)
                if "Falló la conexión a la base de datos" in error_msg:
                    self.mostrar_error_conexion(error_msg)
                else:
                    self.mostrar_error(f"Error al obtener resultados: {error_msg}")
                break
            time.sleep(0.1)

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en la tabla."""
        self.root.after(0, lambda: self._mostrar_resultados_ui(resultados))

    def _mostrar_resultados_ui(self, resultados):
        """Actualiza la interfaz con los resultados."""
        if isinstance(resultados, Exception):
            # Mostrar mensaje de error estándar para errores de conexión
            error_msg = str(resultados)
            if "Falló la conexión a la base de datos" in error_msg:
                messagebox.showerror("Error de Conexión", error_msg)
            else:
                messagebox.showerror("Error", error_msg)
            self.etiqueta_estado.config(text="Error en la consulta")
            # Restaurar estado de la interfaz
            self.consulta_en_progreso = False
            self.boton_consulta.config(state='normal')
            self.boton_cancelar.config(state='disabled')
            self.barra_progreso.stop()
            return

        if resultados:
            # Guardar resultados completos
            self.resultados_completos = resultados
            
            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Mostrar resultados en la tabla
            for resultado in resultados:
                # Convertir None a cadena vacía
                valores = ['' if valor is None else str(valor) for valor in resultado]
                self.tree.insert("", tk.END, values=valores)
            
            # Actualizar estado y valores de filtros
            self.etiqueta_estado.config(text=f"Se encontraron {len(resultados)} registros")
            self.actualizar_valores_filtros()
        else:
            messagebox.showinfo("Información", "No se encontraron resultados para el rango de fechas seleccionado.")
            self.etiqueta_estado.config(text="No se encontraron resultados")

        # Restaurar estado de la interfaz
        self.consulta_en_progreso = False
        self.boton_consulta.config(state='normal')
        self.boton_cancelar.config(state='disabled')
        self.barra_progreso.stop()

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        self.root.after(0, lambda: messagebox.showerror("Error", mensaje))
        self.consulta_en_progreso = False
        self.boton_consulta.config(state='normal')
        self.boton_cancelar.config(state='disabled')
        self.barra_progreso.stop()
        self.etiqueta_estado.config(text="Error en la consulta")

    def mostrar_error_conexion(self, mensaje):
        """Muestra un mensaje de error específico para problemas de conexión."""
        self.root.after(0, lambda: messagebox.showerror("Error de Conexión", mensaje))
        self.consulta_en_progreso = False
        self.boton_consulta.config(state='normal')
        self.boton_cancelar.config(state='disabled')
        self.barra_progreso.stop()
        self.etiqueta_estado.config(text="Error de conexión a la base de datos")

    def cancelar_consulta(self):
        """Cancela la consulta en progreso."""
        if self.consulta_en_progreso:
            self.consulta_en_progreso = False
            self.boton_consulta.config(state='normal')
            self.boton_cancelar.config(state='disabled')
            self.barra_progreso.stop()
            self.etiqueta_estado.config(text="Consulta cancelada")

    def volver_inicio(self):
        """Vuelve a la ventana principal."""
        # Desvincular el evento del mousewheel antes de destruir la ventana
        self.root.unbind_all("<MouseWheel>")
        self.root.destroy()

    def exportar_a_excel(self):
        """Inicia el proceso de exportación a Excel en un hilo separado."""
        if not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return

        # Verificar si ya hay una exportación en progreso
        if hasattr(self, 'exportacion_en_progreso') and self.exportacion_en_progreso:
            messagebox.showwarning("Advertencia", "Ya hay una exportación en progreso.")
            return

        # Obtener los datos actuales de la tabla
        datos = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            datos.append(valores)

        if not datos:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return

        # Crear DataFrame
        columnas = [
            "ID", "Formulario", "Fecha", "Hora", "Localidad",
            "Clases Vehículos", "Placas", "Condiciones Actores",
            "Fallecidos", "Heridos", "Ilesos", "Estados",
            "Géneros", "Edades", "Causante", "Causa", 
            "Terreno Vía", "Estado Vía"
        ]
        df = pd.DataFrame(datos, columns=columnas)

        # Generar nombre de archivo con fecha y hora
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"siniestros_{fecha_hora}.xlsx"

        # Abrir diálogo para guardar archivo
        destino = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=nombre_archivo,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not destino:
            return

        # Configurar estado de exportación
        self.exportacion_en_progreso = True
        self.boton_exportar.config(state='disabled')
        self.barra_progreso.config(mode='determinate')
        self.barra_progreso['maximum'] = 100
        self.barra_progreso['value'] = 0
        self.barra_progreso.start()
        self.etiqueta_estado.config(text="Exportando a Excel...")

        # Iniciar exportación en hilo separado
        threading.Thread(
            target=self._exportar_a_excel_hilo,
            args=(df, destino),
            daemon=True
        ).start()

    def _exportar_a_excel_hilo(self, df, destino):
        """Exporta los datos a Excel en un hilo separado."""
        try:
            # Escritura robusta: archivo temporal en misma carpeta
            carpeta_destino = os.path.dirname(destino) or os.getcwd()
            nombre_tmp = f".__tmp_{os.path.basename(destino)}"
            ruta_tmp = os.path.join(carpeta_destino, nombre_tmp)

            # Tamaño por hoja para grandes volúmenes
            filas_por_hoja = 100000  # Excel soporta ~1,048,576 filas
            total_filas = len(df)

            try:
                with pd.ExcelWriter(ruta_tmp, engine="openpyxl") as writer:
                    if total_filas <= filas_por_hoja:
                        # Actualizar progreso
                        self.root.after(0, lambda: self._actualizar_progreso(50))
                        df.to_excel(writer, sheet_name="Datos", index=False)
                        self.root.after(0, lambda: self._actualizar_progreso(90))
                    else:
                        num_hojas = (total_filas + filas_por_hoja - 1) // filas_por_hoja
                        progreso_por_hoja = 80 / num_hojas
                        
                        for i in range(num_hojas):
                            inicio = i * filas_por_hoja
                            fin = min((i + 1) * filas_por_hoja, total_filas)
                            hoja = f"Datos_{i+1}"
                            
                            # Actualizar progreso
                            progreso_actual = 10 + (i * progreso_por_hoja)
                            self.root.after(0, lambda p=progreso_actual: self._actualizar_progreso(p))
                            
                            df.iloc[inicio:fin].to_excel(writer, sheet_name=hoja, index=False)

                # Mover atómicamente al destino final
                self.root.after(0, lambda: self._actualizar_progreso(95))
                
                if os.path.exists(destino):
                    try:
                        os.remove(destino)
                    except Exception:
                        pass
                os.replace(ruta_tmp, destino)
                
                # Completar exportación
                self.root.after(0, lambda: self._completar_exportacion(True, destino))
                
            finally:
                # Limpiar temporal si quedó
                if os.path.exists(ruta_tmp):
                    try:
                        os.remove(ruta_tmp)
                    except Exception:
                        pass

        except Exception as e:
            self.root.after(0, lambda: self._completar_exportacion(False, str(e)))

    def _actualizar_progreso(self, valor):
        """Actualiza la barra de progreso desde el hilo principal."""
        self.barra_progreso['value'] = valor
        self.etiqueta_estado.config(text=f"Exportando a Excel... {int(valor)}%")

    def _completar_exportacion(self, exito, mensaje):
        """Completa el proceso de exportación y restaura la interfaz."""
        self.exportacion_en_progreso = False
        self.boton_exportar.config(state='normal')
        self.barra_progreso.stop()
        self.barra_progreso.config(mode='indeterminate')
        
        if exito:
            self.etiqueta_estado.config(text=f"Exportación completada: {len(self.tree.get_children())} registros")
            messagebox.showinfo("Éxito", f"Los datos se han exportado correctamente a:\n{mensaje}")
        else:
            self.etiqueta_estado.config(text="Error en la exportación")
            messagebox.showerror("Error", f"Error al exportar a Excel: {mensaje}")

    def ordenar_por_columna(self, columna):
        """Ordena los datos de la tabla por la columna especificada."""
        if not self.resultados_completos:
            return
        
        # Determinar el orden de ordenamiento
        if self.columna_ordenamiento == columna:
            # Si es la misma columna, invertir el orden
            self.orden_descendente = not self.orden_descendente
        else:
            # Si es una nueva columna, empezar con orden descendente
            self.columna_ordenamiento = columna
            self.orden_descendente = True
        
        # Actualizar el indicador visual en el encabezado
        self._actualizar_indicador_ordenamiento(columna)
        
        # Obtener los datos actuales de la tabla
        datos = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            datos.append(valores)
        
        if not datos:
            return
        
        # Mapear nombres de columnas a índices
        columnas = [
            "ID", "Formulario", "Fecha", "Hora", "Localidad",
            "Clases Vehículos", "Placas", "Condiciones Actores",
            "Fallecidos", "Heridos", "Ilesos", "Estados",
            "Géneros", "Edades", "Causante", "Causa", 
            "Terreno Vía", "Estado Vía"
        ]
        
        try:
            indice_columna = columnas.index(columna)
            
            # Ordenar los datos
            if columna in ["ID", "Fallecidos", "Heridos", "Ilesos"]:
                # Ordenamiento numérico
                datos_ordenados = sorted(datos, 
                    key=lambda x: int(x[indice_columna]) if x[indice_columna] and str(x[indice_columna]).isdigit() else 0,
                    reverse=self.orden_descendente
                )
            elif columna in ["Fecha", "Hora"]:
                # Ordenamiento por fecha/hora
                datos_ordenados = sorted(datos,
                    key=lambda x: x[indice_columna] if x[indice_columna] else "",
                    reverse=self.orden_descendente
                )
            else:
                # Ordenamiento alfabético
                datos_ordenados = sorted(datos,
                    key=lambda x: str(x[indice_columna]).lower() if x[indice_columna] else "",
                    reverse=self.orden_descendente
                )
            
            # Limpiar la tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insertar los datos ordenados
            for resultado in datos_ordenados:
                # Convertir None a cadena vacía
                valores = ['' if valor is None else str(valor) for valor in resultado]
                self.tree.insert("", tk.END, values=valores)
            
            # Actualizar el estado
            orden_texto = "descendente" if self.orden_descendente else "ascendente"
            self.etiqueta_estado.config(text=f"Ordenado por {columna} ({orden_texto}) - {len(datos_ordenados)} registros")
            
        except (ValueError, IndexError) as e:
            print(f"Error al ordenar por columna {columna}: {str(e)}")
            messagebox.showerror("Error", f"No se pudo ordenar por la columna {columna}")

    def _actualizar_indicador_ordenamiento(self, columna_actual):
        """Actualiza los indicadores visuales de ordenamiento en los encabezados."""
        columnas = [
            "ID", "Formulario", "Fecha", "Hora", "Localidad",
            "Clases Vehículos", "Placas", "Condiciones Actores",
            "Fallecidos", "Heridos", "Ilesos", "Estados",
            "Géneros", "Edades", "Causante", "Causa", 
            "Terreno Vía", "Estado Vía"
        ]
        
        for col in columnas:
            if col == columna_actual:
                # Agregar indicador de ordenamiento
                indicador = " ↓" if self.orden_descendente else " ↑"
                self.tree.heading(col, text=col + indicador)
            else:
                # Quitar indicador de otras columnas
                self.tree.heading(col, text=col)

    def _aplicar_ordenamiento(self, datos, columna, descendente):
        """Aplica el ordenamiento a una lista de datos."""
        columnas = [
            "ID", "Formulario", "Fecha", "Hora", "Localidad",
            "Clases Vehículos", "Placas", "Condiciones Actores",
            "Fallecidos", "Heridos", "Ilesos", "Estados",
            "Géneros", "Edades", "Causante", "Causa", 
            "Terreno Vía", "Estado Vía"
        ]
        
        try:
            indice_columna = columnas.index(columna)
            
            # Ordenar los datos
            if columna in ["ID", "Fallecidos", "Heridos", "Ilesos"]:
                # Ordenamiento numérico
                datos_ordenados = sorted(datos, 
                    key=lambda x: int(x[indice_columna]) if x[indice_columna] and str(x[indice_columna]).isdigit() else 0,
                    reverse=descendente
                )
            elif columna in ["Fecha", "Hora"]:
                # Ordenamiento por fecha/hora
                datos_ordenados = sorted(datos,
                    key=lambda x: x[indice_columna] if x[indice_columna] else "",
                    reverse=descendente
                )
            else:
                # Ordenamiento alfabético
                datos_ordenados = sorted(datos,
                    key=lambda x: str(x[indice_columna]).lower() if x[indice_columna] else "",
                    reverse=descendente
                )
            
            return datos_ordenados
            
        except (ValueError, IndexError) as e:
            print(f"Error al aplicar ordenamiento: {str(e)}")
            return datos

    def _actualizar_opciones_hora(self, datos_filtrados):
        """Actualiza las opciones de hora basadas en los datos filtrados."""
        try:
            horas = sorted(set(str(resultado[3]).strip() for resultado in datos_filtrados if resultado[3]))
            self.hora_filtro_inicio['values'] = [''] + horas
            self.hora_filtro_fin['values'] = [''] + horas
        except Exception as e:
            print(f"Error al actualizar opciones de hora: {str(e)}")

    def _actualizar_opciones_filtros(self, datos_filtrados):
        """Actualiza todas las opciones de filtros basadas en los datos filtrados."""
        try:
            # Obtener valores únicos de los datos filtrados
            localidades = sorted(set(str(resultado[4]).strip() for resultado in datos_filtrados if resultado[4]))
            ids = sorted(set(str(resultado[0]).strip() for resultado in datos_filtrados if resultado[0]))
            formularios = sorted(set(str(resultado[1]).strip() for resultado in datos_filtrados if resultado[1]))
            horas = sorted(set(str(resultado[3]).strip() for resultado in datos_filtrados if resultado[3]))
            
            # Actualizar comboboxes con los nuevos valores
            self.combo_localidad['values'] = [''] + localidades
            self.combo_id['values'] = [''] + ids
            self.combo_formulario['values'] = [''] + formularios
            self.hora_filtro_inicio['values'] = [''] + horas
            self.hora_filtro_fin['values'] = [''] + horas
            
        except Exception as e:
            print(f"Error al actualizar opciones de filtros: {str(e)}")