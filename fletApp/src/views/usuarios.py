import flet as ft
import views.styles as styles
from views.pops.usuario import UserForm

# 1. CAMBIO: Heredar de ft.Container
class UsersView(ft.Container): 
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30) # El padding ahora lo aplica el contenedor
        # 2. CAMBIO: El contenido es una Columna con scroll
        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            controls=self._build_view()
        )

    def _open_user_modal(self, e):
        form = UserForm(e.page)
        form.open_dialog()

    def _build_view(self):

        # --- Barra de Herramientas ---
        toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Crear Usuario",
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12)
                    ),
                    on_click=lambda e: self._open_user_modal(e),
                ),
                ft.ElevatedButton(
                    "Modificar Usuario",
                    bgcolor=ft.Colors.GREY_200,
                    color=styles.TEXT_COLOR,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        overlay_color=ft.Colors.GREY_300,
                    ),
                    on_click=lambda e: self._open_user_modal(e),
                ),
                ft.TextButton(
                    "Eliminar Usuario",
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_600,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED_600,
                        overlay_color=ft.Colors.RED_50,
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                     on_click=lambda e: print("Eliminar Usuario click"),
                )
            ]
        )

        users_data = [
            {"usuario": "ana.torres", "departamento": "Ingeniería"},
            {"usuario": "carlos.vega", "departamento": "Recursos Humanos"},
            {"usuario": "sofia.reyes", "departamento": "Marketing"},
            {"usuario": "luis.morales", "departamento": "Ventas"},
        ]

        rows = []
        for user in users_data:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(user["usuario"], weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                        ft.DataCell(ft.Text(user["departamento"], color=styles.TEXT_COLOR)),
                    ],
                )
            )

        table_container = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.all(5),
            content=ft.DataTable(
                width=float("inf"),
                heading_row_height=60,
                data_row_min_height=60,
                column_spacing=20,
                columns=[
                    ft.DataColumn(ft.Text("NOMBRE DE USUARIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("DEPARTAMENTO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows
            )
        )

        # 3. CAMBIO: Retornamos la lista de controles, que será usada por la Columna en el __init__
        return [
            toolbar,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            table_container
        ]