import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkinter.simpledialog import askstring
import pandas as pd

# Inicializar base de datos y tablas
def init_db():
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            id_departamento INTEGER,
            UNIQUE(nombre, id_departamento),
            FOREIGN KEY(id_departamento) REFERENCES departamentos(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            id_departamento INTEGER,
            UNIQUE(nombre, id_departamento),
            FOREIGN KEY(id_departamento) REFERENCES departamentos(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hora_llegada TEXT,
            detalles TEXT,
            id_usuario INTEGER,
            id_categoria INTEGER,
            atendido INTEGER DEFAULT 0,
            hora_cierre TEXT,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
            FOREIGN KEY(id_categoria) REFERENCES categorias(id)
        )
    ''')
    conn.commit()
    return conn, cursor

# Conexión global
db_conn, cursor = init_db()

# Funciones auxiliares
def obtener_usuarios(id_departamento=None):
    if id_departamento:
        cursor.execute('SELECT id, nombre FROM usuarios WHERE id_departamento = ?', (id_departamento,))
    else:
        cursor.execute('SELECT id, nombre FROM usuarios')
    return cursor.fetchall()

def obtener_categorias(id_departamento=None):
    if id_departamento:
        cursor.execute('SELECT id, nombre FROM categorias WHERE id_departamento = ?', (id_departamento,))
    else:
        cursor.execute('SELECT id, nombre FROM categorias')
    return cursor.fetchall()

def obtener_departamentos():
    cursor.execute('SELECT id, nombre FROM departamentos')
    return cursor.fetchall()

def obtener_llamadas(filtro_usuario=None, filtro_categoria=None):
    query = '''
        SELECT l.id, l.hora_llegada, l.detalles, u.nombre, c.nombre, l.atendido, l.hora_cierre
        FROM llamadas l
        LEFT JOIN usuarios u ON l.id_usuario = u.id
        LEFT JOIN categorias c ON l.id_categoria = c.id
    '''
    params = []
    condiciones = []
    if filtro_usuario:
        condiciones.append("u.nombre = ?")
        params.append(filtro_usuario)
    if filtro_categoria:
        condiciones.append("c.nombre = ?")
        params.append(filtro_categoria)
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    query += " ORDER BY l.id DESC"
    cursor.execute(query, params)
    return cursor.fetchall()

def exportar_excel():
    datos = obtener_llamadas()
    filas = []
    for row in datos:
        # row = (id, hora_llegada, detalles, usuario, categoria, atendido, hora_cierre)
        _, hora_llegada, detalles, usuario, categoria, atendido, hora_cierre = row
        fecha, hora = hora_llegada.split(" ") if hora_llegada else ("", "")
        fecha_cierre, hora_cierre_val = ("", "")
        if hora_cierre:
            parts = hora_cierre.split(" ")
            fecha_cierre = parts[0]
            hora_cierre_val = parts[1] if len(parts) > 1 else ""
        filas.append({
            "Fecha": fecha,
            "Fecha Cierre": fecha_cierre,
            "Hora": hora,
            "Hora Cierre": hora_cierre_val,
            "Usuario": usuario or '',
            "Categoría": categoria or '',
            "Detalles": detalles or '',
            "Estado": "Atendido" if atendido else "Pendiente"
        })

    df = pd.DataFrame(filas)
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file:
        df.to_excel(file, index=False)
        messagebox.showinfo("Exportado", f"Archivo guardado como\n{file}")


def registrar_llamada():
    detalles = entry_detalles.get().strip()
    if not detalles:
        messagebox.showwarning("Atención", "Ingrese detalles de la falla.")
        return
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    if not id_dep:
        messagebox.showwarning("Atención", "Seleccione un departamento.")
        return
    usuario_nombre = combo_usuario.get()
    categoria_nombre = combo_categoria.get()
    id_usuario = next((u[0] for u in obtener_usuarios(id_dep) if u[1] == usuario_nombre), None)
    id_categoria = next((c[0] for c in obtener_categorias(id_dep) if c[1] == categoria_nombre), None)
    hora_llegada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT INTO llamadas (hora_llegada, detalles, id_usuario, id_categoria) VALUES (?, ?, ?, ?)',
        (hora_llegada, detalles, id_usuario, id_categoria)
    )
    db_conn.commit()
    entry_detalles.delete(0, END)
    combo_usuario.set('')
    combo_categoria.set('')
    refrescar_combos_llamada()
    refrescar_combos()
    refrescar_filtros()
    actualizar_tabla()

def marcar_atendida():
    sel = tabla_llamadas.focus()
    if not sel:
        return
    id_llamada = int(sel)
    hora_cierre = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE llamadas SET atendido = 1, hora_cierre = ? WHERE id = ?', (hora_cierre, id_llamada))
    db_conn.commit()
    actualizar_tabla()

def marcar_pendiente():
    sel = tabla_llamadas.focus()
    if not sel:
        messagebox.showwarning("Atención", "Seleccione una llamada para marcar como pendiente.")
        return
    id_llamada = int(sel)
    cursor.execute('UPDATE llamadas SET atendido = 0, hora_cierre = NULL WHERE id = ?', (id_llamada,))
    db_conn.commit()
    actualizar_tabla()

def editar_detalles():
    sel = tabla_llamadas.focus()
    if not sel:
        messagebox.showwarning("Atención", "Seleccione una llamada para editar.")
        return

    id_llamada = int(sel)
    detalles_actual = tabla_llamadas.item(sel)['values'][6]  # Columna de detalles

    ventana = Toplevel(app)
    ventana.title("Editar Detalles")
    ventana.geometry("600x300")  # Aumenta tamaño de la ventana
    ventana.configure(bg="#f0f0f0")
    ventana.transient(app)  # Bloquea detrás

    Label(ventana, text="Nuevo detalle:", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(pady=10)

    text_area = Text(ventana, wrap=WORD, font=("Helvetica", 13), height=10)
    text_area.pack(expand=True, fill=BOTH, padx=20, pady=10)
    text_area.insert(END, detalles_actual)

    def guardar():
        nuevo = text_area.get("1.0", END).strip()
        if nuevo:
            cursor.execute('UPDATE llamadas SET detalles = ? WHERE id = ?', (nuevo, id_llamada))
            db_conn.commit()
            actualizar_tabla()
            ventana.destroy()

    Button(ventana, text="Guardar", command=guardar, font=("Helvetica", 13), bg="#4CAF50", fg="white").pack(pady=10)




def crear_departamento():
    nombre = entry_departamento.get().strip()
    if not nombre:
        return
    try:
        cursor.execute('INSERT INTO departamentos (nombre) VALUES (?)', (nombre,))
        db_conn.commit()
        entry_departamento.delete(0, END)
        refrescar_departamentos()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Departamento ya existe.")

def eliminar_departamento_ui():
    sel = tv_departamentos.focus()
    if not sel:
        return
    id_d = tv_departamentos.item(sel)['values'][0]
    if messagebox.askyesno("Confirmar", f"Eliminar departamento ID {id_d}?"):
        cursor.execute('DELETE FROM departamentos WHERE id = ?', (id_d,))
        db_conn.commit()
        refrescar_departamentos()

def refrescar_departamentos():
    for i in tv_departamentos.get_children():
        tv_departamentos.delete(i)
    for d in obtener_departamentos():
        tv_departamentos.insert('', END, values=(d[1]))  # Mostrar nombre, no ID
    combo_departamento_gestion['values'] = [d[1] for d in obtener_departamentos()]


def actualizar_tabla():
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    usuario = filtro_usuario.get()
    categoria = filtro_categoria.get()
    usuario = usuario if usuario and usuario != "Todos" else None
    categoria = categoria if categoria and categoria != "Todos" else None
    for item in tabla_llamadas.get_children():
        tabla_llamadas.delete(item)
    # Filtrar llamadas por departamento, usuario y categoría
    llamadas = []
    for llamada in obtener_llamadas(usuario, categoria):
        # llamada: (id, hora_llegada, detalles, usuario, categoria, atendido, hora_cierre)
        # Necesitamos filtrar por departamento
        if id_dep:
            # Buscar usuario y categoría en este departamento
            usuario_nombre = llamada[3]
            categoria_nombre = llamada[4]
            usuario_obj = next((u for u in obtener_usuarios(id_dep) if u[1] == usuario_nombre), None)
            categoria_obj = next((c for c in obtener_categorias(id_dep) if c[1] == categoria_nombre), None)
            if not usuario_obj and not categoria_obj:
                continue
        llamadas.append(llamada)
    for llamada in llamadas:
        id_llamada, hora_llegada, detalles, usuario, categoria, atendido_flag, hora_cierre = llamada
        fecha, hora = ('-', '-')
        if hora_llegada:
            parts = hora_llegada.split(' ')
            fecha = parts[0]
            hora = parts[1] if len(parts) > 1 else ''
        fecha_cierre, hora_cierre_val = ('-', '-')
        if hora_cierre:
            parts_cierre = hora_cierre.split(' ')
            fecha_cierre = parts_cierre[0]
            hora_cierre_val = parts_cierre[1] if len(parts_cierre) > 1 else ''
        estado_texto = 'Atendido' if atendido_flag else 'Pendiente'
        tabla_llamadas.insert('', END, iid=str(id_llamada), values=(
            fecha, fecha_cierre, hora, hora_cierre_val, usuario or '-', categoria or '-', detalles, estado_texto
        ))


def crear_usuario():
    nombre = entry_usuario.get().strip()
    if not nombre:
        return
    dep_nombre = combo_departamento_gestion.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    if not id_dep:
        messagebox.showwarning("Atención", "Seleccione un departamento.")
        return
    try:
        cursor.execute('INSERT INTO usuarios (nombre, id_departamento) VALUES (?, ?)', (nombre, id_dep))
        db_conn.commit()
        entry_usuario.delete(0, END)
        refrescar_usuarios_y_categorias_por_departamento()
        refrescar_combos()
        refrescar_filtros()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Usuario ya existe en este departamento.")

def eliminar_usuario_ui():
    sel = tv_usuarios.focus()
    if not sel:
        return
    id_u = tv_usuarios.item(sel)['values'][0]
    if messagebox.askyesno("Confirmar", f"Eliminar usuario ID {id_u}?"):
        cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_u,))
        db_conn.commit()
        refrescar_usuarios()
        refrescar_combos()
        refrescar_filtros()  # <-- Añade esto

def crear_categoria():
    nombre = entry_categoria.get().strip()
    if not nombre:
        return
    dep_nombre = combo_departamento_gestion.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    if not id_dep:
        messagebox.showwarning("Atención", "Seleccione un departamento.")
        return
    try:
        cursor.execute('INSERT INTO categorias (nombre, id_departamento) VALUES (?, ?)', (nombre, id_dep))
        db_conn.commit()
        entry_categoria.delete(0, END)
        refrescar_usuarios_y_categorias_por_departamento()
        refrescar_combos()
        refrescar_filtros()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Categoría ya existe en este departamento.")

def eliminar_categoria_ui():
    sel = tv_categorias.focus()
    if not sel:
        return
    id_c = tv_categorias.item(sel)['values'][0]
    if messagebox.askyesno("Confirmar", f"Eliminar categoría ID {id_c}?"):
        cursor.execute('DELETE FROM categorias WHERE id = ?', (id_c,))
        db_conn.commit()
        refrescar_categorias()
        refrescar_combos()
        refrescar_filtros()  # <-- Añade esto

def refrescar_usuarios():
    for i in tv_usuarios.get_children():
        tv_usuarios.delete(i)
    for u in obtener_usuarios():
        tv_usuarios.insert('', END, values=(u[1]))

def refrescar_categorias():
    for i in tv_categorias.get_children():
        tv_categorias.delete(i)
    for c in obtener_categorias():
        tv_categorias.insert('', END, values=(c[1]))

def refrescar_usuarios_y_categorias_por_departamento(*args):
    dep_nombre = combo_departamento_gestion.get()
    if not dep_nombre:
        # Limpiar si no hay departamento seleccionado
        for i in tv_usuarios.get_children():
            tv_usuarios.delete(i)
        for i in tv_categorias.get_children():
            tv_categorias.delete(i)
        return
    # Buscar el id del departamento por nombre
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None

    # Refrescar usuarios
    for i in tv_usuarios.get_children():
        tv_usuarios.delete(i)
    for u in obtener_usuarios(id_dep):
        tv_usuarios.insert('', END, values=(u[1]))

    # Refrescar categorías
    for i in tv_categorias.get_children():
        tv_categorias.delete(i)
    for c in obtener_categorias(id_dep):
        tv_categorias.insert('', END, values=(c[1]))
        
def refrescar_combos():
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    combo_usuario['values'] = [u[1] for u in obtener_usuarios(id_dep)]
    combo_categoria['values'] = [c[1] for c in obtener_categorias(id_dep)]

# Refrescar combos de usuario y categoría según el departamento seleccionado en el formulario de llamadas
def refrescar_combos_llamada(*args):
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    if not id_dep:
        combo_usuario['values'] = []
        combo_categoria['values'] = []
        combo_usuario.set('')
        combo_categoria.set('')
        return
    combo_usuario['values'] = [u[1] for u in obtener_usuarios(id_dep)]
    combo_categoria['values'] = [c[1] for c in obtener_categorias(id_dep)]
    combo_usuario.set('')
    combo_categoria.set('')

# Inicializar valores del combo de departamento en el formulario de llamadas
def refrescar_departamentos_llamada():
    combo_departamento_llamada['values'] = [d[1] for d in obtener_departamentos()]
    if combo_departamento_llamada.get() not in combo_departamento_llamada['values']:
        combo_departamento_llamada.set('')

# Modifica registrar_llamada para usar el departamento seleccionado en el formulario
def registrar_llamada():
    detalles = entry_detalles.get().strip()
    if not detalles:
        messagebox.showwarning("Atención", "Ingrese detalles de la falla.")
        return
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    if not id_dep:
        messagebox.showwarning("Atención", "Seleccione un departamento.")
        return
    usuario_nombre = combo_usuario.get()
    categoria_nombre = combo_categoria.get()
    id_usuario = next((u[0] for u in obtener_usuarios(id_dep) if u[1] == usuario_nombre), None)
    id_categoria = next((c[0] for c in obtener_categorias(id_dep) if c[1] == categoria_nombre), None)
    hora_llegada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT INTO llamadas (hora_llegada, detalles, id_usuario, id_categoria) VALUES (?, ?, ?, ?)',
        (hora_llegada, detalles, id_usuario, id_categoria)
    )
    db_conn.commit()
    entry_detalles.delete(0, END)
    combo_usuario.set('')
    combo_categoria.set('')
    refrescar_combos_llamada()
    refrescar_combos()
    refrescar_filtros()
    actualizar_tabla()

# Inicializar UI
def inicializar_ui():
    refrescar_departamentos()
    refrescar_departamentos_llamada()
    refrescar_filtros()
    refrescar_combos_llamada()
    actualizar_tabla()

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"

def refrescar_filtros():
    dep_nombre = combo_departamento_llamada.get()
    dep = next((d for d in obtener_departamentos() if d[1] == dep_nombre), None)
    id_dep = dep[0] if dep else None
    usuarios = ["Todos"] + [u[1] for u in obtener_usuarios(id_dep)]
    categorias = ["Todos"] + [c[1] for c in obtener_categorias(id_dep)]
    filtro_usuario['values'] = usuarios
    filtro_categoria['values'] = categorias
    filtro_usuario.set("Todos")
    filtro_categoria.set("Todos")


# Interfaz gráfica
app = Tk()
app.title("Pigmeus App -  Free")
app.geometry("1400x900")
app.configure(bg="#e9eff5")

style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#e9eff5")
style.configure("TNotebook.Tab", font=("Helvetica", 16, "bold"), padding=12)
style.configure("Treeview", rowheight=30, font=("Helvetica", 13))
style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
style.configure('TButton', font=('Helvetica', 14), padding=10)

notebook = ttk.Notebook(app)
notebook.pack(expand=True, fill='both', padx=20, pady=20)

# Vista Llamadas
frame_llamadas = Frame(notebook, bg="#e9eff5")
notebook.add(frame_llamadas, text="Llamadas")

# --- PRIMERO el formulario para registrar llamadas ---
frame_nueva = Frame(frame_llamadas, bg="#e9eff5")
frame_nueva.pack(fill='x', pady=10)

# Selector de departamento (nuevo, antes que todo)
Label(frame_nueva, text="Departamento:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=0)
combo_departamento_llamada = ttk.Combobox(frame_nueva, font=("Helvetica", 13), state="readonly")
combo_departamento_llamada.grid(row=0, column=1, padx=5)

Label(frame_nueva, text="Usuario:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=2)
combo_usuario = ttk.Combobox(frame_nueva, font=("Helvetica", 13), state="readonly")
combo_usuario.grid(row=0, column=3, padx=5)
Label(frame_nueva, text="Categoría:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=4)
combo_categoria = ttk.Combobox(frame_nueva, font=("Helvetica", 13), state="readonly")
combo_categoria.grid(row=0, column=5, padx=5)
Label(frame_nueva, text="Detalles:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=6)
entry_detalles = Entry(frame_nueva, width=30, font=("Helvetica", 13))
entry_detalles.grid(row=0, column=7, padx=5)
btn_registrar = Button(frame_nueva, text="Registrar Llamada", command=registrar_llamada, font=("Helvetica", 13))
btn_registrar.grid(row=0, column=8, padx=5)

# --- FILTROS arriba de la tabla ---
frame_filtros = Frame(frame_llamadas, bg="#e9eff5")
frame_filtros.pack(fill='x', padx=10, pady=(5, 0))

Label(frame_filtros, text="Filtrar Usuario:", font=("Helvetica", 13), bg="#e9eff5").pack(side=LEFT)
filtro_usuario = ttk.Combobox(frame_filtros, font=("Helvetica", 13), width=18, state="readonly")
filtro_usuario.pack(side=LEFT, padx=5)
Label(frame_filtros, text="Filtrar Categoría:", font=("Helvetica", 13), bg="#e9eff5").pack(side=LEFT)
filtro_categoria = ttk.Combobox(frame_filtros, font=("Helvetica", 13), width=18, state="readonly")
filtro_categoria.pack(side=LEFT, padx=5)
Button(frame_filtros, text="Limpiar Filtros", command=lambda: limpiar_filtros(), font=("Helvetica", 12)).pack(side=LEFT, padx=10)

# --- LUEGO la tabla de llamadas ---
tabla_llamadas = ttk.Treeview(
    frame_llamadas,
    columns=('Fecha', 'Fecha Cierre', 'Hora', 'Hora Cierre', 'Usuario', 'Categoría', 'Detalles', 'Estado'),
    show='headings'
)

# Encabezados (esto es lo que hace que se vean los nombres de las columnas)
tabla_llamadas.heading('Fecha', text='Fecha')
tabla_llamadas.heading('Fecha Cierre', text='Fecha Cierre')
tabla_llamadas.heading('Hora', text='Hora')
tabla_llamadas.heading('Hora Cierre', text='Hora Cierre')
tabla_llamadas.heading('Usuario', text='Usuario')
tabla_llamadas.heading('Categoría', text='Categoría')
tabla_llamadas.heading('Detalles', text='Detalles')
tabla_llamadas.heading('Estado', text='Estado')

# Ancho y alineación de columnas
tabla_llamadas.column('Fecha', width=70, anchor='center')
tabla_llamadas.column('Fecha Cierre', width=70, anchor='center')
tabla_llamadas.column('Hora', width=70, anchor='center')
tabla_llamadas.column('Hora Cierre', width=70, anchor='center')
tabla_llamadas.column('Usuario', width=120, anchor='center')
tabla_llamadas.column('Categoría', width=120, anchor='center')
tabla_llamadas.column('Detalles', width=500, anchor='w')
tabla_llamadas.column('Estado', width=100, anchor='center')

# Columna grande para "Detalles"
tabla_llamadas.column('Detalles', width=400, anchor='w')  # ‘w’ para alinear a la izquierda

tabla_llamadas.pack(expand=True, fill='both', padx=10, pady=10)

# --- DEBAJO los botones de editar y marcar atendida ---
frame_botones = Frame(frame_llamadas, bg="#e9eff5")
frame_botones.pack(fill='x', pady=5)
btn_editar_detalles = Button(frame_botones, text="Editar Detalles", command=editar_detalles,
                             font=("Helvetica", 13), bg="#2196F3", fg="white")  # Azul
btn_editar_detalles.pack(side=LEFT, padx=10)

btn_atendido = Button(frame_botones, text="Marcar Atendida", command=marcar_atendida,
                      font=("Helvetica", 13), bg="#4CAF50", fg="white")  # Verde
btn_atendido.pack(side=LEFT, padx=10)

btn_pendiente = Button(frame_botones, text="Marcar Pendiente", command=marcar_pendiente,
                       font=("Helvetica", 13), bg="#FFC107", fg="black")  # Amarillo
btn_pendiente.pack(side=LEFT, padx=10)


# Vista Gestión
frame_gestion = Frame(notebook, bg="#e9eff5")
notebook.add(frame_gestion, text="Gestión Usuarios/Categorías")

# --- Frame principal horizontal para los tres bloques ---
frame_horizontal = Frame(frame_gestion, bg="#e9eff5")
frame_horizontal.pack(fill='both', expand=True, padx=10, pady=10)

# --- Departamentos a la izquierda ---
lf_d = LabelFrame(frame_horizontal, text="Departamentos", font=("Helvetica", 14), bg="#e9eff5")
lf_d.pack(side=LEFT, fill='both', expand=True, padx=(0, 10), pady=0)

tv_departamentos = ttk.Treeview(lf_d, columns=('Nombre'), show='headings')
tv_departamentos.heading('Nombre', text='Nombre')
tv_departamentos.pack(expand=True, fill='both', pady=5)

entry_departamento = Entry(lf_d, font=("Helvetica", 13))
entry_departamento.pack(fill='x', pady=5)

btn_crear_d = Button(lf_d, text="Crear Departamento", command=crear_departamento, font=("Helvetica", 13))
btn_crear_d.pack(fill='x', pady=2)

btn_eliminar_d = Button(lf_d, text="Eliminar Departamento", command=eliminar_departamento_ui, font=("Helvetica", 13))
btn_eliminar_d.pack(fill='x', pady=2)

# --- Derecha: frame vertical para selector y usuarios/categorías ---
frame_derecha = Frame(frame_horizontal, bg="#e9eff5")
frame_derecha.pack(side=LEFT, fill='both', expand=True, padx=(0, 0), pady=0)

# Selector de departamento arriba
frame_selector = Frame(frame_derecha, bg="#e9eff5")
frame_selector.pack(fill='x', padx=10, pady=(10, 0))

Label(frame_selector, text="Departamento:", font=("Helvetica", 13), bg="#e9eff5").pack(side=LEFT)
combo_departamento_gestion = ttk.Combobox(frame_selector, font=("Helvetica", 13), state="readonly")
combo_departamento_gestion.pack(side=LEFT, padx=10)

# Usuarios y Categorías en horizontal debajo del selector
frame_usuarios_categorias = Frame(frame_derecha, bg="#e9eff5")
frame_usuarios_categorias.pack(fill='both', expand=True, padx=0, pady=(10, 0))

# Usuarios
lf_u = LabelFrame(frame_usuarios_categorias, text="Usuarios", font=("Helvetica", 14), bg="#e9eff5")
lf_u.pack(side=LEFT, fill='both', expand=True, padx=(0, 5), pady=0)

tv_usuarios = ttk.Treeview(lf_u, columns=('Nombre'), show='headings')
tv_usuarios.heading('Nombre', text='Nombre')
tv_usuarios.pack(expand=True, fill='both', pady=5)
entry_usuario = Entry(lf_u, font=("Helvetica", 13))
entry_usuario.pack(fill='x', pady=5)
btn_crear_u = Button(lf_u, text="Crear Usuario", command=crear_usuario, font=("Helvetica", 13))
btn_crear_u.pack(fill='x', pady=2)
btn_eliminar_u = Button(lf_u, text="Eliminar Usuario", command=eliminar_usuario_ui, font=("Helvetica", 13))
btn_eliminar_u.pack(fill='x', pady=2)

# Categorías
lf_c = LabelFrame(frame_usuarios_categorias, text="Categorías", font=("Helvetica", 14), bg="#e9eff5")
lf_c.pack(side=LEFT, fill='both', expand=True, padx=(5, 0), pady=0)

tv_categorias = ttk.Treeview(lf_c, columns=('Nombre'), show='headings')
tv_categorias.heading('Nombre', text='Nombre')
tv_categorias.pack(expand=True, fill='both', pady=5)
entry_categoria = Entry(lf_c, font=("Helvetica", 13))
entry_categoria.pack(fill='x', pady=5)
btn_crear_c = Button(lf_c, text="Crear Categoría", command=crear_categoria, font=("Helvetica", 13))
btn_crear_c.pack(fill='x', pady=2)
btn_eliminar_c = Button(lf_c, text="Eliminar Categoría", command=eliminar_categoria_ui, font=("Helvetica", 13))
btn_eliminar_c.pack(fill='x', pady=2)

# Vista Exportación
frame_extra = Frame(notebook, bg="#e9eff5")
notebook.add(frame_extra, text="Exportar a Excel")
Label(frame_extra, text="Exportar las llamadas registradas a Excel", font=("Helvetica", 18, "bold"), bg="#e9eff5").pack(pady=40)
Button(frame_extra, text="Exportar", command=exportar_excel, width=25, font=("Helvetica", 16), bg="#4CAF50", fg="white").pack(pady=30)

# Enlazar Enter en los campos del formulario
entry_detalles.bind("<Return>", lambda e: (combo_usuario.focus(), combo_usuario.event_generate('<Down>')))
combo_usuario.bind("<Return>", lambda e: (combo_categoria.focus(), combo_categoria.event_generate('<Down>')))
combo_categoria.bind("<Return>", lambda e: btn_registrar.invoke())

filtro_usuario.bind("<<ComboboxSelected>>", lambda e: actualizar_tabla())
filtro_categoria.bind("<<ComboboxSelected>>", lambda e: actualizar_tabla())

combo_departamento_gestion.bind("<<ComboboxSelected>>", refrescar_usuarios_y_categorias_por_departamento)
combo_departamento_llamada.bind("<<ComboboxSelected>>", lambda e: (
    refrescar_combos_llamada(),
    refrescar_combos(),
    refrescar_filtros(),
    actualizar_tabla()
))

inicializar_ui()

app.mainloop()
db_conn.close()
