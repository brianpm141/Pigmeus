import flet as ft
import views.styles as styles
from controllers.departamentos_controller import get_all_departments

class LoginOptionsView(ft.Container):
    def __init__(self, on_app_start):
        super().__init__()
        self.expand = True
        self.bgcolor = styles.BG_COLOR
        self.alignment = ft.alignment.center
        self.on_app_start = on_app_start # Callback para iniciar la app (guest mode)

        self.logo = ft.Image(
            src="img/pigmeus.png",
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
        )

        # --- VISTAS ---
        self.main_options = self._build_main_options()
        self.login_form = self._build_login_form()
        self.guest_selection = self._build_guest_selection()

        # Contenedor dinámico
        self.current_content = ft.Container(content=self.main_options, animate_opacity=300)

        self.content = ft.Column(
            controls=[
                self.logo,
                ft.Container(height=20),
                self.current_content
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

    def _build_main_options(self):
        return ft.Column(
            controls=[
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    icon=ft.Icons.LOGIN,
                    style=ft.ButtonStyle(
                        bgcolor=styles.PRIMARY_BLUE,
                        color="white",
                        padding=20,
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    width=250,
                    on_click=lambda _: self._switch_view(self.login_form)
                ),
                ft.Text("o", size=14, color=ft.Colors.GREY_500),
                ft.OutlinedButton(
                    "Ingresar sin cuenta",
                    icon=ft.Icons.PERSON_OUTLINE,
                    style=ft.ButtonStyle(
                        color=styles.PRIMARY_BLUE,
                        padding=20,
                         text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    width=250,
                    on_click=self._load_departments_and_show
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

    def _build_login_form(self):
        return ft.Column(
            controls=[
                ft.TextField(label="Usuario", width=250, border_radius=8),
                ft.TextField(label="Contraseña", width=250, password=True, can_reveal_password=True, border_radius=8),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Ingresar",
                    width=250,
                    style=ft.ButtonStyle(bgcolor=styles.PRIMARY_BLUE, color="white"),
                    # Sin función por ahora
                ),
                ft.TextButton("Regresar", on_click=lambda _: self._switch_view(self.main_options))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

    def _build_guest_selection(self):
        # Este contenedor se llenará dinámicamente
        self.dept_list = ft.ListView(expand=False, height=200, spacing=10, padding=10)
        
        return ft.Column(
            controls=[
                ft.Text("Selecciona tu Departamento", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.dept_list,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    width=300,
                    height=250,
                    bgcolor="white",
                    padding=5
                ),
                ft.TextButton("Regresar", on_click=lambda _: self._switch_view(self.main_options))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

    def _switch_view(self, new_content):
        self.current_content.content = new_content
        self.update()

    def _load_departments_and_show(self, e):
        # Cargar departamentos de la BD
        depts = get_all_departments()
        self.dept_list.controls.clear()
        
        if not depts:
             self.dept_list.controls.append(ft.Text("No hay departamentos disponibles.", color="red"))
        else:
            for dept in depts:
                self.dept_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(dept.nombre, weight=ft.FontWeight.W_500),
                        leading=ft.Icon(ft.Icons.BUSINESS, color=styles.PRIMARY_BLUE),
                        on_click=lambda _, d=dept: self.on_app_start(d)
                    )
                )
        
        self._switch_view(self.guest_selection)
