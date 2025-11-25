import flet as ft
import views.styles as styles

class DepartmentsView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.spacing = 20
        self.controls = self._build_view()

    def _build_view(self):

        #--------------- Barra de botones-----------
        toolbar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # Grupo Izquierdo: Crear y Modificar
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.ElevatedButton(
                            "Crear Departamento",
                            bgcolor=styles.PRIMARY_BLUE,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=20, vertical=12)
                            ),
                            on_click=lambda e: print("Crear click"),
                        ),
                        ft.ElevatedButton(
                            "Modificar Departamento",
                            bgcolor=ft.Colors.GREY_200,
                            color=styles.TEXT_COLOR,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                overlay_color=ft.Colors.GREY_300,
                            ),
                            on_click=lambda e: print("Modificar click"),
                        ),
                    ]
                ),
                # Grupo Derecho: Eliminar
                ft.TextButton(
                    "Eliminar Departamento",
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_600,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED_600,
                        overlay_color=ft.Colors.RED_50,
                        padding=ft.padding.symmetric(horizontal=15, vertical=10)
                    ),
                     on_click=lambda e: print("Eliminar click"),
                )
            ]
        )

        # --- 3. Tabla de Datos ---
        
        # Datos Mock
        departments_data = [
            {"nombre": "Ingeniería", "encargado": "Ana Torres", "usuarios": 15},
            {"nombre": "Recursos Humanos", "encargado": "Carlos Vega", "usuarios": 5},
            {"nombre": "Marketing", "encargado": "Sofía Reyes", "usuarios": 8},
            {"nombre": "Ventas", "encargado": "Luis Morales", "usuarios": 12},
        ]

        # Construcción de filas
        rows = []
        for dept in departments_data:
            rows.append(
                ft.DataRow(
                    cells=[
                        # Celda 1: Nombre (W_500 como en Actividades)
                        ft.DataCell(ft.Text(dept["nombre"], weight=ft.FontWeight.W_500, color=styles.TEXT_COLOR)),
                        # Celda 2: Encargado
                        ft.DataCell(ft.Text(dept["encargado"], color=styles.TEXT_COLOR)),
                        # Celda 3: Usuarios
                        ft.DataCell(ft.Text(str(dept["usuarios"]), color=styles.TEXT_COLOR)),
                    ],
                )
            )

        # Contenedor limpio (Estilo Actividades)
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
                    ft.DataColumn(ft.Text("NOMBRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("ENCARGADO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("NÚMERO DE USUARIOS", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows
            )
        )

        return [
            toolbar,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            table_container
        ]