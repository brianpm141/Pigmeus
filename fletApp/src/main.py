import flet as ft
import time
import views.styles as styles
from views.sidebar import Sidebar
from views.actividades import ActividadesView
from views.departamentos import DepartmentsView
from views.usuarios import UsersView
from views.usuarios import UsersView
from views.categorias import CategoriesView
from views.loading import LoadingView
from views.login_options import LoginOptionsView
from db.seed import seed_data 

from db.database import init_db, verify_connection

def main(page: ft.Page):
    page.title = "Pigmeus Teams"
    styles.apply_theme(page)

    # Definir la interfaz principal (lógica de navegación)
    def load_main_interface():
        # --------------------Contenido ---------------------
        # Usamos AnimatedSwitcher para transiciones suaves
        switcher = ft.AnimatedSwitcher(
            content=ft.Container(bgcolor=styles.BG_COLOR), # Contenido inicial (placeholder)
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300, # 300ms
            reverse_duration=200,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
        )

        content_area = ft.Container(
            content=switcher,
            expand=True,
            bgcolor=styles.BG_COLOR,
            alignment=ft.alignment.center,
        )

        #---------------------Navegacion---------------------
        def navigate_to(view_name):
            new_content = None
            
            if view_name == "Actividades":
                new_content = ActividadesView()
            elif view_name == "Departamentos":
                new_content = DepartmentsView()
            elif view_name == "Usuarios":
                new_content = UsersView()
            elif view_name == "Categorias":
                new_content = CategoriesView()
            else:
                new_content = ft.Column(
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
            
            # Flet AnimatedSwitcher requiere que el control sea distinto o tenga key distinto
            # Las vistas son instancias nuevas así que funcionará.
            switcher.content = new_content
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

    # Función para cargar opciones de Login
    def load_login_interface():
        def on_guest_enter(selected_dept):
            if selected_dept:
                print(f"Entrando como invitado: {selected_dept.nombre}")
            else:
                 print("Entrando como invitado (Sin departamento seleccionado)")
            
            # --- Transición Final (Cargando...) ---
            # 1. Limpiar Login
            page.clean()
            
            # 2. Mostrar "Cargando..."
            loading = LoadingView(message="Cargando...")
            page.add(loading)
            page.update()
            
            # 3. Esperar 1.5 seg
            time.sleep(1.5)
            
            # 4. Fade out
            loading.opacity = 0
            page.update()
            time.sleep(0.5)
            
            # 5. Cargar App Principal
            page.clean()
            load_main_interface()

        login_view = LoginOptionsView(on_app_start=on_guest_enter)
        page.add(login_view)
        page.update()

    # Función para intentar conectar
    def try_connect_and_start(e=None):
        page.clean()
        
        # 1. Mostrar "Conectando..."
        loading = LoadingView(message="Conectando a la base de datos...")
        page.add(loading)
        page.update()

        print("Iniciando intento de conexión...")
        try:
            # UX Delay inicial 
            time.sleep(1.0) 
            
            # Verificar
            verify_connection()
            print("Base de datos conectada correctamente")
            
            # Inicializar
            init_db()
            print("Base de datos inicializada correctamente")
            
            # Seed de datos (si aplica)
            seed_data()
            
            # --- Transición Final (Cargando...) ---
            page.clean()
            load_login_interface()
            
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
