# views/gestion.py
from tkinter import *
from tkinter import ttk, messagebox
import gestion_roles as roles

def construir_vista_gestion(frame):
    frame.configure(bg="#ecf0f1")

    # --- Layout principal horizontal ---
    layout = Frame(frame, bg="#ecf0f1")
    layout.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # --- Sección Departamentos ---
    left_frame = Frame(layout, bg="#ecf0f1")
    left_frame.pack(side=LEFT, fill=Y, padx=10)

    Label(left_frame, text="Departamentos", font=("Helvetica", 14, "bold"), bg="#ecf0f1").pack()

    tree_departamentos = ttk.Treeview(left_frame, columns=('Nombre'), show='headings', height=10)
    tree_departamentos.heading('Nombre', text='Nombre')
    tree_departamentos.pack(pady=5)

    entry_departamento = Entry(left_frame)
    entry_departamento.pack(pady=5, fill=X)

    def crear_departamento():
        nombre = entry_departamento.get().strip()
        if nombre:
            if roles.crear_departamento(nombre):
                refrescar_departamentos()
                entry_departamento.delete(0, END)

    def eliminar_departamento():
        sel = tree_departamentos.focus()
        if sel:
            nombre = tree_departamentos.item(sel)['values'][0]
            deps = roles.obtener_departamentos()
            id_dep = next((d[0] for d in deps if d[1] == nombre), None)
            if id_dep:
                if messagebox.askyesno("Confirmar", f"Eliminar departamento '{nombre}'?"):
                    roles.eliminar_departamento(id_dep)
                    refrescar_departamentos()
                    refrescar_usuarios_y_categorias()

    Button(left_frame, text="Crear", command=crear_departamento).pack(pady=2, fill=X)
    Button(left_frame, text="Eliminar", command=eliminar_departamento).pack(pady=2, fill=X)

    # --- Sección derecha: selector + usuarios y categorías ---
    right_frame = Frame(layout, bg="#ecf0f1")
    right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)

    selector = Frame(right_frame, bg="#ecf0f1")
    selector.pack(fill=X)

    Label(selector, text="Departamento:", bg="#ecf0f1").pack(side=LEFT)
    combo_dep = ttk.Combobox(selector, state="readonly")
    combo_dep.pack(side=LEFT, padx=10)

    # --- Usuarios y Categorías ---
    split = Frame(right_frame, bg="#ecf0f1")
    split.pack(fill=BOTH, expand=True)

    # Usuarios
    usuarios_frame = Frame(split, bg="#ecf0f1")
    usuarios_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=5)

    Label(usuarios_frame, text="Usuarios", font=("Helvetica", 12, "bold"), bg="#ecf0f1").pack()
    tree_usuarios = ttk.Treeview(usuarios_frame, columns=('Nombre'), show='headings')
    tree_usuarios.heading('Nombre', text='Nombre')
    tree_usuarios.pack(fill=BOTH, expand=True, pady=5)

    entry_usuario = Entry(usuarios_frame)
    entry_usuario.pack(fill=X, pady=5)

    def crear_usuario():
        nombre = entry_usuario.get().strip()
        if not nombre:
            return
        dep = combo_dep.get()
        id_dep = obtener_id_departamento(dep)
        if id_dep:
            if roles.crear_usuario(nombre, id_dep):
                entry_usuario.delete(0, END)
                refrescar_usuarios_y_categorias()

    def eliminar_usuario():
        sel = tree_usuarios.focus()
        if sel:
            nombre = tree_usuarios.item(sel)['values'][0]
            dep = combo_dep.get()
            id_dep = obtener_id_departamento(dep)
            usuarios = roles.obtener_usuarios(id_dep)
            id_u = next((u[0] for u in usuarios if u[1] == nombre), None)
            if id_u:
                if messagebox.askyesno("Confirmar", f"Eliminar usuario '{nombre}'?"):
                    roles.eliminar_usuario(id_u)
                    refrescar_usuarios_y_categorias()

    Button(usuarios_frame, text="Crear", command=crear_usuario).pack(fill=X, pady=2)
    Button(usuarios_frame, text="Eliminar", command=eliminar_usuario).pack(fill=X, pady=2)

    # Categorías
    categorias_frame = Frame(split, bg="#ecf0f1")
    categorias_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=5)

    Label(categorias_frame, text="Categorías", font=("Helvetica", 12, "bold"), bg="#ecf0f1").pack()
    tree_categorias = ttk.Treeview(categorias_frame, columns=('Nombre'), show='headings')
    tree_categorias.heading('Nombre', text='Nombre')
    tree_categorias.pack(fill=BOTH, expand=True, pady=5)

    entry_categoria = Entry(categorias_frame)
    entry_categoria.pack(fill=X, pady=5)

    def crear_categoria():
        nombre = entry_categoria.get().strip()
        if not nombre:
            return
        dep = combo_dep.get()
        id_dep = obtener_id_departamento(dep)
        if id_dep:
            if roles.crear_categoria(nombre, id_dep):
                entry_categoria.delete(0, END)
                refrescar_usuarios_y_categorias()

    def eliminar_categoria():
        sel = tree_categorias.focus()
        if sel:
            nombre = tree_categorias.item(sel)['values'][0]
            dep = combo_dep.get()
            id_dep = obtener_id_departamento(dep)
            categorias = roles.obtener_categorias(id_dep)
            id_c = next((c[0] for c in categorias if c[1] == nombre), None)
            if id_c:
                if messagebox.askyesno("Confirmar", f"Eliminar categoría '{nombre}'?"):
                    roles.eliminar_categoria(id_c)
                    refrescar_usuarios_y_categorias()

    Button(categorias_frame, text="Crear", command=crear_categoria).pack(fill=X, pady=2)
    Button(categorias_frame, text="Eliminar", command=eliminar_categoria).pack(fill=X, pady=2)

    # --- Funciones de ayuda ---
    def obtener_id_departamento(nombre):
        deps = roles.obtener_departamentos()
        dep = next((d for d in deps if d[1] == nombre), None)
        return dep[0] if dep else None

    def refrescar_departamentos():
        tree_departamentos.delete(*tree_departamentos.get_children())
        for d in roles.obtener_departamentos():
            tree_departamentos.insert('', END, values=(d[1],))
        combo_dep['values'] = [d[1] for d in roles.obtener_departamentos()]
        if combo_dep['values']:
            combo_dep.set(combo_dep['values'][0])
            refrescar_usuarios_y_categorias()

    def refrescar_usuarios_y_categorias(*args):
        dep = combo_dep.get()
        id_dep = obtener_id_departamento(dep)

        # Usuarios
        tree_usuarios.delete(*tree_usuarios.get_children())
        for u in roles.obtener_usuarios(id_dep):
            tree_usuarios.insert('', END, values=(u[1],))

        # Categorías
        tree_categorias.delete(*tree_categorias.get_children())
        for c in roles.obtener_categorias(id_dep):
            tree_categorias.insert('', END, values=(c[1],))

    combo_dep.bind("<<ComboboxSelected>>", refrescar_usuarios_y_categorias)

    refrescar_departamentos()
