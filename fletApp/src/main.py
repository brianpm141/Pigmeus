import flet as ft
import time
import views.styles as styles
from views.sidebar import Sidebar
from views.actividades import ActividadesView
from views.departamentos import DepartmentsView
from views.usuarios import UsersView
from views.categorias import CategoriesView
from views.loading import LoadingView

from db.database import init_db, verify_connection

def main(page: ft.Page):
    page.title = "Pigmeus Teams"
    styles.apply_theme(page)

    # Definir la interfaz principal (lógica de navegación)
    def load_main_interface():
        # --------------------Contenido ---------------------
        content_area = ft.Container(
            expand=True,
            bgcolor=styles.BG_COLOR,
            alignment=ft.alignment.center,
        )

        #---------------------Navegacion---------------------
        def navigate_to(view_name):
            content_area.content = None 
            
            if view_name == "Actividades":
                content_area.content = ActividadesView()
            elif view_name == "Departamentos":
                content_area.content = DepartmentsView()
            elif view_name == "Usuarios":
                content_area.content = UsersView()
            elif view_name == "Categorias":
                content_area.content = CategoriesView()
            else:
                content_area.content = ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE_OUTLINED, size=80, color=styles.PRIMARY_BLUE),
                        ft.Text(
                            value=view_name, 
                            size=40, 
                            weight=ft.FontWeight.BOLD, 
                            color=styles.TEXT_COLOR
                        ),
                        ft.Text("Vista en construcción...", color=ft.Colors.GREY_500, size=16),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            page.update()

        #---------------------Sidebar---------------------
        sidebar = Sidebar(on_nav_change=navigate_to)

        layout = ft.Row(
            controls=[sidebar, content_area],
            expand=True,
            spacing=0,
        )

        page.add(layout)
        navigate_to("Actividades")

    # Función para intentar conectar
    def try_connect_and_start(e=None):
        page.clean()
        
        # Mostrar carga
        loading = LoadingView()
        page.add(loading)
        page.update()

        print("Iniciando intento de conexión...")
        try:
            # UX Delay inicial (Simulando conexión)
            time.sleep(1.0) 
            
            # Verificar
            verify_connection()
            print("Base de datos conectada correctamente")
            
            # Inicializar
            init_db()
            print("Base de datos inicializada correctamente")
            
            # --- Transición Exitosa ---
            # 1. Cambiar mensaje a "Cargando..."
            loading.msg.value = "Cargando..."
            page.update()
            
            # 2. Mantener mensaje por 1.5 segundos (Solicitado por usuario)
            time.sleep(1.5)
            
            # 3. Fade out
            loading.opacity = 0
            page.update()
            
            # 4. Esperar animación (0.5s porque animate_opacity=500)
            time.sleep(0.5)
            
            # Limpiar y cargar app
            page.clean()
            load_main_interface()
            
        except Exception as ex:
            print(f"Error al iniciar la base de datos: {ex}")
            page.remove(loading)
            
            error_view = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=60, color="red"),
                    ft.Text("Error de Conexión", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("No se pudo conectar a la base de datos.", size=16),
                    ft.Container(height=10),
                    ft.Text(f"Detalles: {ex}", size=12, color="red", selectable=True),
                    ft.Container(height=20),
                    ft.ElevatedButton("Reintentar", on_click=try_connect_and_start),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
            page.add(ft.Container(content=error_view, alignment=ft.alignment.center, expand=True))
            page.update()

    # Manejador de teclado global
    def handle_keyboard_event(e: ft.KeyboardEvent):
        if e.key == "Escape":
            if page.overlay:
                page.close(page.overlay[-1])
            elif page.dialog:
                page.close(page.dialog)

    page.on_keyboard_event = handle_keyboard_event

    # Iniciar flujo
    try_connect_and_start()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
