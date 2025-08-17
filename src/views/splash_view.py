import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashView:
    def __init__(self, root, image_path, duration=5000):
        self.root = root
        self.duration = duration
        
        # Configurar la ventana del splash
        self.root.overrideredirect(True)  # Eliminar la barra de título
        self.root.attributes('-topmost', True)  # Mantener siempre visible
        
        # Cargar la imagen
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        
        # Crear el canvas para mostrar la imagen
        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height, highlightthickness=0)
        self.canvas.pack()
        
        # Mostrar la imagen
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        
        # Centrar la ventana
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - self.image.width) // 2
        y = (screen_height - self.image.height) // 2
        root.geometry(f"{self.image.width}x{self.image.height}+{x}+{y}")
        
        # Programar el cierre después de la duración especificada
        self.root.after(self.duration, self.close)
    
    def close(self):
        self.root.destroy() 