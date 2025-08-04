# db.py
import sqlite3

def init_db(nombre_db='llamadas.db'):
    conn = sqlite3.connect(nombre_db)
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pendientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    avance TEXT,
    completado INTEGER DEFAULT 0,
    fecha_creacion TEXT,
    fecha_completado TEXT,
    id_usuario INTEGER,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
);

    ''')
    conn.commit()
    return conn
