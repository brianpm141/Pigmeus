import flet as ft
import views.styles as styles
import controllers.proyectos_controller as controller
from views.pops.mensaje import Aviso
from views.pops.proyecto import ProjectForm
from views.pops.eliminar import ConfirmationDialog

class ProjectsView(ft.Container):
    def __init__(self, current_user=None):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.all(30)
        self.current_user = current_user
        
        # Inicializar componentes
        self._init_layout_components()

        self.content = ft.Column(
            controls=[
                self.header,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.toolbar,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.data_container
            ],
        )
        
        self.data_container.expand = True
        
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
        form = ProjectForm(self.page, on_success=self.refresh_data, current_user=self.current_user)
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
            form = ProjectForm(self.page, project_data=proj_data, on_success=self.refresh_data, current_user=self.current_user)
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

    def _init_layout_components(self):
        # Header
        self.header = ft.Text("Proyectos", size=24, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR)

        self.toolbar = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Crear Proyecto",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    bgcolor=styles.BTN_PRIMARY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._open_create_modal,
                    expand=1
                ),
                ft.ElevatedButton(
                    "Modificar Proyecto",
                    icon=ft.Icons.EDIT_OUTLINED,
                    bgcolor=styles.BTN_MODIFY_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._open_modify_modal,
                    expand=1
                ),
                ft.ElevatedButton(
                    "Eliminar Proyecto",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=styles.BTN_DELETE_BG,
                    color=styles.BTN_TEXT_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    on_click=self._delete_handler,
                    expand=1
                ),
                ft.Container(expand=1),
            ],
            spacing=15
        )
        
        # --- Filtro Administrativo (Solo Admins) ---
        self.dept_filter = None
        
        is_admin = False
        if self.current_user and hasattr(self.current_user, 'role'):
            role_str = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
            if "Administrador" in role_str:
                is_admin = True
        
        if is_admin:
            from controllers.departamentos_controller import get_all_departments
            depts = get_all_departments()
            
            options = [ft.dropdown.Option("all", "Todos")]
            for d in depts:
                options.append(ft.dropdown.Option(str(d.id), d.nombre))
            
            self.dept_filter = ft.Dropdown(
                width=200,
                label="Filtrar por Departamento",
                label_style=ft.TextStyle(color=styles.TEXT_COLOR, size=12),
                text_style=ft.TextStyle(color=styles.TEXT_COLOR, size=14),
                border_color=styles.PRIMARY_BLUE,
                border_radius=8,
                content_padding=10,
                focused_border_color=styles.PRIMARY_BLUE,
                value="all",
                options=options,
                on_change=lambda e: self.refresh_data()
            )
            
            self.toolbar.controls.append(self.dept_filter)
        
        self.data_container = ft.Container()

    def _build_card(self, proj):
        is_selected = (proj.id == self.selected_id)
        
        # Fecha
        last_update = proj.fecha_mov if proj.fecha_mov else proj.created_at
        last_progress_text = last_update.strftime("%d/%m/%Y") if last_update else "N/A"
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Icon Area
                    ft.Container(
                        content=ft.Icon(ft.Icons.ROCKET_LAUNCH, color=ft.Colors.GREY_600),
                        padding=15,
                        bgcolor=ft.Colors.GREY_200,
                        border_radius=10,
                    ),
                    # Info Area
                    ft.Column(
                        controls=[
                            ft.Text(proj.nombre, weight=ft.FontWeight.BOLD, size=16, color=styles.TEXT_COLOR),
                            ft.Row([
                                self._build_status_badge(proj.estado),
                                ft.Text(f"Act: {last_progress_text}", size=12, color=ft.Colors.GREY_400)
                            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(expand=True), # Spacer
                    # Actions Area
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
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(15),
            bgcolor=styles.CARD_BG,
            border_radius=12,
            shadow=styles.CARD_SHADOW if not is_selected else None,
            border=ft.border.all(2, styles.PRIMARY_BLUE) if is_selected else None,
            on_click=lambda e: self._on_card_click(proj.id),
            ink=True
        )

    def _on_card_click(self, proj_id):
        if self.selected_id == proj_id:
            self.selected_id = None
        else:
            self.selected_id = proj_id
        self.refresh_data()

    def refresh_data(self):
        dept_filter_val = self.dept_filter.value if self.dept_filter else None
        projects = controller.get_projects(self.current_user, filter_dept_id=dept_filter_val)
        
        if projects:
            cards = []
            for proj in projects:
                cards.append(self._build_card(proj))

            self.data_container.alignment = ft.alignment.top_center
            self.data_container.content = ft.ListView(
                controls=cards,
                spacing=15,
                padding=ft.padding.only(bottom=20)
            )
        else:
            self.data_container.alignment = ft.alignment.center
            self.data_container.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ROCKET_LAUNCH_OUTLINED, size=60, color=ft.Colors.GREY_300),
                    ft.Text("No hay proyectos registrados.", color=ft.Colors.GREY_500, size=16)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
        
        if self.page:
            self.update()
