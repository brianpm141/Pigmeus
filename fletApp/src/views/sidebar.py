import flet as ft
import views.styles as styles

class Sidebar(ft.Container):
    # on_nav_change
    def __init__(self, on_nav_change):
        super().__init__()
        self.on_nav_change = on_nav_change 
        self.width = 250
        self.bgcolor = styles.SIDEBAR_BG
        self.padding = ft.padding.all(20)
        self.border = ft.border.only(
            right=ft.BorderSide(width=1, color=ft.Colors.GREY_200)
        )
        self.content = self._build_content()

    def _build_item(self, icon, text, is_selected=False):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        name=icon,
                        color=ft.Colors.WHITE if is_selected else styles.TEXT_COLOR,
                        size=20
                    ),
                    ft.Text(
                        value=text,
                        color=ft.Colors.WHITE if is_selected else styles.TEXT_COLOR,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=ft.border_radius.all(10),
            bgcolor=styles.PRIMARY_BLUE if is_selected else ft.Colors.TRANSPARENT,
            ink=True,
            # AQUÍ ESTÁ LA MAGIA: Llamamos a la función que nos pasó el main
            on_click=lambda e: self.on_nav_change(text)
        )

    def _build_content(self):
        return ft.Column(
            controls=[
                # Logo
                ft.Row(
                    [
                        ft.Image(
                            src = "img/pigmeus.png",
                            width=30,
                            height=30,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Text("Pigmeus App", size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                    ],
                    spacing=10,
                ),
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),

                # Menú
                # Nota: Por ahora la selección visual (azul) es estática en "Actividades"
                # Luego podemos hacer lógica para cambiar el color del botón activo
                self._build_item(ft.Icons.CHECKLIST_RTL_ROUNDED, "Actividades", is_selected=True),
                self._build_item(ft.Icons.LAYERS_OUTLINED, "Pisos y Áreas"),
                self._build_item(ft.Icons.ASSIGNMENT_OUTLINED, "Pendientes"),
            ],
            spacing=5,
        )