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

        # Configurar columnas
        for col in columnas:
            self.tree.heading(col, text=col)
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
        ttk.Button(
            nav_frame,
            text="Exportar a Excel",
            command=self.exportar_a_excel
        ).pack(side=tk.LEFT, padx=10)

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
            
            # Actualizar combobox de localidad
            self.combo_localidad['values'] = [''] + localidades
            
            # Los demás comboboxes ya tienen sus valores predefinidos
            # Solo necesitamos limpiar sus selecciones actuales
            self.combo_localidad.set('')
            self.combo_vehiculo.set('')
            self.combo_estado.set('')
            self.combo_causante.set('')

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

            # Verificar si hay algún filtro seleccionado
            if not any([localidad, vehiculo, estado, causante]):
                messagebox.showinfo("Información", "Por favor seleccione al menos un filtro.")
                return

            # Filtrar resultados
            resultados_filtrados = self.resultados_completos

            # Aplicar filtro de localidad
            if localidad:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[4]).strip() == localidad.strip()]

            # Aplicar filtro de vehículo
            if vehiculo:
                resultados_filtrados = [r for r in resultados_filtrados if vehiculo in str(r[5]).split(', ')]

            # Aplicar filtro de estado
            if estado:
                resultados_filtrados = [r for r in resultados_filtrados if estado in str(r[11]).split(', ')]

            # Aplicar filtro de causante
            if causante:
                resultados_filtrados = [r for r in resultados_filtrados if str(r[15]).strip() == causante.strip()]

            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)

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

            # Limpiar tabla actual
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Mostrar todos los resultados
            for resultado in self.resultados_completos:
                # Convertir None a cadena vacía
                valores = ['' if valor is None else str(valor) for valor in resultado]
                self.tree.insert("", tk.END, values=valores)

            self.filtros_activos = False
            self.etiqueta_estado.config(text=f"Mostrando {len(self.resultados_completos)} registros")

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
        """Exporta los datos actuales de la tabla a un archivo Excel."""
        if not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return

        try:
            # Obtener los datos actuales de la tabla
            datos = []
            for item in self.tree.get_children():
                valores = self.tree.item(item)['values']
                datos.append(valores)

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
            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=nombre_archivo,
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )

            if archivo:
                # Exportar a Excel
                df.to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", f"Los datos se han exportado correctamente a:\n{archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}") 