# views/menu.py
from tkinter import *
from tkinter import ttk
from views.actividades import construir_vista_actividades
from views.gestion import construir_vista_gestion
from views.pendientes import construir_vista_pendientes

def construir_menu_general(parent):
    parent.configure(bg="#f0f0f0")

    # Panel lateral
    menu = Frame(parent, width=200, bg="#2c3e50")
    menu.pack(side=LEFT, fill=Y)

    # Contenedor central donde se cargan vistas
    contenido = Frame(parent, bg="#ecf0f1")
    contenido.pack(side=LEFT, fill=BOTH, expand=True)

    # Función para cambiar de vista
    def mostrar_vista(func):
        for widget in contenido.winfo_children():
            widget.destroy()
        func(contenido)

    # Botones del menú
    style = {"font": ("Helvetica", 13), "bg": "#34495e", "fg": "white", "activebackground": "#1abc9c"}
    Button(menu, text="Actividades", command=lambda: mostrar_vista(construir_vista_actividades), **style).pack(fill=X, pady=2)
    Button(menu, text="Pisos y Áreas", command=lambda: mostrar_vista(construir_vista_gestion), **style).pack(fill=X, pady=2)
    Button(menu, text="Pendientes", command=lambda: mostrar_vista(construir_vista_pendientes), **style).pack(fill=X, pady=2)

    # Cargar vista inicial
    mostrar_vista(construir_vista_actividades)





