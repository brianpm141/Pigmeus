import flet as ft
import views.styles as styles

class ActivitiesView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.content = self._build_view()

    def _build_status_badge(self, status, bg_color, txt_color):
        return ft.Container(
            content=ft.Text(status, color=txt_color, size=12, weight=ft.FontWeight.W_500),
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15),
            alignment=ft.alignment.center
        )

    def _build_view(self):
        # Datos de ejemplo
        rows_data = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Juan Pérez", weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text("Reunión")),
                    ft.DataCell(ft.Text("Revisión de proyecto trimestral.")),
                    ft.DataCell(self._build_status_badge("Completada", styles.STATUS_GREEN_BG, styles.STATUS_GREEN_TXT)),
                    ft.DataCell(ft.Text("2023-10-26")),
                    ft.DataCell(ft.Text("09:00")),
                    ft.DataCell(ft.Text("2023-10-26")),
                ],
            ),
             ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("Ana Gómez", weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text("Llamada")),
                    ft.DataCell(ft.Text("Seguimiento con cliente B.")),
                    ft.DataCell(self._build_status_badge("Pendiente", styles.STATUS_YELLOW_BG, styles.STATUS_YELLOW_TXT)),
                    ft.DataCell(ft.Text("2023-10-27")),
                    ft.DataCell(ft.Text("11:00")),
                    ft.DataCell(ft.Text("-")),
                ],
            ),
        ]

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # --- Barra Superior de Botones ---
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Registrar actividad",
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            bgcolor=styles.PRIMARY_BLUE,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            height=45,
                        ),
                        ft.OutlinedButton(
                            "Marcar como completado",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            style=ft.ButtonStyle(
                                color=styles.TEXT_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(width=1, color=ft.Colors.GREY_300)
                            ),
                            height=45,
                        ),
                        ft.OutlinedButton(
                            "Modificar",
                            icon=ft.Icons.EDIT_OUTLINED,
                             style=ft.ButtonStyle(
                                color=styles.TEXT_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(width=1, color=ft.Colors.GREY_300)
                            ),
                            height=45,
                        ),
                        ft.OutlinedButton(
                            "Eliminar actividad",
                            icon=ft.Icons.DELETE_OUTLINE,
                            style=ft.ButtonStyle(
                                color=ft.Colors.RED_500,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(width=1, color=ft.Colors.RED_200)
                            ),
                             height=45,
                        ),
                    ],
                    wrap=True,
                    spacing=15,
                ),
                
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),

                # --- Tabla ---
                ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=ft.border_radius.all(12),
                    padding=ft.padding.all(5),
                    content=ft.DataTable(
                        width=float("inf"),
                        heading_row_height=60,
                        data_row_min_height=60,
                        column_spacing=20,
                        columns=[
                            ft.DataColumn(ft.Text("USUARIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("CATEGORÍA", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("DETALLES", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("ESTADO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("FECHA INICIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("HORA INICIO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("FECHA CIERRE", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ],
                        rows=rows_data
                    )
                ),

                ft.Divider(height=50, color=ft.Colors.TRANSPARENT),

                # --- Placeholder ---
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=60, color=ft.Colors.GREY_300),
                            ft.Text("No hay actividades para mostrar.", color=ft.Colors.GREY_500, size=16)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    )
                )
            ]
        )