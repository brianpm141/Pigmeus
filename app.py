import sqlite3
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Inicializar base de datos y tablas
def init_db():
    conn = sqlite3.connect('llamadas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
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
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
            FOREIGN KEY(id_categoria) REFERENCES categorias(id)
        )
    ''')
    conn.commit()
    return conn, cursor

# Conexión global
db_conn, cursor = init_db()

# Funciones auxiliares para obtener datos
def obtener_usuarios():
    cursor.execute('SELECT id, nombre FROM usuarios')
    return cursor.fetchall()

def obtener_categorias():
    cursor.execute('SELECT id, nombre FROM categorias')
    return cursor.fetchall()

def obtener_llamadas():
    cursor.execute('''
        SELECT l.id, l.hora_llegada, l.detalles, u.nombre, c.nombre, l.atendido
        FROM llamadas l
        LEFT JOIN usuarios u ON l.id_usuario = u.id
        LEFT JOIN categorias c ON l.id_categoria = c.id
        ORDER BY l.id DESC
    ''')
    return cursor.fetchall()

# Funciones de exportación
def exportar_excel():
    datos = obtener_llamadas()
    filas = []
    for row in datos:
        _, hora_llegada, detalles, usuario, categoria, atendido = row
        fecha, hora = hora_llegada.split(" ") if hora_llegada else ("", "")
        filas.append({
            "Fecha": fecha,
            "Hora": hora,
            "Detalles": detalles,
            "Atendió": usuario or '',
            "Categoría": categoria or '',
            "Estado": "Atendido" if atendido else "Pendiente"
        })
    df = pd.DataFrame(filas)
    file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file:
        df.to_excel(file, index=False)
        messagebox.showinfo("Exportado", f"Archivo guardado como\n{file}")

# Funciones de operación de llamadas
def registrar_llamada():
    detalles = entry_detalles.get().strip()
    if not detalles:
        messagebox.showwarning("Atención", "Ingrese detalles de la falla.")
        return
    usuario_nombre = combo_usuario.get()
    categoria_nombre = combo_categoria.get()
    id_usuario = next((u[0] for u in obtener_usuarios() if u[1] == usuario_nombre), None)
    id_categoria = next((c[0] for c in obtener_categorias() if c[1] == categoria_nombre), None)
    hora_llegada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT INTO llamadas (hora_llegada, detalles, id_usuario, id_categoria) VALUES (?, ?, ?, ?)',
        (hora_llegada, detalles, id_usuario, id_categoria)
    )
    db_conn.commit()
    entry_detalles.delete(0, END)
    refrescar_combos()
    actualizar_tabla()

def marcar_atendida():
    sel = tabla_llamadas.focus()
    if not sel:
        return
    vals = tabla_llamadas.item(sel)['values']
    id_llamada = vals[0]
    cursor.execute('UPDATE llamadas SET atendido = 1 WHERE id = ?', (id_llamada,))
    db_conn.commit()
    actualizar_tabla()

def actualizar_tabla():
    for item in tabla_llamadas.get_children():
        tabla_llamadas.delete(item)
    for llamada in obtener_llamadas():
        id_llamada, hora_llegada, detalles, usuario, categoria, atendido_flag = llamada
        fecha, hora = ('-', '-')
        if hora_llegada:
            parts = hora_llegada.split(' ')
            fecha = parts[0]
            hora = parts[1] if len(parts) > 1 else ''
        estado_texto = 'Atendido' if atendido_flag else 'Pendiente'
        tabla_llamadas.insert('', END, values=(
            id_llamada, fecha, hora, detalles, usuario or '-', categoria or '-', estado_texto
        ))

# CRUD Usuarios
def crear_usuario():
    nombre = entry_usuario.get().strip()
    if not nombre:
        return
    try:
        cursor.execute('INSERT INTO usuarios (nombre) VALUES (?)', (nombre,))
        db_conn.commit()
        entry_usuario.delete(0, END)
        refrescar_usuarios()
        refrescar_combos()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Usuario ya existe.")

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

def refrescar_usuarios():
    for i in tv_usuarios.get_children():
        tv_usuarios.delete(i)
    for u in obtener_usuarios():
        tv_usuarios.insert('', END, values=(u[0], u[1]))

# CRUD Categorías
def crear_categoria():
    nombre = entry_categoria.get().strip()
    if not nombre:
        return
    try:
        cursor.execute('INSERT INTO categorias (nombre) VALUES (?)', (nombre,))
        db_conn.commit()
        entry_categoria.delete(0, END)
        refrescar_categorias()
        refrescar_combos()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Categoría ya existe.")

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

def refrescar_categorias():
    for i in tv_categorias.get_children():
        tv_categorias.delete(i)
    for c in obtener_categorias():
        tv_categorias.insert('', END, values=(c[0], c[1]))

def refrescar_combos():
    combo_usuario['values'] = [u[1] for u in obtener_usuarios()]
    combo_categoria['values'] = [c[1] for c in obtener_categorias()]

# Interfaz gráfica
app = Tk()
app.title("Gestor de Llamadas")
app.geometry("1200x720")
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

tabla_llamadas = ttk.Treeview(
    frame_llamadas,
    columns=('ID', 'Fecha', 'Hora', 'Detalles', 'Usuario', 'Categoría', 'Estado'),
    show='headings'
)
tabla_llamadas.column('ID', width=0, stretch=False)
for col in ('Fecha', 'Hora', 'Detalles', 'Usuario', 'Categoría', 'Estado'):
    tabla_llamadas.heading(col, text=col)
    tabla_llamadas.column(col, width=160)
tabla_llamadas.pack(expand=True, fill='both', padx=10, pady=10)

btn_atendido = Button(frame_llamadas, text="Marcar Atendida", command=marcar_atendida, font=("Helvetica", 13))
btn_atendido.pack(pady=5)

frame_nueva = Frame(frame_llamadas, bg="#e9eff5")
frame_nueva.pack(fill='x', pady=10)
Label(frame_nueva, text="Detalles:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=0)
entry_detalles = Entry(frame_nueva, width=30, font=("Helvetica", 13))
entry_detalles.grid(row=0, column=1, padx=5)
Label(frame_nueva, text="Usuario:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=2)
combo_usuario = ttk.Combobox(frame_nueva, font=("Helvetica", 13))
combo_usuario.grid(row=0, column=3, padx=5)
Label(frame_nueva, text="Categoría:", font=("Helvetica", 13), bg="#e9eff5").grid(row=0, column=4)
combo_categoria = ttk.Combobox(frame_nueva, font=("Helvetica", 13))
combo_categoria.grid(row=0, column=5, padx=5)
btn_registrar = Button(frame_nueva, text="Registrar Llamada", command=registrar_llamada, font=("Helvetica", 13))
btn_registrar.grid(row=0, column=6, padx=5)

# Vista Gestión
frame_gestion = Frame(notebook, bg="#e9eff5")
notebook.add(frame_gestion, text="Gestión Usuarios/Categorías")

lf_u = LabelFrame(frame_gestion, text="Usuarios", font=("Helvetica", 14), bg="#e9eff5")
lf_u.pack(side=LEFT, fill='both', expand=True, padx=10, pady=10)

tv_usuarios = ttk.Treeview(lf_u, columns=('ID', 'Nombre'), show='headings')
tv_usuarios.heading('ID', text='ID')
tv_usuarios.heading('Nombre', text='Nombre')
tv_usuarios.pack(expand=True, fill='both', pady=5)
entry_usuario = Entry(lf_u, font=("Helvetica", 13))
entry_usuario.pack(fill='x', pady=5)
btn_crear_u = Button(lf_u, text="Crear Usuario", command=crear_usuario, font=("Helvetica", 13))
btn_crear_u.pack(fill='x', pady=2)
btn_eliminar_u = Button(lf_u, text="Eliminar Usuario", command=eliminar_usuario_ui, font=("Helvetica", 13))
btn_eliminar_u.pack(fill='x', pady=2)

lf_c = LabelFrame(frame_gestion, text="Categorías", font=("Helvetica", 14), bg="#e9eff5")
lf_c.pack(side=RIGHT, fill='both', expand=True, padx=10, pady=10)

tv_categorias = ttk.Treeview(lf_c, columns=('ID', 'Nombre'), show='headings')
tv_categorias.heading('ID', text='ID')
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

# Inicializar UI
def inicializar_ui():
    refrescar_usuarios()
    refrescar_categorias()
    refrescar_combos()
    actualizar_tabla()

inicializar_ui()
app.mainloop()
db_conn.close()
