# gestion_roles.py
import sqlite3
from tkinter import messagebox

# Conexión global (debe recibirse desde el archivo principal)
db_conn = None
cursor = None

def set_connection(conn):
    global db_conn, cursor
    db_conn = conn
    cursor = db_conn.cursor()

# Departamentos
def obtener_departamentos():
    cursor.execute('SELECT id, nombre FROM departamentos')
    return cursor.fetchall()

def crear_departamento(nombre):
    try:
        cursor.execute('INSERT INTO departamentos (nombre) VALUES (?)', (nombre,))
        db_conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Departamento ya existe.")
        return False

def eliminar_departamento(id_d):
    cursor.execute('DELETE FROM departamentos WHERE id = ?', (id_d,))
    db_conn.commit()

# Usuarios
def obtener_usuarios(id_departamento=None):
    if id_departamento:
        cursor.execute('SELECT id, nombre FROM usuarios WHERE id_departamento = ?', (id_departamento,))
    else:
        cursor.execute('SELECT id, nombre FROM usuarios')
    return cursor.fetchall()

def crear_usuario(nombre, id_dep):
    try:
        cursor.execute('INSERT INTO usuarios (nombre, id_departamento) VALUES (?, ?)', (nombre, id_dep))
        db_conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Usuario ya existe en este departamento.")
        return False

def eliminar_usuario(id_u):
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_u,))
    db_conn.commit()

# Categorías
def obtener_categorias(id_departamento=None):
    if id_departamento:
        cursor.execute('SELECT id, nombre FROM categorias WHERE id_departamento = ?', (id_departamento,))
    else:
        cursor.execute('SELECT id, nombre FROM categorias')
    return cursor.fetchall()

def crear_categoria(nombre, id_dep):
    try:
        cursor.execute('INSERT INTO categorias (nombre, id_departamento) VALUES (?, ?)', (nombre, id_dep))
        db_conn.commit()
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Categoría ya existe en este departamento.")
        return False

def eliminar_categoria(id_c):
    cursor.execute('DELETE FROM categorias WHERE id = ?', (id_c,))
    db_conn.commit()
