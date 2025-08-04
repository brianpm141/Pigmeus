# views/actividades.py
from tkinter import *
from tkinter import ttk, messagebox
import gestion_roles as roles
import gestion_actividades as actividades

def construir_vista_actividades(frame):
    frame.configure(bg="#ecf0f1")

    # --- Formularios ---
    formulario = Frame(frame, bg="#ecf0f1")
    formulario.pack(pady=10)

    Label(formulario, text="Departamento", bg="#ecf0f1").grid(row=0, column=0)
    combo_dep = ttk.Combobox(formulario, state="readonly", width=20)
    combo_dep.grid(row=0, column=1, padx=5)

    Label(formulario, text="Usuario", bg="#ecf0f1").grid(row=0, column=2)
    combo_usu = ttk.Combobox(formulario, state="readonly", width=20)
    combo_usu.grid(row=0, column=3, padx=5)

    Label(formulario, text="Categoría", bg="#ecf0f1").grid(row=0, column=4)
    combo_cat = ttk.Combobox(formulario, state="readonly", width=20)
    combo_cat.grid(row=0, column=5, padx=5)

    Label(formulario, text="Detalles", bg="#ecf0f1").grid(row=1, column=0, pady=10)
    entry_detalles = Entry(formulario, width=80)
    entry_detalles.grid(row=1, column=1, columnspan=5, pady=10, padx=5)

    # --- Tabla de actividades ---
    tabla = ttk.Treeview(frame,
        columns=('Usuario', 'Categoría', 'Detalles', 'Estado',
                'Fecha inicio', 'Hora inicio', 'Fecha cierre', 'Hora cierre'),
        show='headings'
    )  

    tabla.pack(expand=True, fill='both', padx=10, pady=10)

    # Ocultamos la columna interna #0
    tabla.column('#0', width=0, minwidth=0, stretch=False)

    anchos = {
    'Usuario':     80,
    'Categoría':   80,
    'Detalles':    300,
    'Estado':      80,
    'Fecha inicio':80,
    'Hora inicio': 70,
    'Fecha cierre':80,
    'Hora cierre': 70,
    }

    for col, w in anchos.items():
        tabla.heading(col, text=col)
        tabla.column(col, width=w, minwidth=30, anchor='center')    

    # --- Funciones ---
    def refrescar_combos():
        deps = roles.obtener_departamentos()
        valores_dep = ['Todos'] + [d[1] for d in deps]
        combo_dep['values'] = valores_dep
        combo_dep.set('Todos')

    def actualizar_usuarios_y_categorias(*args):
        dep_nombre = combo_dep.get()
        deps = roles.obtener_departamentos()
        dep = next((d for d in deps if d[1] == dep_nombre), None)
        id_dep = dep[0] if dep else None
        combo_usu['values'] = [u[1] for u in roles.obtener_usuarios(id_dep)]
        combo_cat['values'] = [c[1] for c in roles.obtener_categorias(id_dep)]
        combo_usu.set('')
        combo_cat.set('')

    def registrar():
        detalles = entry_detalles.get().strip()
        if not detalles:
            messagebox.showwarning("Atención", "Ingrese detalles.")
            return
        dep_nombre = combo_dep.get()
        deps = roles.obtener_departamentos()
        dep = next((d for d in deps if d[1] == dep_nombre), None)
        id_dep = dep[0] if dep else None
        usu_nombre = combo_usu.get()
        cat_nombre = combo_cat.get()
        id_usu = next((u[0] for u in roles.obtener_usuarios(id_dep) if u[1] == usu_nombre), None)
        id_cat = next((c[0] for c in roles.obtener_categorias(id_dep) if c[1] == cat_nombre), None)
        actividades.registrar_actividad(detalles, id_usu, id_cat)
        entry_detalles.delete(0, END)
        cargar_actividades()

    def cargar_actividades():
        # 1) Determinar id_dep: si es “Todos”, dejamos None para traer todo
        dep_nombre = combo_dep.get()
        if dep_nombre == 'Todos':
            id_dep = None
        else:
            deps = roles.obtener_departamentos()
            dep = next((d for d in deps if d[1] == dep_nombre), None)
            id_dep = dep[0] if dep else None

        # 2) Limpiar la tabla
        for row in tabla.get_children():
            tabla.delete(row)

        # 3) Pasar id_dep (o None) y mostrar resultados
        for act in actividades.obtener_actividades(id_dep):
            id_, hora_llegada, detalles, usuario, categoria, atendido, hora_cierre = act
            if hora_llegada:
                fecha_inicio, hora_inicio = hora_llegada.split()
            else:
                fecha_inicio, hora_inicio = '', ''
            if hora_cierre:
                fecha_cierre, hora_cierre_str = hora_cierre.split()
            else:
                fecha_cierre, hora_cierre_str = '', ''
            estado = "Completado" if atendido else "Pendiente"
            tabla.insert(
                '', END, iid=id_,
                values=(
                    usuario, categoria, detalles, estado,
                    fecha_inicio, hora_inicio,
                    fecha_cierre, hora_cierre_str
                )
            )


    def marcar_completada():
        sel = tabla.focus()
        if sel:
            actividades.marcar_completada(int(sel))
            cargar_actividades()

    def marcar_pendiente():
        sel = tabla.focus()
        if sel:
            actividades.marcar_pendiente(int(sel))
            cargar_actividades()

    def iniciar_edicion():
        sel = tabla.focus()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una actividad para editar.")
            return
        valores = tabla.item(sel, "values")
        detalles_act = valores[2]  # columna Detalles
        entry_detalles.delete(0, END)
        entry_detalles.insert(0, detalles_act)
        boton_registrar.config(text="Guardar Cambios", command=guardar_cambios)

    def guardar_cambios():
        sel = tabla.focus()
        nuevos_detalles = entry_detalles.get().strip()
        if not sel or not nuevos_detalles:
            messagebox.showwarning("Atención", "Seleccione actividad e ingrese detalles.")
            return
        actividades.actualizar_detalles(int(sel), nuevos_detalles)
        # reset formulario
        entry_detalles.delete(0, END)
        boton_registrar.config(text="Registrar Actividad", command=registrar)
        tabla.selection_remove(sel)
        cargar_actividades()

    def on_dep_change(event):            
        actualizar_usuarios_y_categorias()  
        cargar_actividades() 

    # --- Botón registrar y acciones ---
    # --- Botón registrar y acciones ---
    botonera = Frame(frame, bg="#ecf0f1")
    botonera.pack()

    # Guarda el botón en la variable para poder hacer .config() sobre él
    boton_registrar = Button(botonera, text="Registrar Actividad", command=registrar)
    boton_registrar.pack(side=LEFT, padx=10)

    Button(botonera, text="Editar Detalles", command=iniciar_edicion).pack(side=LEFT, padx=10)
    Button(botonera, text="Marcar Completada", command=marcar_completada).pack(side=LEFT, padx=10)
    Button(botonera, text="Marcar Pendiente", command=marcar_pendiente).pack(side=LEFT, padx=10)

    combo_dep.bind("<<ComboboxSelected>>", on_dep_change)

    refrescar_combos()
    cargar_actividades()
