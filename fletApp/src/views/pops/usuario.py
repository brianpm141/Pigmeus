import flet as ft
import views.styles as styles
import controllers.departamentos_controller as dept_controller
import controllers.usuarios_controller as user_controller
from views.pops.mensaje import Aviso

class UserForm(ft.AlertDialog):
    def __init__(self, page: ft.Page, user_data=None, on_success=None):
        super().__init__()
        self.page = page
        self.user_data = user_data
        self.on_success = on_success
        
        # --- Configuración ---
        self.modal = True
        self.bgcolor = ft.Colors.WHITE
        self.surface_tint_color = ft.Colors.WHITE
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.scrollable = True
        
        # --- Título ---
        title_text = "Modificar Usuario" if user_data else "Registrar Nuevo Usuario"
        sub_title = "Edite los datos." if user_data else "Complete la información del colaborador."
        
        self.title = ft.Column(
            [
                ft.Text(title_text, size=20, weight=ft.FontWeight.BOLD, color=styles.TEXT_COLOR),
                ft.Text(sub_title, size=12, color=ft.Colors.GREY_500),
            ],
            spacing=5
        )

        # --- Campos ---
        
        # 1. Nombre
        self.name_field = ft.TextField(
            label="Nombre(s)",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error_on_type
        )

        # 2. Apellidos
        self.lastname_field = ft.TextField(
            label="Apellidos",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error_on_type
        )

        # 3. ID
        self.id_field = ft.TextField(
            label="ID de Empleado",
            width=400,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._clear_error_on_type
        )

        # 4. Departamento (Dinámico)
        # Obtenemos departamentos activos
        depts = dept_controller.get_all_departments()
        dept_options = [ft.dropdown.Option(key=d.id, text=d.nombre) for d in depts]

        self.dept_dropdown = ft.Dropdown(
            label="Departamento",
            width=400,
            options=dept_options,
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            on_change=self._clear_error_on_type
        )

        # 5. Nivel de Usuario
        self.role_dropdown = ft.Dropdown(
            label="Nivel de Usuario",
            width=400,
            options=[
                ft.dropdown.Option("Básico"),
                ft.dropdown.Option("Gerente"),
                ft.dropdown.Option("Administrador"),
            ],
            border_color=ft.Colors.GREY_300,
            text_style=ft.TextStyle(color=styles.TEXT_COLOR),
            label_style=ft.TextStyle(color=styles.TEXT_COLOR),
            value="Básico" 
        )

        # --- Pre-llenado (Si es Modificar) ---
        if user_data:
            self.name_field.value = user_data.get("nombre", "")
            self.lastname_field.value = user_data.get("apellidos", "")
            self.id_field.value = user_data.get("user", "")
            self.dept_dropdown.value = user_data.get("departamento_id")
            
            # Mapeo inverso de int a str para el rol
            role_int = user_data.get("role", 1)
            role_map_inv = {1: "Básico", 2: "Gerente", 3: "Administrador"}
            self.role_dropdown.value = role_map_inv.get(role_int, "Básico")

        # --- Contenido ---
        self.content = ft.Column(
            [
                self.name_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.lastname_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.id_field,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.dept_dropdown,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.role_dropdown,
            ],
            width=400,
            height=420,
            scroll=ft.ScrollMode.AUTO
        )

        # --- Botones ---
        self.actions = [
            ft.OutlinedButton(
                "Cancelar",
                style=ft.ButtonStyle(
                    color=styles.TEXT_COLOR,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(width=1, color=ft.Colors.GREY_300)
                ),
                height=40,
                on_click=self.close_dialog
            ),
            ft.ElevatedButton(
                "Guardar" if user_data else "Registrar",
                style=ft.ButtonStyle(
                    bgcolor=styles.PRIMARY_BLUE,
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                height=40,
                on_click=self._save
            ),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _clear_error_on_type(self, e):
        if e.control.error_text:
            e.control.error_text = None
            e.control.update()

    def _save(self, e):
        # Validaciones
        has_error = False
        
        if not self.name_field.value:
            self.name_field.error_text = "Campo obligatorio"
            has_error = True
            
        if not self.lastname_field.value:
            self.lastname_field.error_text = "Campo obligatorio"
            has_error = True
            
        if not self.id_field.value:
            self.id_field.error_text = "Campo obligatorio"
            has_error = True
            
        if not self.dept_dropdown.value:
            self.dept_dropdown.error_text = "Seleccione un departamento"
            has_error = True # Dropdown no tiene on_change para limpiar error visualmente igual, pero sirve
            self.dept_dropdown.update()

        if has_error:
            self.update()
            return

        data = {
            "nombre": self.name_field.value,
            "apellidos": self.lastname_field.value,
            "user_id": self.id_field.value,
            "dept_id": int(self.dept_dropdown.value),
            "role": self.role_dropdown.value
        }

        if self.user_data:
            # Update
            result = user_controller.update_user(self.user_data["id"], **data)
        else:
            # Create
            result = user_controller.create_user(**data)

        if result["status"] == "success":
            self.close_dialog(None)
            
            def on_aviso_close(e):
                if self.on_success:
                    self.on_success()
            
            aviso = Aviso(
                self.page, 
                message=result["message"], 
                is_error=False,
                on_dismiss=on_aviso_close
            )
            aviso.show()
        else:
            # Si es error de duplicado, lo mostramos en el campo ID
            if "ID" in result["message"] or "usuario" in result["message"]:
                 self.id_field.error_text = result["message"]
                 self.id_field.update()
            else:
                aviso = Aviso(
                    self.page, 
                    message=result["message"], 
                    is_error=True
                )
                aviso.show()

    def open_dialog(self):
        self.page.open(self)

    def close_dialog(self, e):
        self.page.close(self)