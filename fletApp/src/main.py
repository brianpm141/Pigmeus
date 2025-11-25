import flet as ft
import views.styles as styles
from views.sidebar import Sidebar

def main(page: ft.Page):
    page.title = "Pigmeus Teams"
    styles.apply_theme(page)

    # --------------------Contenido ---------------------
    content_area = ft.Container(
        expand=True,
        bgcolor=styles.BG_COLOR,
        alignment=ft.alignment.center,
    )

    #---------------------Navegacion---------------------
    def navigate_to(view_name):
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

    # Cargar la vista inicial por defecto
    navigate_to("Actividades")

if __name__ == "__main__":
    ft.app(target=main)