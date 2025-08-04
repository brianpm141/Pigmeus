# gestion_actividades.py
import sqlite3
from datetime import datetime

db_conn = None
cursor = None

def set_connection(conn):
    global db_conn, cursor
    db_conn = conn
    cursor = db_conn.cursor()

def registrar_actividad(detalles, id_usuario, id_categoria):
    hora_llegada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        'INSERT INTO llamadas (hora_llegada, detalles, id_usuario, id_categoria) VALUES (?, ?, ?, ?)',
        (hora_llegada, detalles, id_usuario, id_categoria)
    )
    db_conn.commit()

def obtener_actividades(dep_id=None, filtro_usuario=None, filtro_categoria=None):
    sql = """
        SELECT l.id, l.hora_llegada, l.detalles,
               u.nombre, c.nombre, l.atendido, l.hora_cierre
        FROM llamadas l
        LEFT JOIN usuarios u ON l.id_usuario   = u.id
        LEFT JOIN categorias c ON l.id_categoria = c.id
    """
    params = []
    condiciones = []
    if dep_id:
        condiciones.append("c.id_departamento = ?")
        params.append(dep_id)
    if filtro_usuario:
        condiciones.append("u.nombre = ?")
        params.append(filtro_usuario)
    if filtro_categoria:
        condiciones.append("c.nombre = ?")
        params.append(filtro_categoria)
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY l.id DESC"
    cursor.execute(sql, params)
    return cursor.fetchall()


def marcar_completada(id_actividad):
    hora_cierre = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE llamadas SET atendido = 1, hora_cierre = ? WHERE id = ?', (hora_cierre, id_actividad))
    db_conn.commit()

def marcar_pendiente(id_actividad):
    cursor.execute('UPDATE llamadas SET atendido = 0, hora_cierre = NULL WHERE id = ?', (id_actividad,))
    db_conn.commit()


def actualizar_detalles(id_llamada, nuevos_detalles):
    sql = "UPDATE llamadas SET detalles = ? WHERE id = ?"
    cursor.execute(sql, (nuevos_detalles, id_llamada))
    db_conn.commit()
