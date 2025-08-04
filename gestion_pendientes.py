# gestion_pendientes.py
import sqlite3
from datetime import datetime

db_conn = None
cursor = None

def set_connection(conn):
    global db_conn, cursor
    db_conn = conn
    cursor = db_conn.cursor()

def crear_pendiente(titulo, descripcion, id_usuario):
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO pendientes (titulo, descripcion, fecha_creacion, id_usuario)
        VALUES (?, ?, ?, ?)
    ''', (titulo, descripcion, fecha, id_usuario))
    db_conn.commit()

def obtener_pendientes(id_departamento=None, solo_pendientes=False):
    sql = '''
        SELECT p.id, p.titulo, p.descripcion, p.avance, p.completado,
               p.fecha_creacion, p.fecha_completado, u.nombre, u.id_departamento
        FROM pendientes p
        LEFT JOIN usuarios u ON p.id_usuario = u.id
    '''
    condiciones = []
    params = []

    if id_departamento:
        condiciones.append("u.id_departamento = ?")
        params.append(id_departamento)
    if solo_pendientes:
        condiciones.append("p.completado = 0")

    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY p.id DESC"
    cursor.execute(sql, params)
    return cursor.fetchall()

def actualizar_pendiente(id_pendiente, nuevo_titulo, nueva_desc):
    cursor.execute('''
        UPDATE pendientes SET titulo = ?, descripcion = ?
        WHERE id = ?
    ''', (nuevo_titulo, nueva_desc, id_pendiente))
    db_conn.commit()

def registrar_avance(id_pendiente, texto_avance):
    cursor.execute('''
        UPDATE pendientes SET avance = ?
        WHERE id = ?
    ''', (texto_avance, id_pendiente))
    db_conn.commit()

def marcar_completado(id_pendiente):
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE pendientes
        SET completado = 1, fecha_completado = ?
        WHERE id = ?
    ''', (fecha, id_pendiente))
    db_conn.commit()

def marcar_pendiente(id_pendiente):
    cursor.execute('''
        UPDATE pendientes
        SET completado = 0, fecha_completado = NULL
        WHERE id = ?
    ''', (id_pendiente,))
    db_conn.commit()

def eliminar_pendiente(id_pendiente):
    cursor.execute('DELETE FROM pendientes WHERE id = ?', (id_pendiente,))
    db_conn.commit()
