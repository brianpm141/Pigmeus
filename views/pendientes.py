from tkinter import *
from tkinter import ttk, messagebox
from tkinter import simpledialog
import gestion_roles as roles
import gestion_pendientes as pendientes

def construir_vista_pendientes(frame):
    frame.configure(bg="#ecf0f1")

    # --- Formulario ---
    formulario = Frame(frame, bg="#ecf0f1")
    formulario.pack(pady=10)

    Label(formulario, text="Departamento", bg="#ecf0f1").grid(row=0, column=0)
    combo_dep = ttk.Combobox(formulario, state="readonly", width=20)
    combo_dep.grid(row=0, column=1, padx=5)

    Label(formulario, text="Responsable", bg="#ecf0f1").grid(row=0, column=2)
    combo_usu = ttk.Combobox(formulario, state="readonly", width=20)
    combo_usu.grid(row=0, column=3, padx=5)

    Label(formulario, text="Título", bg="#ecf0f1").grid(row=1, column=0, pady=5)
    entry_titulo = Entry(formulario, width=40)
    entry_titulo.grid(row=1, column=1, columnspan=3, pady=5)

    Label(formulario, text="Avance", bg="#ecf0f1").grid(row=2, column=0)
    entry_desc = Entry(formulario, width=80)
    entry_desc.grid(row=2, column=1, columnspan=3, padx=5)

    # --- Tabla ---
    tabla = ttk.Treeview(frame, columns=("Título", "Responsable", "Avance", "Estado", "Creación", "Cierre"), show="headings")
    tabla.pack(expand=True, fill='both', padx=10, pady=10)

    headers = {
        "Título": 150, "Responsable": 100, "Avance": 200,
        "Estado": 80, "Creación": 120, "Cierre": 120
    }

    for col, ancho in headers.items():
        tabla.heading(col, text=col)
        tabla.column(col, width=ancho, anchor="center")

    # --- Funciones ---
    def refrescar_combos():
        deps = roles.obtener_departamentos()
        combo_dep['values'] = ['Todos'] + [d[1] for d in deps]
        combo_dep.set('Todos')

    def actualizar_usuarios(event=None):
        dep_nombre = combo_dep.get()
        deps = roles.obtener_departamentos()
        dep = next((d for d in deps if d[1] == dep_nombre), None)
        id_dep = dep[0] if dep else None
        combo_usu['values'] = [u[1] for u in roles.obtener_usuarios(id_dep)]
        combo_usu.set('')

    def cargar_pendientes():
        tabla.delete(*tabla.get_children())
        dep_nombre = combo_dep.get()
        id_dep = None
        if dep_nombre != 'Todos':
            deps = roles.obtener_departamentos()
            dep = next((d for d in deps if d[1] == dep_nombre), None)
            id_dep = dep[0] if dep else None

        for p in pendientes.obtener_pendientes(id_departamento=id_dep):
            id_, titulo, desc, avance, completado, f_creacion, f_cierre, nombre_u, _ = p
            estado = "Completado" if completado else "Pendiente"
            tabla.insert('', END, iid=id_, values=(titulo, nombre_u, avance or "", estado, f_creacion or "", f_cierre or ""))

    def registrar():
        titulo = entry_titulo.get().strip()
        desc = entry_desc.get().strip()
        usuario = combo_usu.get()

        if not titulo or not usuario:
            messagebox.showwarning("Atención", "Debe ingresar título y responsable.")
            return

        dep_nombre = combo_dep.get()
        deps = roles.obtener_departamentos()
        dep = next((d for d in deps if d[1] == dep_nombre), None)
        id_dep = dep[0] if dep else None
        id_usu = next((u[0] for u in roles.obtener_usuarios(id_dep) if u[1] == usuario), None)

        pendientes.crear_pendiente(titulo, desc, id_usu)
        limpiar_formulario()
        cargar_pendientes()

    def limpiar_formulario():
        entry_titulo.delete(0, END)
        entry_desc.delete(0, END)
        combo_usu.set('')
        boton_registrar.config(text="Registrar Pendiente", command=registrar)

    def iniciar_edicion():
        sel = tabla.focus()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pendiente.")
            return
        valores = tabla.item(sel, "values")
        entry_titulo.delete(0, END)
        entry_desc.delete(0, END)
        entry_titulo.insert(0, valores[0])
        entry_desc.insert(0, valores[2])
        boton_registrar.config(text="Guardar Cambios", command=guardar_cambios)

    def guardar_cambios():
        sel = tabla.focus()
        if not sel:
            return
        nuevo_titulo = entry_titulo.get().strip()
        nueva_desc = entry_desc.get().strip()
        pendientes.actualizar_pendiente(int(sel), nuevo_titulo, nueva_desc)
        limpiar_formulario()
        cargar_pendientes()

    def registrar_avance():
        sel = tabla.focus()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un pendiente.")
            return
        nuevo_avance = simpledialog.askstring("Avance", "Ingrese el avance:")
        if nuevo_avance is not None:
            pendientes.registrar_avance(int(sel), nuevo_avance)
            cargar_pendientes()

    def marcar_completado():
        sel = tabla.focus()
        if sel:
            pendientes.marcar_completado(int(sel))
            cargar_pendientes()

    def marcar_pendiente():
        sel = tabla.focus()
        if sel:
            pendientes.marcar_pendiente(int(sel))
            cargar_pendientes()

    def eliminar():
        sel = tabla.focus()
        if sel and messagebox.askyesno("Confirmar", "¿Eliminar pendiente?"):
            pendientes.eliminar_pendiente(int(sel))
            cargar_pendientes()

    # --- Botones ---
    acciones = Frame(frame, bg="#ecf0f1")
    acciones.pack()

    boton_registrar = Button(acciones, text="Registrar Pendiente", command=registrar)
    boton_registrar.pack(side=LEFT, padx=10)

    Button(acciones, text="Editar", command=iniciar_edicion).pack(side=LEFT, padx=10)
    Button(acciones, text="Avance", command=registrar_avance).pack(side=LEFT, padx=10)
    Button(acciones, text="Completado", command=marcar_completado).pack(side=LEFT, padx=10)
    Button(acciones, text="Pendiente", command=marcar_pendiente).pack(side=LEFT, padx=10)
    Button(acciones, text="Eliminar", command=eliminar).pack(side=LEFT, padx=10)

    # Eventos y carga inicial
    combo_dep.bind("<<ComboboxSelected>>", actualizar_usuarios)

    refrescar_combos()
    actualizar_usuarios()
    cargar_pendientes()
