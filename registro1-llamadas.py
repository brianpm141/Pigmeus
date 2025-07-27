import sqlite3
from datetime import datetime

conn = sqlite3.connect('llamadas.db')
cursor = conn.cursor()

# Crear tablas si no existen
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

# CRUD Usuarios
def crear_usuario(nombre):
    try:
        cursor.execute('INSERT INTO usuarios (nombre) VALUES (?)', (nombre,))
        conn.commit()
        print(f"Usuario '{nombre}' creado.")
    except sqlite3.IntegrityError:
        print("Este usuario ya existe.")

def ver_usuarios():
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    print("\nUsuarios registrados:")
    for usuario in usuarios:
        print(f"ID: {usuario[0]}, Nombre: {usuario[1]}")

def actualizar_usuario(id_usuario, nuevo_nombre):
    cursor.execute('UPDATE usuarios SET nombre = ? WHERE id = ?', (nuevo_nombre, id_usuario))
    conn.commit()
    print(f"Usuario ID {id_usuario} actualizado a '{nuevo_nombre}'.")

def eliminar_usuario(id_usuario):
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
    conn.commit()
    print(f"Usuario ID {id_usuario} eliminado.")

# CRUD Categorías
def crear_categoria(nombre):
    try:
        cursor.execute('INSERT INTO categorias (nombre) VALUES (?)', (nombre,))
        conn.commit()
        print(f"Categoría '{nombre}' creada.")
    except sqlite3.IntegrityError:
        print("Esta categoría ya existe.")

def ver_categorias():
    cursor.execute('SELECT * FROM categorias')
    categorias = cursor.fetchall()
    print("\nCategorías disponibles:")
    for cat in categorias:
        print(f"ID: {cat[0]}, Nombre: {cat[1]}")

def actualizar_categoria(id_categoria, nuevo_nombre):
    cursor.execute('UPDATE categorias SET nombre = ? WHERE id = ?', (nuevo_nombre, id_categoria))
    conn.commit()
    print(f"Categoría ID {id_categoria} actualizada a '{nuevo_nombre}'.")

def eliminar_categoria(id_categoria):
    cursor.execute('DELETE FROM categorias WHERE id = ?', (id_categoria,))
    conn.commit()
    print(f"Categoría ID {id_categoria} eliminada.")

# Funciones llamadas
def registrar_llamada(detalles, id_usuario, id_categoria):
    hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO llamadas (hora_llegada, detalles, id_usuario, id_categoria)
        VALUES (?, ?, ?, ?)''', (hora, detalles, id_usuario, id_categoria))
    conn.commit()
    print(f"Llamada registrada a las {hora}.")

def marcar_atendido(id_llamada):
    cursor.execute('UPDATE llamadas SET atendido = 1 WHERE id = ?', (id_llamada,))
    conn.commit()
    print(f"Llamada ID {id_llamada} marcada como atendida.")

def mostrar_llamadas():
    cursor.execute('''
    SELECT llamadas.id, llamadas.hora_llegada, llamadas.detalles,
           usuarios.nombre, categorias.nombre, llamadas.atendido
    FROM llamadas
    LEFT JOIN usuarios ON llamadas.id_usuario = usuarios.id
    LEFT JOIN categorias ON llamadas.id_categoria = categorias.id
    ''')
    llamadas = cursor.fetchall()
    print("\nRegistro de llamadas:")
    for llamada in llamadas:
        estado = 'Atendido' if llamada[5] else 'Pendiente'
        usuario = llamada[3] if llamada[3] else "No asignado"
        categoria = llamada[4] if llamada[4] else "No asignada"
        print(f"ID: {llamada[0]}, Hora: {llamada[1]}, Detalles: {llamada[2]}, "
              f"Atendió: {usuario}, Categoría: {categoria}, Estado: {estado}")

# Menú principal
def menu():
    while True:
        print("\n--- Menú principal ---")
        print("1. Registrar llamada")
        print("2. Marcar llamada como atendida")
        print("3. Mostrar llamadas")
        print("4. Gestionar usuarios")
        print("5. Gestionar categorías")
        print("6. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            detalles = input("Detalles de la falla: ")
            
            ver_usuarios()
            try:
                id_usuario = int(input("ID del usuario que atiende (0 si ninguno): "))
                id_usuario = id_usuario if id_usuario != 0 else None
            except ValueError:
                id_usuario = None

            ver_categorias()
            try:
                id_categoria = int(input("ID de la categoría (0 si ninguna): "))
                id_categoria = id_categoria if id_categoria != 0 else None
            except ValueError:
                id_categoria = None

            registrar_llamada(detalles, id_usuario, id_categoria)

        elif opcion == '2':
            mostrar_llamadas()
            id_llamada = int(input("ID de la llamada atendida: "))
            marcar_atendido(id_llamada)

        elif opcion == '3':
            mostrar_llamadas()

        elif opcion == '4':
            gestionar_usuarios()

        elif opcion == '5':
            gestionar_categorias()

        elif opcion == '6':
            break
        else:
            print("Opción no válida.")

# Submenú gestión usuarios
def gestionar_usuarios():
    while True:
        print("\n--- Gestión de Usuarios ---")
        print("1. Crear usuario")
        print("2. Ver usuarios")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("5. Volver al menú principal")

        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            nombre = input("Nombre del nuevo usuario: ")
            crear_usuario(nombre)
        elif opcion == '2':
            ver_usuarios()
        elif opcion == '3':
            ver_usuarios()
            id_usuario = int(input("ID del usuario a actualizar: "))
            nuevo_nombre = input("Nuevo nombre: ")
            actualizar_usuario(id_usuario, nuevo_nombre)
        elif opcion == '4':
            ver_usuarios()
            id_usuario = int(input("ID del usuario a eliminar: "))
            eliminar_usuario(id_usuario)
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")

# Submenú gestión categorías
def gestionar_categorias():
    while True:
        print("\n--- Gestión de Categorías ---")
        print("1. Crear categoría")
        print("2. Ver categorías")
        print("3. Actualizar categoría")
        print("4. Eliminar categoría")
        print("5. Volver al menú principal")

        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            nombre = input("Nombre de la nueva categoría: ")
            crear_categoria(nombre)
        elif opcion == '2':
            ver_categorias()
        elif opcion == '3':
            ver_categorias()
            id_categoria = int(input("ID de la categoría a actualizar: "))
            nuevo_nombre = input("Nuevo nombre: ")
            actualizar_categoria(id_categoria, nuevo_nombre)
        elif opcion == '4':
            ver_categorias()
            id_categoria = int(input("ID de la categoría a eliminar: "))
            eliminar_categoria(id_categoria)
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")

# Ejecución
if __name__ == "__main__":
    menu()
    conn.close()
