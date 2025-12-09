import flet as ft
from datetime import datetime
import views.styles as styles
import controllers.proyectos_controller as controller
from controllers.usuarios_controller import get_all_users
from controllers.departamentos_controller import get_all_departments
from views.pops.mensaje import Aviso

class ProjectForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, project_data=None, on_success=None, current_user=None):
        super().__init__()
        self.page = page
        self.project_data = project_data
        self.on_success = on_success
        self.current_user = current_user
        
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        # self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # Cargar datos
        self.users = get_all_users(current_user)
        self.departments = get_all_departments() # Dept controller lacks filtering? We might need to handle this manually or just filter the list for now if needed. 
        # Actually standard users shouldn't change department of a project usually, but if creating...
        
        # --- CAMPOS ---
        
        self.txt_nombre = ft.TextField(
            label="Nombre del Proyecto",
            border_color=styles.PRIMARY_BLUE,
            color=styles.TEXT_COLOR
        )
        
        self.dd_responsable = ft.Dropdown(
            label="Responsable",
            border_color=styles.PRIMARY_BLUE,
            color=styles.TEXT_COLOR,
            options=[
                ft.dropdown.Option(u.id, f"{u.nombre} {u.apellidos}") for u in self.users
            ]
        )
        
        self.dd_departamento = ft.Dropdown(
            label="Departamento",
            border_color=styles.PRIMARY_BLUE,
            color=styles.TEXT_COLOR,
            options=[
                ft.dropdown.Option(d.id, d.nombre) for d in self.departments
            ]
        )
        
        # Simplificación: Fecha como texto por ahora, idealmente un DatePicker
        self.txt_fecha = ft.TextField(
            label="Fecha Estimada (YYYY-MM-DD)",
            border_color=styles.PRIMARY_BLUE,
            color=styles.TEXT_COLOR,
            hint_text="Ej: 2024-12-31"
        )

        
        self.title = ft.Text(
            "Modificar Proyecto" if project_data else "Nuevo Proyecto",
            weight=ft.FontWeight.BOLD,
            color=styles.TEXT_COLOR
        )
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY)),
            ft.ElevatedButton(
                "Guardar", 
                on_click=self.save_project,
                bgcolor=styles.PRIMARY_BLUE,
                color=ft.Colors.WHITE
            )
        ]
        
        self._init_fields()
        
        self.content = ft.Column(
            controls=[
                self.txt_nombre,
                self.dd_responsable,
                self.dd_departamento,
                self.txt_fecha,
            ],
            tight=True,
            width=400
        )
        
    def _init_fields(self):
        if self.project_data:
            self.txt_nombre.value = self.project_data.get("nombre", "")
            
            resp_id = self.project_data.get("responsable_id")
            if resp_id: self.dd_responsable.value = str(resp_id)
            
            dept_id = self.project_data.get("departamento_id")
            if dept_id: self.dd_departamento.value = str(dept_id)
            
            fecha = self.project_data.get("fecha_entrega")
            if fecha:
                # Asumiendo fecha es datetime
                if isinstance(fecha, str):
                     self.txt_fecha.value = fecha
                else:
                     self.txt_fecha.value = fecha.strftime("%Y-%m-%d")
        
        # Lógica de bloqueo si no es Admin
        if self.current_user:
            is_admin = False
            # Check Role
            if hasattr(self.current_user, 'role'):
                role_str = str(self.current_user.role.value) if hasattr(self.current_user.role, 'value') else str(self.current_user.role)
                if "Administrador" in role_str:
                    is_admin = True
            
            if not is_admin:
                # Pre-seleccionar y bloquear departamento
                dept_id = None
                if hasattr(self.current_user, 'departamento_id'):
                    dept_id = self.current_user.departamento_id
                elif hasattr(self.current_user, 'id') and hasattr(self.current_user, 'code'): # Is Department
                    dept_id = self.current_user.id
                
                if dept_id:
                     self.dd_departamento.value = str(dept_id)
                     self.dd_departamento.disabled = True

    def open_dialog(self):
        self.page.dialog = self
        self.open = True
        self.page.update()

    def close_dialog(self, e=None):
        self.open = False
        self.page.update()

    def save_project(self, e):
        nombre = self.txt_nombre.value
        resp_id = self.dd_responsable.value
        dept_id = self.dd_departamento.value
        fecha_str = self.txt_fecha.value
        
        if not nombre or not dept_id:
            Aviso(self.page, "Nombre y Departamento son obligatorios", is_error=True).show()
            return

        # Parsear fecha
        fecha_est = None
        if fecha_str:
            try:
                fecha_est = datetime.strptime(fecha_str, "%Y-%m-%d")
            except ValueError:
                Aviso(self.page, "Formato de fecha inválido (YYYY-MM-DD)", is_error=True).show()
                return

        if self.project_data:
            # Update
            res = controller.update_project(
                proj_id=self.project_data["id"],
                nombre=nombre,
                responsable_id=resp_id,
                departamento_id=dept_id,
                fecha_est=fecha_est
            )
        else:
            # Create
            res = controller.create_project(
                nombre=nombre,
                responsable_id=resp_id,
                departamento_id=dept_id,
                fecha_est=fecha_est
            )
            
        if res["status"] == "success":
            self.close_dialog()
            if self.on_success:
                self.on_success()
            Aviso(self.page, res["message"]).show()
        else:
            Aviso(self.page, res["message"], is_error=True).show()
