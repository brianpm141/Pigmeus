from tkinter import *
from db import init_db
from views.menu import construir_menu_general
import gestion_roles as roles
import gestion_actividades as actividades
import gestion_pendientes as pendientes

# Inicializar base de datos y pasar conexión a los módulos
db_conn = init_db()
roles.set_connection(db_conn)
actividades.set_connection(db_conn)
pendientes.set_connection(db_conn)

# Crear ventana principal
app = Tk()
app.title("Pigmeus App")
app.geometry("1280x720")

# Cargar menú general (con navegación entre vistas)
construir_menu_general(app)

# Ejecutar app
app.mainloop()
db_conn.close()
