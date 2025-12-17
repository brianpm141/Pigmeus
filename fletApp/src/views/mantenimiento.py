import flet as ft
import views.styles as styles

class MaintenanceView(ft.Container):
    def __init__(self, current_user=None):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.current_user = current_user
        
        self.content = ft.Column(
            controls=[
                ft.Text("Mantenimiento", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=80, color=styles.BTN_MODIFY_BG),
                            ft.Text("Mantenimiento del Sistema", size=30, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                            ft.Text("Opciones avanzadas de configuración y mantenimiento.", color=ft.Colors.GREY_500, size=16),
                            ft.Text("(Solo Administradores)", color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD),
                             ft.Text("(En construcción)", color=ft.Colors.GREY_400, italic=True)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
        )
