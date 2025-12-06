import flet as ft
import views.styles as styles
import controllers.proyectos_controller as controller
from views.pops.mensaje import Aviso
from views.pops.proyecto import ProjectForm
from views.pops.eliminar import ConfirmationDialog

class ProjectsView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            controls=self._build_layout(),
        )
        
        self.selected_id = None
        self.refresh_data()

    def _handle_select(self, e):
        is_selected = e.data == "true"
        proj_id = e.control.data 
        
        if is_selected:
            self.selected_id = proj_id
        else:
            if self.selected_id == proj_id:
                self.selected_id = None
        
        self.refresh_data()

    def _open_create_modal(self, e):
        form = ProjectForm(self.page, on_success=self.refresh_data)
        form.open_dialog()

    def _open_modify_modal(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona un proyecto para modificar", is_error=True).show()
            return
        
        projects = controller.get_projects()
        selected_proj = next((p for p in projects if p.id == self.selected_id), None)
        
        if selected_proj:
            proj_data = {
                "id": selected_proj.id,
                "nombre": selected_proj.nombre,
                "fecha_entrega": selected_proj.fecha_est,
                "responsable_id": selected_proj.responsable_id,
                "departamento_id": selected_proj.departamento_id,
            }
            form = ProjectForm(self.page, project_data=proj_data, on_success=self.refresh_data)
            form.open_dialog()

    def _delete_handler(self, e):
        if not self.selected_id:
            Aviso(self.page, "Selecciona un proyecto para eliminar", is_error=True).show()
            return
        
        dialog = ConfirmationDialog(
            self.page,
            title="Eliminar Proyecto",
            content_text="¿Estás seguro de que deseas eliminar este proyecto?",
            on_confirm=self._execute_delete
        )
        dialog.show()

    def _execute_delete(self):
        res = controller.delete_project(self.selected_id)
        if res["status"] == "success":
            self.selected_id = None
            self.refresh_data()
            Aviso(self.page, res["message"]).show()
        else:
            Aviso(self.page, res["message"], is_error=True).show()

    def _open_activities(self, e):
        # Placeholder for navigating to activities of a project
        Aviso(self.page, f"Ver actividades del proyecto {e.control.data}").show()

    def _build_status_badge(self, status_int):
        if status_int == 2: # Completado
            text = "Completado"
            bg = styles.STATUS_GREEN_BG
            txt = styles.STATUS_GREEN_TXT
        elif status_int == 1: # En Proceso
            text = "En Proceso"
            bg = "#DBEAFE" # Blue 100
            txt = "#1E40AF" # Blue 800
        else: # Pendiente
            text = "Pendiente"
            bg = styles.STATUS_YELLOW_BG
            txt = styles.STATUS_YELLOW_TXT

        return ft.Container(
            content=ft.Text(text, color=txt, size=12, weight=ft.FontWeight.W_500),
            bgcolor=bg,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=ft.border_radius.all(15),
            alignment=ft.alignment.center
        )

    def _build_layout(self):
        self.toolbar = ft.Row(
            wrap=True,
            spacing=15,
            controls=[
                ft.ElevatedButton(
                    "Crear Proyecto",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._open_create_modal
                ),
                ft.ElevatedButton(
                    "Modificar Proyecto",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._open_modify_modal
                ),
                ft.ElevatedButton(
                    "Eliminar Proyecto",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=styles.BTN_DELETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    height=45,
                    on_click=self._delete_handler
                )
            ]
        )
        
        self.data_container = ft.Container()

        return [
            self.toolbar,
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            self.data_container
        ]

    def refresh_data(self):
        projects = controller.get_projects()
        
        if projects:
            rows = []
            for proj in projects:
                is_selected = (proj.id == self.selected_id)
                
                # Logic for Last Progress / Completion Date
                # Use fecha_mov if available, else created_at
                last_update = proj.fecha_mov if proj.fecha_mov else proj.created_at
                last_progress_text = last_update.strftime("%Y-%m-%d") if last_update else "Sin fecha"

                rows.append(
                    ft.DataRow(
                        selected=is_selected,
                        on_select_changed=self._handle_select,
                        data=proj.id,
                        cells=[
                            ft.DataCell(ft.Text(proj.nombre, weight=ft.FontWeight.W_500)),
                            ft.DataCell(self._build_status_badge(proj.estado)),
                            ft.DataCell(ft.Text(last_progress_text)),
                            ft.DataCell(
                                ft.ElevatedButton(
                                    "Actividades",
                                    icon=ft.Icons.LIST_ALT,
                                    bgcolor=styles.PRIMARY_BLUE, 
                                    color=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    height=35,
                                    data=proj.id,
                                    on_click=self._open_activities
                                )
                            ),
                        ],
                    )
                )

            self.data_container.content = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                padding=ft.padding.all(5),
                content=ft.DataTable(
                    width=float("inf"),
                    heading_row_height=60,
                    data_row_min_height=60,
                    column_spacing=20,
                    show_checkbox_column=False,
                    columns=[
                        ft.DataColumn(ft.Text("PROYECTO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("ESTADO", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("ÚLTIMA ACTUALIZACIÓN", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("ACCIONES", color=ft.Colors.GREY_500, size=12, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows
                )
            )
        else:
            self.data_container.content = ft.Container(
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.ROCKET_LAUNCH_OUTLINED, size=60, color=ft.Colors.GREY_300),
                        ft.Text("No hay proyectos registrados.", color=ft.Colors.GREY_500, size=16)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        
        if self.page:
            self.update()
