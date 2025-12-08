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

    # --- Root Layout Architecture ---
    # Usamos un AnimatedSwitcher en la raíz para transiciones suaves entre
    # Pantalla de Carga -> Login -> App Principal
    
    root_switcher = ft.AnimatedSwitcher(
        content=ft.Container(bgcolor=styles.BG_COLOR),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=500,
        reverse_duration=500,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )
    
    def set_root_content(content):
        root_switcher.content = content
        root_switcher.update()

    page.add(
        ft.Container(
            content=root_switcher,
            expand=True,
            bgcolor=styles.BG_COLOR,
            alignment=ft.alignment.center
        )
    )

    # Definir la interfaz principal (lógica de navegación)
    def load_main_interface():
        # --------------------Contenido ---------------------
        # Switcher interno para vistas de la App (Departamentos, Usuarios, etc.)
        app_content_switcher = ft.AnimatedSwitcher(
            content=ft.Container(bgcolor=styles.BG_COLOR), 
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300, 
            reverse_duration=200,
        )

        content_area = ft.Container(
            content=app_content_switcher,
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
            
            app_content_switcher.content = new_content
            app_content_switcher.update()

        #---------------------Sidebar---------------------
        sidebar = Sidebar(on_nav_change=navigate_to)

        layout = ft.Row(
            controls=[sidebar, content_area],
            expand=True,
            spacing=0,
        )

        set_root_content(layout)
        
        # Iniciar en Actividades por defecto
        # Pequeño delay para que el layout se monte antes de cargar la vista
        # (Aunque en Flet síncrono no es estrictamente necesario, ayuda a la fluidez visual)
        navigate_to("Actividades")

    # Función para cargar opciones de Login
    def load_login_interface():
        def on_guest_enter(selected_dept):
            if selected_dept:
                print(f"Entrando como invitado: {selected_dept.nombre}")
            
            # --- Transición Final (Cargando...) ---
            # Mostrar "Cargando..." brevemente antes de entrar
            loading_transition = LoadingView(message=f"Iniciando en {selected_dept.nombre}...")
            set_root_content(loading_transition)
            
            # Trigger animation
            loading_transition.animate_in()
            
            # Simular carga
            page.update()
            time.sleep(1.5)
            load_main_interface()

        login_view = LoginOptionsView(on_app_start=on_guest_enter)
        set_root_content(login_view)

    # Función para intentar conectar
    def try_connect_and_start(e=None):
        # 1. Mostrar "Conectando..."
        loading = LoadingView(message="Conectando a la base de datos...")
        set_root_content(loading)
        
        # Pequeño hack para dar tiempo a renderizar la vista de carga antes de bloquear con DB
        page.update()
        time.sleep(0.5)
        
        loading.animate_in()

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
            
            # --- Transición a Login ---
            load_login_interface()
            
        except Exception as ex:
            print(f"Error al iniciar la base de datos: {ex}")
            
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
            set_root_content(ft.Container(content=error_view, alignment=ft.alignment.center))

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
